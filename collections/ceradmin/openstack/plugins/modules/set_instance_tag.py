#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)

import os
import novaclient.client as nova_client
from keystoneauth1 import identity, session
from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type

DOCUMENTATION = r'''
---
module: set_instance_tag
short_description: Set a tag on an instance
version_added: "1.0.0"
description: Set a tag on an instance

options:
    instance_id:
        description: ID of the Nectar instance
        required: true
        type: str
    tag:
        description: tag value
        required: true
        type: str
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - openstack.set_instance_tag

author:
    - Martin Feller (@mondkaefer)
'''

EXAMPLES = r'''
# Pass in a message
- name: Test with a message
  openstack.set_instance_tag:
    instance_id: 5dd81950-5a21-4095-830a-150d68499095
    tag: test
'''

RETURN = r'''

'''


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        instance_id=dict(type='str', required=True),
        tag=dict(type='str', required=True)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False
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
    OS_COMPUTE_API_VERSION: float = 2.83
    result['changed'] = False
    auth = identity.v3.application_credential.ApplicationCredential(
               auth_url=os.environ['OS_AUTH_URL'],
               application_credential_id=os.environ['OS_APPLICATION_CREDENTIAL_ID'],
               application_credential_secret=os.environ['OS_APPLICATION_CREDENTIAL_SECRET'])
    sess = session.Session(auth=auth)
    novac = nova_client.Client(OS_COMPUTE_API_VERSION, session=sess)
    instance_id = module.params['instance_id']
    tag = module.params['tag']
    tag_list = novac.servers.get(instance_id).tag_list()
    if tag not in tag_list:
        novac.servers.get(instance_id).add_tag(tag)
        result['changed'] = True

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
