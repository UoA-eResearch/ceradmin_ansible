#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)

import os
from keystoneclient.exceptions import NotFound
from keystoneclient import utils
from keystoneclient.v3 import client
from keystoneauth1.identity import v3
from keystoneauth1 import session
from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type

DOCUMENTATION = r'''
---
module: get_projects
short_description: Return list of projects
version_added: "1.0.0"
description: Return list of projects

options:
    domain_id:
        description: filter by domain id
        required: false
        type: str
        default: nz
    user:
        description: filter by user (name or id)
        required: false
        type: str
        default: None
    enabled:
        description: filter by enabled status
        required: false
        type: bool
        default: None
    tags:
        description: filter projects that contain all of the specified tags (comma-separated)
        required: false
        type: str
        default: ''
    tags_any:
        description: filter projects that contain at least one of the specified tags (comma-separated)
        required: false
        type: str
        default: ''
    not_tags:
        description: filter projects that do not contain exactly all of the specified tags (comma-separated)
        required: false
        type: str
        default: ''
    not_tags_any:
        description: filter projects that do not contain any one of the specified tags (comma-separated)
        required: false
        type: str
        default: ''
    
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - ceradmin.openstack.get_projects

author:
    - Martin Feller (@mondkaefer)
'''

EXAMPLES = r'''
# Pass in a message
- name: Test with a message
  ceradmin.openstack.get_projects:
    tags: 'auckland_condition_of_use,accepted'
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
details:
    description: List of projects
    type: list
    returned: always
'''


def filter_by_enabled(projects, enabled: bool):
    if enabled is None:
        return [p.to_dict() for p in projects]
    else:
        p_list = []
        for p in projects:
            tmp_p = p.to_dict()
            if tmp_p['enabled'] == enabled:
                p_list.append(tmp_p)
        return p_list


def run_module():

    module_args = dict(
        domain_id=dict(type='str', required=False, default='b38a521521d844e49daf98571fa8a153'),#nz
        user=dict(type='str', required=False, default=None),
        enabled=dict(type='bool', required=False, default=None),
        tags=dict(type='str', required=False, default=None),
        tags_any=dict(type='str', required=False, default=None),
        not_tags=dict(type='str', required=False, default=None),
        not_tags_any=dict(type='str', required=False, default=None)
    )

    result = dict(
        changed=False,
        projects=[]
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

    auth = v3.application_credential.ApplicationCredential(
             auth_url=os.environ['OS_AUTH_URL'],
             application_credential_id=os.environ['OS_APPLICATION_CREDENTIAL_ID'],
             application_credential_secret=os.environ['OS_APPLICATION_CREDENTIAL_SECRET'])
    sess = session.Session(auth=auth)
    keystone_c = client.Client(session=sess)

    user = module.params['user']
    if user is not None and '@' in user:
        try:
            user = utils.find_resource(keystone_c.users, user).to_dict()['id']
        except NotFound:
            module.fail_json(msg=f'No such user: {user}', **result)

    projects = keystone_c.projects.list(domain=module.params['domain_id'],
                                        user=user,
                                        tags=module.params['tags'],
                                        tags_any=module.params['tags_any'],
                                        not_tags=module.params['not_tags'],
                                        not_tags_any=module.params['not_tags_any'])

    result['projects'] = filter_by_enabled(projects, module.params['enabled'])
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
