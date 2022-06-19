#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)

import re
from ansible.module_utils.basic import AnsibleModule
from ceradmin_common.api.openstack_util import AppCredOpenstackUtil
from ceradmin_common.api.openstack_util import UoANectarIPRegex

__metaclass__ = type

DOCUMENTATION = r'''
---
module: get_instance_details
short_description: Return the first public IP and the project id
version_added: "1.0.0"
description: Return the first public IP and the project id

options:
    instance_id:
        description: ID of the Nectar instance
        required: true
        type: str
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - openstack.get_instance_details

author:
    - Martin Feller (@mondkaefer)
'''

EXAMPLES = r'''
# Pass in a message
- name: Test with a message
  openstack.get_instance_details:
    instance_id: 5dd81950-5a21-4095-830a-150d68499095

'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
public_ip:
    description: First public IP found for the given instance
    type: str
    returned: always
    sample: '136.216.216.17'
project_id:
    description: Project ID of given instance
    type: str
    returned: always
    sample: 'bb7ded84e4b64ed5ab2816443600e0e8'
'''


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        instance_id=dict(type='str', required=True)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        public_ip='',
        project_id=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    conf = AppCredOpenstackUtil.get_creds_from_environment()
    ou = AppCredOpenstackUtil(app_cred_id=conf['application_credential_id'],
                              app_cred_secret=conf['application_credential_secret'],
                              auth_url=conf['auth_url'])
    server_dict = ou.get_server(module.params['instance_id'])
    result['project_id'] = server_dict['tenant_id']
    ips = AppCredOpenstackUtil.get_ipv4s_of_server(server_dict)
    for ip in ips:
        if re.match(UoANectarIPRegex.PUBLIC_EXTERNAL, ip):
            result['public_ip'] = ip
            break
    result['changed'] = False

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
