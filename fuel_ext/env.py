#    Copyright 2015 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the 'License'); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an 'AS IS' BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import json
import logging
import logging.handlers
import os
import os.path
import sys
import urllib2

from fuel_ext import default_settings
from fuel_ext import nailgun_client


LOG = logging.getLogger(__name__)
_LOG_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_FILE = '/var/log/fuel_ext.log'


if not os.path.exists(LOG_FILE):
    open(LOG_FILE, 'a').close()


def exit(message):
    LOG(message)
    sys.exit(message)


def parse_settings(settings):
    res = {}
    for k, v in default_settings.DEFAULT.iteritems():
        if k in settings:
            res[k] = settings[k]
            continue
        if v['mandatory'] and v['default'] is None:
            message = 'Key `%s` is mandatory' % k
            exit(message)
        res[k] = v['default']
    return res


def log_setup(log_file=None):
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s (%(module)s) %(message)s',
        _LOG_TIME_FORMAT)
    log = logging.getLogger(None)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    log.addHandler(stream_handler)

    if log_file:
        file_handler = logging.handlers.WatchedFileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        mode = int('0644', 8)
        os.chmod(log_file, mode)
        file_handler.setFormatter(formatter)
        log.addHandler(file_handler)

    log.setLevel(logging.INFO)


def update_interfaces(old_ifaces, new_ifaces, networks):
    supported = ['private', 'public', 'storage', 'management']
    updated = []
    for v in new_ifaces.values():
        updated.extend(v)
    diff = set(supported) - set(updated)
    if diff:
        message = "Networks %s should be assigned." % diff
        exit(message)
    nets = dict((n['name'],
                 {"id": n['id'],
                  "name": n['name']}) for n in networks['networks'])
    for net in old_ifaces:
        if net['name'] not in new_ifaces.keys():
            continue
        assigned_networks = [nets[p] for p in new_ifaces[net['name']]]
        if net['name'] == 'eth0':
            assigned_networks.append(nets['fuelweb_admin'])
        net['assigned_networks'] = assigned_networks


def update_disks(disks, settings_disks, mac):
        node_disks = dict((v['name'], v) for v in disks[mac])
        changed = set(node_disks.keys()) & set(settings_disks.keys())
        for disk_name in changed:
            node_disks[disk_name]['volumes'] = [
                {"name": k, "size": v}
                for k, v in settings_disks[disk_name].iteritems()]
        return node_disks.values()


def main():
    log_setup(log_file=LOG_FILE)
    LOG.info('Start service.')
    argv = sys.argv
    if len(argv) < 2:
        message = 'You should use fuel-env PATH_TO_YOUR_SETTINGS_JSON'
        exit(message)
    json_settings_file = argv[1]
    with open(json_settings_file, 'r') as f:
        json_settings = f.read()
    try:
        settings = json.loads(json_settings)
    except Exception as e:
        exit(e.message)
    settings = parse_settings(settings)
    LOG.info('Used settings: %s' % settings)
    client = nailgun_client.NailgunClient(settings['master_ip'],
                                          settings['username'],
                                          settings['password'],
                                          settings['tenant_name'])

    data = {
        'name': settings['env_name'],
        'release_id': 2,
        'net_provider': 'neutron',
        'net_segment_type': 'vlan'}

    try:
        cluster_id = client.create_cluster(data)['id']
    except urllib2.HTTPError as e:
        message = json.loads(e.read())['message']
        exit(message)

    # Update cluster settings:
    # - enable gamma-lcp-ui plugin,
    # - enable KVM hypervisor,
    # - enable assignment public network to all nodes,
    # - update repos.
    cluster_settings = client.get_cluster_attributes(cluster_id)
    cluster_settings[
        'editable']['gamma-lcp-ui']['metadata']['enabled'] = True
    cluster_settings['editable']['common']['libvirt_type']['value'] = 'kvm'
    cluster_settings[
        'editable']['public_network_assignment'][
        'assign_to_all_nodes']['value'] = True
    cluster_settings[
        'editable']['repo_setup']['repos']['value'] = settings['repos']
    client.update_cluster_attributes(cluster_id, cluster_settings)

    # Update networking Public section.
    networks = client.get_networks(cluster_id)
    all_networks = dict((n['name'], n) for n in networks['networks'])
    all_networks['public'].update(settings['networks']['public_network'])
    networks['networks'] = all_networks.values()
    networks[
        'networking_parameters'][
        'floating_ranges'] = settings['networks']['floating_ranges']
    client.update_networks(cluster_id, networks)

    # Update nodes info.
    nodes = client.get_nodes()
    nodes = dict((n['mac'], n) for n in nodes)
    disks = dict(
        (k, client.get_node_disks(v['id'])) for k, v in nodes.iteritems())

    nodes_roles = []
    interfaces = {}
    updated_disks = {}
    # Prepare data for roles, interfaces and volumes.
    for node in settings['nodes']:
        mac = node['mac']
        settings_interfaces = node.get('interfaces')
        settings_disks = node.get('disks', None)
        node_id = nodes[mac]['id']

        if mac not in nodes:
            message = "Node witn MAC %s is not available" % node['mac']
            exit(message)
        # Set roles.
        nodes_roles.append({
            'id': node_id,
            'roles': node['roles'],
        })
        # Set interfaces.
        if settings_interfaces is not None:
            ifaces = client.get_node_interfaces(node_id)
            update_interfaces(ifaces,
                              settings_interfaces,
                              networks)
            interfaces[node_id] = ifaces

        # Set disks.
        if settings_disks is not None:
            updated_disks[node_id] = update_disks(disks, settings_disks, mac)

    # Add nodes roles.
    client.add_nodes(cluster_id, nodes_roles)
    # Update nodes volumes.
    for node_id, disks in updated_disks.iteritems():
        client.put_node_disks(node_id, disks)

    nodes = client.get_nodes()
    nodes = dict((n['mac'], n) for n in nodes)
    for node in settings['nodes']:
        mac = node['mac']
        if 'name' in node:
            nodes[mac]['name'] = node['name']
    client.update_nodes(nodes.values())

    # Update nodes interfaces
    for node_id, ifaces in interfaces.iteritems():
        client.put_node_interfaces(node_id, ifaces)

    # Deploy changes.
    client.deploy_cluster_changes(cluster_id)
