#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)

import os
import keystoneclient.client as keystone_client
from keystoneclient import utils
from keystoneauth1 import identity, session
from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type

DOCUMENTATION = r'''
---
module: get_user_by_id
short_description: Look up user details by id
version_added: "1.0.0"
description: Look up user details by id

options:
    email:
        description: id of Nectar user
        required: true
        type: str
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - openstack.get_user_by_id

author:
    - Martin Feller (@mondkaefer)
'''

EXAMPLES = r'''
# Pass in a message
- name: Get user
  openstack.get_user_by_id
    id: b6717975146a48b2a608884f440ec8a9

'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
details:
    description: Openstack user dict, or None
    type: dict
    returned: always
'''


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        id=dict(type='str', required=True)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        user=None
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

    # Verify required environment variables are defined
    for x in ['OS_AUTH_URL', 'OS_APPLICATION_CREDENTIAL_ID', 'OS_APPLICATION_CREDENTIAL_SECRET']:
        if x not in os.environ:
            module.fail_json(msg='%s is not set as environment variable' % x, **result)

    keystone_api_version = 3
    auth = identity.v3.application_credential.ApplicationCredential(
             auth_url=os.environ['OS_AUTH_URL'],
             application_credential_id=os.environ['OS_APPLICATION_CREDENTIAL_ID'],
             application_credential_secret=os.environ['OS_APPLICATION_CREDENTIAL_SECRET'])
    keystonec = keystone_client.Client(keystone_api_version, session=session.Session(auth=auth))
    result['user'] = keystonec.users.get(module.params['id']).to_dict()

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()