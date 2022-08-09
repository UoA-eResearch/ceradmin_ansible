#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)

from ansible.module_utils.basic import AnsibleModule
import os
import nectarallocationclient.client as allocation_client
from nectarallocationclient.exceptions import NotFound
from keystoneauth1 import identity, session

__metaclass__ = type

DOCUMENTATION = r'''
---
module: get_allocations
short_description: Return allocations. Can be filtered.
version_added: "1.0.0"
description: Get a list of allocations, based on filters

options:
    allocation_home
        description: filter by allocation_home
        required: false
        type: str
        default: auckland
    status
        description: filter by status
        required: false
        type: str
    
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - ceradmin.openstack.get_allocations

author:
    - Martin Feller (@mondkaefer)
'''

EXAMPLES = r'''
# Pass in a message
- name: Test with a message
  openstack.get_allocations:
    allocation_home: auckland
    status: A

'''

RETURN = r'''
# Returns a list of allocation objects
'''


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        allocation_home=dict(type='str', required=False, default='auckland'),
        status=dict(type='str', required=False, default='A')
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        allocations=None
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
            module.fail_json(msg='%s is not set as environment variable.' % x, **result)

    auth = identity.v3.application_credential.ApplicationCredential(
             auth_url=os.environ['OS_AUTH_URL'],
             application_credential_id=os.environ['OS_APPLICATION_CREDENTIAL_ID'],
             application_credential_secret=os.environ['OS_APPLICATION_CREDENTIAL_SECRET'])
    sess = session.Session(auth=auth)
    allocationc = allocation_client.Client(1, session=sess)
    allocs = allocationc.allocations.list(
                parent_request__isnull=True,
                allocation_home=module.params["allocation_home"],
                status=module.params["status"])
    result['allocations'] = []
    for alloc in allocs:
        result['allocations'].append(alloc.to_dict())

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
