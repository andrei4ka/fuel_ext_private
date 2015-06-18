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

# CONSTANTS
OPENSTACK_RELEASE = 'ubuntu'

# Default settings
DEFAULT = {
    'networks': {
        'default': None,
        'mandatory': True},
    'nodes': {
        'default': None,
        'mandatory': True},
    'env_name': {
        'default': None,
        'mandatory': True},
    'master_ip': {
        'default': None,
        'mandatory': True},
    'username': {
        'default': 'admin',
        'mandatory': True},
    'password': {
        'default': 'admin',
        'mandatory': True},
    'tenant_name': {
        'default': 'admin',
        'mandatory': True},
    'repos': {
        'default': [
            {u'name': u'ubuntu-0',
             u'priority': 10,
             u'section': u'main universe multiverse',
             u'suite': u'trusty',
             u'type': u'deb',
             u'uri': u'http://mirrors.mtn5.cci.att.com/mirrors/ubuntu/'},
            {u'name': u'ubuntu-1',
             u'priority': 10,
             u'section': u'main universe multiverse',
             u'suite': u'trusty-updates',
             u'type': u'deb',
             u'uri': u'http://mirrors.mtn5.cci.att.com/mirrors/ubuntu/'},
            {u'name': u'ubuntu-2',
             u'priority': 10,
             u'section': u'main universe multiverse',
             u'suite': u'trusty-security',
             u'type': u'deb',
             u'uri': u'http://mirrors.mtn5.cci.att.com/mirrors/ubuntu/'},
            {u'name': u'mos',
             u'priority': 11,
             u'section': u'main restricted',
             u'suite': u'mos6.1',
             u'type': u'deb',
             u'uri': u'http://10.109.25.2:8080//2014.2.2-6.1/ubuntu/x86_64'},
            {u'name': u'mos-updates',
             u'priority': 11,
             u'section': u'main restricted',
             u'suite': u'mos6.1-updates',
             u'type': u'deb',
             u'uri': u'http://mirrors.mtn5.cci.att.com/mirrors/'
                     'mirror.fuel-infra.org/mos/ubuntu'},
            {u'name': u'mos-security',
             u'priority': 11,
             u'section': u'main restricted',
             u'suite': u'mos6.1-security',
             u'type': u'deb',
             u'uri': u'http://mirrors.mtn5.cci.att.com/mirrors/'
                     'mirror.fuel-infra.org/mos/ubuntu'},
            {u'name': u'mos-holdback',
             u'priority': 13,
             u'section': u'main restricted',
             u'suite': u'mos6.1-holdback',
             u'type': u'deb',
             u'uri': u'http://mirrors.mtn5.cci.att.com/mirrors/'
                     'mirror.fuel-infra.org/mos/ubuntu'},
            {u'name': u'Auxiliary',
             u'priority': 12,
             u'section': u'main restricted',
             u'suite': u'auxiliary',
             u'type': u'deb',
             u'uri': u'http://10.109.25.2:8080//2014.2.2-6.1/ubuntu/'
                     'auxiliary'},
            {u'name': u'AIC',
             u'priority': 13,
             u'section': u'main',
             u'suite': u'mos6.1',
             u'type': u'deb',
             u'uri': u'http://mirrors.mtn5.cci.att.com/aic-mos/mos-6.1-dev/'}],
        'mandatory': True},
}
