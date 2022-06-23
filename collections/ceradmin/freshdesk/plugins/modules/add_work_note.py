#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
import os
from ansible.module_utils.basic import AnsibleModule
from freshdesk.v2.api import API

__metaclass__ = type

DOCUMENTATION = r'''
---
module: add_work_note
short_description: Add work note to existing Freshdesk ticket
version_added: "1.0.0"
description: add work note to existing Freshdesk ticket

options:
    ticket_id:
        description: ID of existing ticket
        required: true
        type: int
    work_note:
        description: Text of the work note to add
        required: true
        type: str

        
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - ceradmin.freskdesk.add_work_note

author:
    - Martin Feller (@mondkaefer)
'''

EXAMPLES = r'''
# Pass in a message
- name: Add work note to existing ticket
  ceradmin.freshdesk.add_work_note
    ticket_id: 1234
    work_note: This is a work note
'''

RETURN = r'''
Nothing is returned
'''


def run_module():
    module_args = dict(
        statuses=dict(type='list', required=False, default=[]),
        tags=dict(type='list', required=False, default=[]),
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
    for x in ['FRESHDESK_DOMAIN', 'FRESHDESK_API_KEY', 'FRESHDESK_EMAIL_CONFIG_ID', 'FRESHDESK_GROUP_ID']:
        if x not in os.environ:
            module.fail_json(msg='%s is not set as environment variable' % x, **result)

    api = API(os.environ['FRESHDESK_DOMAIN'], os.environ['FRESHDESK_API_KEY'])
    api.comments.create_note(ticket_id=int(module.params['ticket_id']), body=module.params['work_note'])
    result['changed'] = True

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
