#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)

import re
import os
import novaclient.client as nova_client
from novaclient.v2.servers import ServerManager
import glanceclient.client as glance_client
from glanceclient.exc import HTTPNotFound
from keystoneauth1 import identity
from keystoneauth1 import session
from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type

DOCUMENTATION = r'''
---
module: set_instances_os_properties
short_description: Set properties os_type, os_family, os_version for all running Auckland servers
version_added: "1.0.0"
description: Set properties os_type, os_family, os_version for all running Auckland servers

options:
    n/a
        
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - openstack.set_instances_os_properties

author:
    - Martin Feller (@mondkaefer)
'''

EXAMPLES = r'''
# Pass in a message
- name: Set OS properties for all active servers in Auckland 
  openstack.set_instances_os_properties

'''

RETURN = r'''
servers_without_os_information:
    description: Openstack server IDs where we did not find any OS information
    type: list
    returned: always


'''

cer_windows_images_ids = [
    'c8c88133-096f-4a71-84ba-a0bdf4aa5425', # UoA-Server2012-1.6OLD
    'c84058cb-b7d6-4317-a6cd-d9d79378ad74', # UoA-Server2012-1.7
    'db3f90df-9bc7-4a03-a42e-596428e029f2', # UoA-Server2012-1.8
    '4a923018-c83b-453f-8ce3-5e523548c222', # UoA-Server2012-1.9
    'fa1206b3-b646-40d7-a909-eda87a9006c9', # UoA-Server2012-2.0
    'b610209e-1de2-495c-bf6d-5ece685f43b9', # UoA-Server2012-Base-1.1OLD
    '2324c9ef-e2ad-41d7-ae11-67c58497f216', # UoA-Server2012-Base-1.2
    'c9e99b4f-6a3e-4552-b046-298ac8553dc8', # UoA-Server2012-Base-1.2
    '9ab7a8b0-2116-45bf-99a6-12d365dff9c1', # UoA-Server2012-Base-1.3
    '44468951-3a28-46f4-873f-0c13b4f69fe6', # UoA-Server2012-Base-1.31
    'bf4c5248-c5bc-4586-b8d3-46ab8062e69c', # UoA-Server2012-Base-1.4OLD
    '9c4f45f6-3600-420e-801a-ec45af393b12', # UoA-Server2012-Base-1.5OLD
    'edb7e3b0-428b-4369-ae2b-c1c08c6a4b58', # UoA-Server2012-MATLAB-1.0
    '2fd3ea26-1f9a-4a7c-811f-84c0407c14f5', # UoA-Server2012-MATLAB-1.4
    'ee745507-bb0b-472b-95fa-4eeef9305c72' # UoA-Server2012-mfel395_test
]


def get_os_information_from_console_log(server):
    console_log = server.get_console_output()
    os_t = None
    os_f = None
    os_v = None
    if len(console_log) > 0:
        for line in console_log.splitlines():
            if 'Welcome' in line:  # Rocky, Fedora, CentOS, Ubuntu
                if 'Ubuntu' in line:
                    os_t = 'linux'
                    os_f = 'ubuntu'
                    if 'LTS' in line:
                        tmp: str = re.search('.*Ubuntu (\\d+\\.\\d+.*LTS).*', line).group(1)
                        os_v = tmp.replace(' LTS', '')
                    else:
                        os_v = re.search('.*Ubuntu (\\d+\\.\\d+\\.*\\d*).*', line).group(1)
                elif 'CentOS' in line:
                    os_t = 'linux'
                    os_f = 'centos'
                    os_v = re.search('.*CentOS [a-zA-Z]+ (\\d+).*', line).group(1)
                elif 'Rocky' in line:
                    os_t = 'linux'
                    os_f = 'rocky'
                    os_v = re.search('.*Rocky [a-zA-Z]+ (\\d+\\.*\\d*).*', line).group(1)
                elif 'Fedora in line':
                    os_t = 'linux'
                    os_f = 'fedora'
                    os_v = re.search('.*Fedora.* (\\d+).*', line).group(1)
                break
            elif 'Debian' in line:
                os_t = 'linux'
                os_f = 'debian'
                os_v = re.search('.*Debian.* (\\d+).*', line).group(1)
                break

    if os_t is None:
        return None
    else:
        return {'os_type': os_t, 'os_family': os_f, 'os_version': os_v}


def get_instance_os_from_image(glance_c, image_id):
    if image_id in cer_windows_images_ids:
        return {'os_type': 'windows', 'os_family': 'server', 'os_version': '2012 r2'}

    try:
        img_det = glance_c.images.get(image_id)
        if 'nectar_name' in img_det:
            if 'os_distro' in img_det:
                return {'os_type': 'linux', 'os_family': img_det['os_distro'], 'os_version': img_det['os_version']}
            elif '.facts/os_distro' in img_det: # Trove images
                return {'os_type': 'linux', 'os_family': img_det['.facts/os_distro'], 'os_version': img_det['.facts/os_version']}
        elif 'base_image_ref' in img_det:
            if img_det['base_image_ref'] in cer_windows_images_ids:
                return {'os_type': 'windows', 'os_family': 'server', 'os_version': '2012 r2'}
            else:
                return get_instance_os_from_image(img_det['base_image_ref'])
        elif 'os_distro' in img_det and img_det['os_distro'] == 'fedora-coreos':
            return {'os_type': 'linux', 'os_family': 'fedora coreos', 'os_version': img_det['name']}
    except HTTPNotFound:
        print("glance exception: image not found")

    return None


def run_module():
    module_args = dict(
    )

    result = dict(
        changed=False,
        servers_without_os_information=[]
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(**result)

    # Verify required environment variables are defined
    for x in ['OS_AUTH_URL', 'OS_APPLICATION_CREDENTIAL_ID', 'OS_APPLICATION_CREDENTIAL_SECRET']:
        if x not in os.environ:
            module.fail_json(msg='%s is not set as environment variable' % x, **result)

    os_compute_api_version: float = 2.83
    result['changed'] = False

    auth = identity.v3.application_credential.ApplicationCredential(
        auth_url=os.environ['OS_AUTH_URL'],
        application_credential_id=os.environ['OS_APPLICATION_CREDENTIAL_ID'],
        application_credential_secret=os.environ['OS_APPLICATION_CREDENTIAL_SECRET'])
    sess = session.Session(auth=auth)
    nova_c = nova_client.Client(2.83, session=sess)
    glance_c = glance_client.Client(2, session=sess)

    search_opts = {'status': 'ACTIVE', 'availability_zone': 'auckland', 'all_tenants': True}
    for s in nova_c.servers.list(search_opts=search_opts):
        server_dict = s.to_dict()
        existing_md = server_dict['metadata']
        existing_os_info = {
            'os_type': existing_md['os_type'] if 'os_type' in existing_md else None,
            'os_family': existing_md['os_family'] if 'os_family' in existing_md else None,
            'os_version': existing_md['os_version'] if 'os_version' in existing_md else None
        }

        os_info = get_os_information_from_console_log(s)
        if os_info is None:
            os_info = get_instance_os_from_image(glance_c, server_dict["image"]["id"])

        if os_info is None and existing_os_info['os_type'] is None:
            result['servers_without_os_information'].append(server_dict["id"])
        else:
            if existing_os_info['os_type'] is None or existing_os_info['os_type'] != os_info['os_type'] or \
                    existing_os_info['os_family'] is None or existing_os_info['os_family'] != os_info['os_family'] or \
                    existing_os_info['os_version'] is None or existing_os_info['os_version'] != os_info['os_version']:
                print(f'Setting metadata {os_info} for {server_dict["id"]}')
                sm = ServerManager(nova_c)
                sm.set_meta(s, os_info)
                result['changed'] = True

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
