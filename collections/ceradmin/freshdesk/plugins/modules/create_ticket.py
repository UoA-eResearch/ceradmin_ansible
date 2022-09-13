#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
import os
from ansible.module_utils.basic import AnsibleModule
from freshdesk.v2.api import API

__metaclass__ = type

DOCUMENTATION = r'''
---
module: create_ticket
short_description: Create Freshdesk ticket
version_added: "1.0.0"
description: Create Freshdesk ticket

options:
    recipient:
        description: Email address of ticket owner
        required: true
        type: str
    subject:
        description: Subject of ticket
        required: true
        type: str
    body:
        description: Ticket body
        required: true
        type: str
    template_vars:
        description: Variables used in ticket body
        required: true
        type: dict
    status:
        description: Status of ticket. 
                     One of [2 (Open), 3 (Pending), 4 (Resolved), 5 (Waiting on Customer)]
        required: true
        type: int
    ticket_type:
        description: Type of ticket. 
                     One of [Problem, Question, Incident, Feature Request]
        required: true
        type: str
    priority:
        description: Priority of ticket.
                     One of [1 (Low), 2 (Medium), 3 (High), 4 (Urgent)]
        required: false
        type: str
        default: 1
    cc_list:
        description: Email addresses to be put on cc
        required: false
        type: list
        default: []
    tags:
        description: Tags
        required: false
        type: list
        default: []
    dry_run:
        description: If true, information about ticket will be printed to stdout
                     but not ticket will be created
        required: false
        type: bool
        default: true

        
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - ceradmin.freskdesk.create_ticket

author:
    - Martin Feller (@mondkaefer)
'''

EXAMPLES = r'''
# Pass in a message
- name: Create Freshdesk ticket
  ceradmin.freshdesk.create_ticket
    recipient: john@doe.com
    subject: Test ticket
    body: Hello world
    template_vars: {'test': 'value'}
    status: 6
    ticket_type: Question
    dry_run: false
    tags: 
      - foo
      - bar
'''

RETURN = r'''
ticket_id:
    description: ID of newly created ticket
    type: str
ticket_url:
    description: URL of newly created ticket
    type: str
template_vars:
    description: Template variables used in the body
    type: dict
'''


def run_module():
    module_args = dict(
        recipient=dict(type='str', required=True),
        subject=dict(type='str', required=True),
        body=dict(type='str', required=True),
        template_vars=dict(type='dict', required=True),
        status=dict(type='int', required=True),
        ticket_type=dict(type='str', required=True),
        priority=dict(type='int', required=False, default=1),
        cc_list=dict(type='list', required=False, default=[]),
        tags=dict(type='list', required=False, default=[]),
        dry_run=dict(type='bool', required=False, default=True),
    )

    result = dict(
        changed=False,
        ticket_id='N/A',
        ticket_url='N/A',
        template_vars=None,
        stdout='N/A'
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

    recipient_blacklist = ['andrew.botting@unimelb.edu.au']
    domain = os.environ['FRESHDESK_DOMAIN']
    api_key = os.environ['FRESHDESK_API_KEY']
    email_config_id = int(os.environ['FRESHDESK_EMAIL_CONFIG_ID'])
    group_id = int(os.environ['FRESHDESK_GROUP_ID'])
    subject = module.params['subject']
    body = module.params['body']
    template_vars = module.params['template_vars']
    recipient = module.params['recipient']
    status = module.params['status']
    ticket_type = module.params['ticket_type']
    priority = module.params['priority']
    cc_list = module.params['cc_list']
    tags = module.params['tags']
    dry_run = module.params['dry_run']

    for r in recipient_blacklist:
        if r in cc_list:
            cc_list.remove(r)

    if dry_run:
        result['stdout'] = f'''
Would create the following ticket:
--------
Ticket owner: {recipient}
On Cc: {cc_list}
Tags: {tags}
Subject: {subject}
Body:
{body}
--------'''
        result['template_vars'] = template_vars
    else:
        api = API(domain, api_key)
        ticket = api.tickets.create_outbound_email(subject=subject, description=body, email=recipient,
                                                   cc_emails=cc_list, email_config_id=email_config_id,
                                                   group_id=group_id, priority=priority, status=status,
                                                   type=ticket_type, tags=tags)
        result['ticket_id'] = ticket.id
        result['ticket_url'] = 'https://{}/helpdesk/tickets/{}'.format(domain, ticket.id)
        result['template_vars'] = template_vars
        result['changed'] = True

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
