#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)

import os
from keystoneauth1 import session
from keystoneauth1.identity import v3
from openstack.connection import Connection
from keystoneauth1.exceptions import NotFound
from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type

DOCUMENTATION = r'''
---
module: set_project_tag
short_description: Set a tag on a project
version_added: "1.0.0"
description: Set a tag on a project

options:
    project_id:
        description: ID of the Nectar project
        required: true
        type: str
    tag:
        description: tag value
        required: true
        type: str
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - ceradmin.openstack.set_project_tag

author:
    - Martin Feller (@mondkaefer)
'''

EXAMPLES = r'''
# Pass in a message
- name: Test with a message
  ceradmin.openstack.set_project_tag:
    project_id: 5dd81950-5a21-4095-830a-150d68499095
    tag: test
'''

RETURN = r'''

'''


def run_module():
    module_args = dict(
        project_id=dict(type='str', required=True),
        tag=dict(type='str', required=True)
    )

    result = dict(
        changed=False
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

    result['changed'] = False
    auth = v3.application_credential.ApplicationCredential(
               auth_url=os.environ['OS_AUTH_URL'],
               application_credential_id=os.environ['OS_APPLICATION_CREDENTIAL_ID'],
               application_credential_secret=os.environ['OS_APPLICATION_CREDENTIAL_SECRET'])
    sess = session.Session(auth=auth)
    conn = Connection(session=sess)
    project_id = module.params['project_id']
    tag = module.params['tag']
    try:
        p = conn.identity.get_project(project_id)
        tags = p.tags.copy()
        if tag not in tags:
            tags.append(tag)
            conn.identity.update_project(project_id, tags=tags)
            result['changed'] = True
    except NotFound:
        module.fail_json(msg=f'No such project: {project_id}', **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
