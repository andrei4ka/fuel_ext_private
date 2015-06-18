#    Copyright 2013 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import functools
import json
import logging

from fuel_ext.http import HTTPClient
from fuel_ext import default_settings


LOG = logging.getLogger(__name__)


def json_parse(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        response = func(*args, **kwargs)
        return json.loads(response.read())
    return wrapped


class NailgunClient(object):
    """NailgunClient"""  # TODO documentation

    def __init__(self, master_ip, username, password, tenant_name):
        url = "http://{0}:8000".format(master_ip)
        LOG.info('Initiate Nailgun client with url %s', url)
        self.keystone_url = "http://{0}:5000/v2.0".format(master_ip)
        self._client = HTTPClient(url=url, keystone_url=self.keystone_url,
                                  credentials={'username': username,
                                               'password': password,
                                               'tenant_name': tenant_name})
        super(NailgunClient, self).__init__()

    @property
    def client(self):
        return self._client

    def get_root(self):
        return self.client.get("/")

    @json_parse
    def list_nodes(self):
        return self.client.get("/api/nodes/")

    @json_parse
    def list_cluster_nodes(self, cluster_id):
        return self.client.get("/api/nodes/?cluster_id={}".format(cluster_id))

    @json_parse
    def get_networks(self, cluster_id):
        net_provider = self.get_cluster(cluster_id)['net_provider']
        return self.client.get(
            "/api/clusters/{}/network_configuration/{}".format(
                cluster_id, net_provider
            )
        )

    @json_parse
    def update_networks(self, cluster_id, data):
        net_provider = self.get_cluster(cluster_id)['net_provider']
        return self.client.put(
            "/api/clusters/{}/network_configuration/{}".format(
                cluster_id, net_provider
            ),
            data=data
        )

    @json_parse
    def verify_networks(self, cluster_id):
        net_provider = self.get_cluster(cluster_id)['net_provider']
        return self.client.put(
            "/api/clusters/{}/network_configuration/{}/verify/".format(
                cluster_id, net_provider
            ),
            data=self.get_networks(cluster_id)
        )

    @json_parse
    def get_cluster_attributes(self, cluster_id):
        return self.client.get(
            "/api/clusters/{}/attributes/".format(cluster_id)
        )

    @json_parse
    def get_cluster_vmware_attributes(self, cluster_id):
        return self.client.get(
            "/api/clusters/{}/vmware_attributes/".format(cluster_id)
        )

    @json_parse
    def update_cluster_attributes(self, cluster_id, attrs):
        return self.client.put(
            "/api/clusters/{}/attributes/".format(cluster_id),
            attrs
        )

    @json_parse
    def update_cluster_vmware_attributes(self, cluster_id, attrs):
        return self.client.put(
            "/api/clusters/{}/vmware_attributes/".format(cluster_id),
            attrs
        )

    @json_parse
    def get_cluster(self, cluster_id):
        return self.client.get(
            "/api/clusters/{}".format(cluster_id)
        )

    @json_parse
    def get_nodes(self):
        return self.client.get(
            "/api/nodes/")

    @json_parse
    def get_node(self, node_id):
        return self.client.get(
            "/api/nodes/{}".format(node_id)
        )

    @json_parse
    def update_cluster(self, cluster_id, data):
        return self.client.put(
            "/api/clusters/{}/".format(cluster_id),
            data
        )

    @json_parse
    def delete_cluster(self, cluster_id):
        return self.client.delete(
            "/api/clusters/{}/".format(cluster_id)
        )

    @json_parse
    def update_node(self, node_id, data):
        return self.client.put(
            "/api/nodes/{}/".format(node_id), data
        )

    @json_parse
    def update_nodes(self, data):
        return self.client.put(
            "/api/nodes", data
        )

    def add_nodes(self, cluster_id, data):
        return self.client.post(
            "/api/v1/clusters/{}/assignment".format(cluster_id),
            data
        )

    @json_parse
    def deploy_cluster_changes(self, cluster_id):
        return self.client.put(
            "/api/clusters/{}/changes/".format(cluster_id)
        )

    @json_parse
    def get_task(self, task_id):
        return self.client.get("/api/tasks/{}".format(task_id))

    @json_parse
    def get_tasks(self):
        return self.client.get("/api/tasks")

    @json_parse
    def get_releases(self):
        return self.client.get("/api/releases/")

    @json_parse
    def get_release(self, release_id):
        return self.client.get("/api/releases/{}".format(release_id))

    @json_parse
    def put_release(self, release_id, data):
        return self.client.put("/api/releases/{}".format(release_id), data)

    @json_parse
    def get_releases_details(self, release_id):
        return self.client.get("/api/releases/{}".format(release_id))

    @json_parse
    def get_node_disks(self, node_id):
        return self.client.get("/api/nodes/{}/disks".format(node_id))

    @json_parse
    def put_node_disks(self, node_id, data):
        return self.client.put("/api/nodes/{}/disks".format(node_id), data)

    def get_release_id(self, release_name=default_settings.OPENSTACK_RELEASE):
        for release in self.get_releases():
            if release["name"].lower().find(release_name.lower()) != -1:
                return release["id"]

    @json_parse
    def get_node_interfaces(self, node_id):
        return self.client.get("/api/nodes/{}/interfaces".format(node_id))

    @json_parse
    def put_node_interfaces(self, node_id, data):
        return self.client.put("/api/nodes/{}/interfaces".format(node_id),
                               data)

    @json_parse
    def list_clusters(self):
        return self.client.get("/api/clusters/")

    @json_parse
    def create_cluster(self, data):
        LOG.info('Before post to nailgun')
        return self.client.post(
            "/api/clusters",
            data=data)

    @json_parse
    def get_ostf_test_sets(self, cluster_id):
        return self.client.get("/ostf/testsets/{}".format(cluster_id))

    @json_parse
    def get_ostf_tests(self, cluster_id):
        return self.client.get("/ostf/tests/{}".format(cluster_id))

    @json_parse
    def get_ostf_test_run(self, cluster_id):
        return self.client.get("/ostf/testruns/last/{}".format(cluster_id))

    @json_parse
    def ostf_run_tests(self, cluster_id, test_sets_list):
        LOG.info('Run OSTF tests at cluster #%s: %s',
                 cluster_id, test_sets_list)
        data = []
        for test_set in test_sets_list:
            data.append(
                {
                    'metadata': {'cluster_id': str(cluster_id), 'config': {}},
                    'testset': test_set
                }
            )
        # get tests otherwise 500 error will be thrown
        self.get_ostf_tests(cluster_id)
        return self.client.post("/ostf/testruns", data)

    @json_parse
    def ostf_run_singe_test(self, cluster_id, test_sets_list, test_name):
        # get tests otherwise 500 error will be thrown
        self.get_ostf_tests(cluster_id)
        LOG.info('Get tests finish with success')
        data = []
        for test_set in test_sets_list:
            data.append(
                {
                    'metadata': {'cluster_id': str(cluster_id), 'config': {}},
                    'tests': [test_name],
                    'testset': test_set
                }
            )
        return self.client.post("/ostf/testruns", data)

    @json_parse
    def update_network(self, cluster_id, networking_parameters=None,
                       networks=None):
        nc = self.get_networks(cluster_id)
        if networking_parameters is not None:
            for k in networking_parameters:
                nc["networking_parameters"][k] = networking_parameters[k]
        if networks is not None:
            nc["networks"] = networks

        net_provider = self.get_cluster(cluster_id)['net_provider']
        return self.client.put(
            "/api/clusters/{}/network_configuration/{}".format(
                cluster_id, net_provider
            ),
            nc
        )

    def get_cluster_id(self, name):
        for cluster in self.list_clusters():
            if cluster["name"] == name:
                LOG.info('cluster name is %s' % name)
                LOG.info('cluster id is %s' % cluster["id"])
                return cluster["id"]

    def add_syslog_server(self, cluster_id, host, port):
        # Here we updating cluster editable attributes
        # In particular we set extra syslog server
        attributes = self.get_cluster_attributes(cluster_id)
        attributes["editable"]["syslog"]["syslog_server"]["value"] = host
        attributes["editable"]["syslog"]["syslog_port"]["value"] = port
        self.update_cluster_attributes(cluster_id, attributes)

    def get_cluster_vlans(self, cluster_id):
        cluster_vlans = []
        nc = self.get_networks(cluster_id)['networking_parameters']
        vlan_start = nc["fixed_networks_vlan_start"]
        network_amound = int(nc["fixed_networks_amount"] - 1)
        cluster_vlans.extend([vlan_start, vlan_start + network_amound])

        return cluster_vlans

    @json_parse
    def get_notifications(self):
        return self.client.get("/api/notifications")

    @json_parse
    def update_redhat_setup(self, data):
        return self.client.post("/api/redhat/setup", data=data)

    @json_parse
    def generate_logs(self):
        return self.client.put("/api/logs/package")

    def provision_nodes(self, cluster_id):
        return self.do_cluster_action(cluster_id)

    def deploy_nodes(self, cluster_id):
        return self.do_cluster_action(cluster_id, "deploy")

    def stop_deployment(self, cluster_id):
        return self.do_stop_reset_actions(cluster_id)

    def reset_environment(self, cluster_id):
        return self.do_stop_reset_actions(cluster_id, action="reset")

    @json_parse
    def do_cluster_action(self, cluster_id, action="provision"):
        nailgun_nodes = self.list_cluster_nodes(cluster_id)
        cluster_node_ids = map(lambda _node: str(_node['id']), nailgun_nodes)
        return self.client.put(
            "/api/clusters/{0}/{1}?nodes={2}".format(
                cluster_id,
                action,
                ','.join(cluster_node_ids))
        )

    @json_parse
    def do_stop_reset_actions(self, cluster_id, action="stop_deployment"):
        return self.client.put(
            "/api/clusters/{0}/{1}/".format(str(cluster_id), action))

    @json_parse
    def get_api_version(self):
        return self.client.get("/api/version")

    @json_parse
    def run_update(self, cluster_id):
        return self.client.put(
            "/api/clusters/{0}/update/".format(str(cluster_id)))

    @json_parse
    def create_nodegroup(self, cluster_id, group_name):
        data = {"cluster_id": cluster_id, "name": group_name}
        return self.client.post("/api/nodegroups/", data=data)

    @json_parse
    def get_nodegroups(self):
        return self.client.get("/api/nodegroups/")

    @json_parse
    def assign_nodegroup(self, group_id, nodes):
        return self.client.post("/api/nodegroups/{0}/".format(group_id),
                                data=nodes)

    @json_parse
    def update_settings(self, data=None):
        return self.client.put("/api/settings", data=data)

    def send_fuel_stats(self, enabled=False, user_email="test@localhost"):
        settings = self.update_settings()
        params = ('send_anonymous_statistic', 'send_user_info',
                  'user_choice_saved')
        for p in params:
            settings['settings']['statistics'][p]['value'] = enabled
        if user_email:
            settings['settings']['statistics']['email']['value'] = user_email
        self.update_settings(data=settings)

    @json_parse
    def get_cluster_deployment_tasks(self, cluster_id):
        """ Get list of all deployment tasks for cluster."""
        return self.client.get(
            '/api/clusters/{}/deployment_tasks'.format(cluster_id))

    @json_parse
    def get_release_deployment_tasks(self, release_id):
        """ Get list of all deployment tasks for release."""
        return self.client.get(
            '/api/releases/{}/deployment_tasks'.format(release_id))

    @json_parse
    def get_end_deployment_tasks(self, cluster_id, end, start=None):
        """ Get list of all deployment tasks for cluster with end parameter.
        If  end=netconfig, return all tasks from the graph included netconfig
        """
        if not start:
            return self.client.get(
                '/api/clusters/{0}/deployment_tasks?end={1}'.format(
                    cluster_id, end))
        return self.client.get(
            '/api/clusters/{0}/deployment_tasks?start={1}&end={2}'.format(
                cluster_id, start, end))

    @json_parse
    def get_orchestrator_deployment_info(self, cluster_id):
        return self.client.get(
            '/api/clusters/{}/orchestrator/deployment'.format(cluster_id))

    @json_parse
    def put_deployment_tasks_for_cluster(self, cluster_id, data, node_id):
        """ Put  task to be executed on the nodes from cluster.:
        Params:
        cluster_id : Cluster id,
        node_id: Node ids where task should be run, can be node_id=1,
        or node_id =1,2,3,
        data: tasks ids"""
        return self.client.put(
            '/api/clusters/{0}/deploy_tasks?nodes={1}'.format(
                cluster_id, node_id), data)

    @json_parse
    def put_deployment_tasks_for_release(self, release_id, data):
        return self.client.put(
            '/api/releases/{}/deployment_tasks'.format(release_id), data)
