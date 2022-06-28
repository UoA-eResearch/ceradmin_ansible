#!/bin/bash

set -e

org_name="CeR"
project_name="Nectar"
inventory_name="Empty Inventory"
cred_type_openstack_app_cred_name="OpenStack Application Credential"
cred_type_tenable_name="Tenable Config"
job_template_name="Tenable Setup"

if [[ $1 == "create" ]]; then
  awx organizations create \
    --name "${org_name}" > /dev/null
  echo "Created organization ${org_name}"

  awx credential_types create \
    --name "${cred_type_openstack_app_cred_name}" \
    --kind cloud \
    --inputs "@config/openstack_app_cred_type.yml" \
    --injectors "@config/openstack_app_cred_type_injectors.yml" > /dev/null
  echo "Created credeential type ${cred_type_openstack_app_cred_name}"

  awx credential_types create \
    --name "${cred_type_tenable_name}" \
    --kind cloud \
    --inputs "@config/tenable_cred_type.yml" \
    --injectors "@config/tenable_cred_type_injectors.yml" > /dev/null
  echo "Created credential type ${cred_type_tenable_name}"

  awx projects create \
    --name "${project_name}" \
    --organization "${org_name}" \
    --scm_type git \
    --scm_url https://github.com/mondkaefer/awx_debug_playbook \
    --wait > /dev/null
  echo "Created project ${project_name}"

  awx inventories create \
    --name "${inventory_name}" \
    --organization "${org_name}" > /dev/null
  awx hosts create \
    --name "localhost" \
    --inventory "${inventory_name}" \
    --enabled true > /dev/null
  echo "Created inventory ${inventory_name}"

  awx job_templates create \
    --name "${job_template_name}" \
    --project "${project_name}" \
    --playbook "setup_scanning.yml" \
    --inventory "${inventory_name}" \
    --extra_vars "@config/job_template_tenable_setup_extra_vars.yml" \
    --job_type run \
    --survey_enabled true > /dev/null
  echo "Created job template ${job_template_name}"

elif [[ $1 == "delete" ]]; then
  awx credential_types delete "${cred_type_openstack_app_cred_name}"
  echo "Deleted credential type ${cred_type_openstack_app_cred_name}"

  awx credential_types delete "${cred_type_tenable_name}" 
  echo "Deleted credential type ${cred_type_tenable_name}"

  awx job_templates delete "${job_template_name}"
  echo "Deleted job template ${job_template_name}"

  awx inventories delete "${inventory_name}"
  echo "Deleted inventory ${inventory_name}"

  awx projects delete "${project_name}"
  echo "Deleted project ${project_name}"

  awx organizations delete "${org_name}"
  echo "Delete organization ${org_name}"

else
  echo "Invalid parameter: '$1'"
fi

