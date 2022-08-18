#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
import os
from ansible.module_utils.basic import AnsibleModule
from freshdesk.v2.api import API
from freshdesk.v2.models import Ticket

__metaclass__ = type

DOCUMENTATION = r'''
---
module: get_tickets
short_description: Get Freshdesk tickets
version_added: "1.0.0"
description: Get Freshdesk tickets

options:
    statuses:
        description: List of status ids to filter by. 
                     Each status is one of [2 (Open), 3 (Pending), 4 (Resolved), 
                     5 (Closed), 6 (Waiting on Customer)]
        required: false
        type: list
        default: []
    tags:
        description: List of tags to filter by
        required: false
        type: list
        default: []

        
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - ceradmin.freskdesk.get_tickets

author:
    - Martin Feller (@mondkaefer)
'''

EXAMPLES = r'''
# Pass in a message
- name: Get Freshdesk tickets
  ceradmin.freshdesk.get_tickets
    tags:
      - security
'''

RETURN = r'''
List of tickets
'''


def convert_ticket(ticket):
    converted_ticket = dict()
    for prop, value in vars(ticket).items():
        converted_ticket[prop] = value
    return converted_ticket


def run_module():
    module_args = dict(
        statuses=dict(type='list', required=False, default=[]),
        tags=dict(type='list', required=False, default=[])
    )

    result = dict(
        changed=False,
        tickets=[]
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
    tags = module.params['tags']
    statuses = module.params['statuses']
    filter_string = f"group_id:{os.environ['FRESHDESK_GROUP_ID']}"
    if len(tags) > 0:
        tag_string = " AND ".join([f'tag:"{x}"' for x in tags])
        filter_string += f" AND {tag_string}"
    if len(statuses) > 0:
        status_string = " OR ".join([f'status:{x}' for x in statuses])
        filter_string += f" AND ({status_string})"
    tickets = api.tickets.filter_tickets(filter_string)

    # convert the tickets - will result in errors otherwise
    ticket_list = []
    if len(tickets) > 0:
        for t in tickets:
            ticket_list.append(convert_ticket(t))

    result['tickets'] = ticket_list

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
