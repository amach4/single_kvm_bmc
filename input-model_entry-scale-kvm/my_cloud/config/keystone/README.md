
(c) Copyright 2015-2016 Hewlett Packard Enterprise Development LP
(c) Copyright 2017 SUSE LLC

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.


80README
======

There are different configurable entries for keystone
1. Configuration entries that go into keystone.conf
2. Deployment specific configuration which are not part of keystone.conf like
   log_level,process count etc.
3. Additional configuration like the domain-specific configuration or LDAP CA
   certificates update.

The following section describes the mechanism used for overriding or changing those
configuration entries:

For 1: keystone.conf

    - Edit the files keystone.conf.j2 located on a deployer node
      /home/stack/openstack/my_cloud/config/keystone/.  Modify this template file as appropriate.
    - You can get default/available configuration for Liberty from
      http://docs.openstack.org/liberty/config-reference/content/keystone-configuration-file.html
    - Make sure you don't change any values under {{ }}
    - Commit the changes and rerun playbooks of configuration processor and deployment area
      preparation (refer to section Appendix A for the detail)
    - Run reconfiguration playbook in deployment area:
      $ cd ~/scratch/ansible/next/ardana/ansible
      $ ansible-playbook -i hosts/verb_hosts keystone-reconfigure.yml

For 2: keystone deployment such as log level

    - Edit respective parameters in /home/stack/openstack/my_cloud/config/keystone/keystone_deploy_config.yml.
      Here you can only change values, can't add any new settings
    - Commit the changes and rerun playbooks of configuration processor and deployment area
      preparation (refer to section Appendix A for the detail)
    - Run reconfiguration playbook in deployment area:
      $ cd ~/scratch/ansible/next/ardana/ansible
      $ ansible-playbook -i hosts/verb_hosts keystone-reconfigure.yml

For 3.1: Domain-Specific Configuration File Store

By default, domain-specific driver configuration file store is enabled. To update configuration
for a specific LDAP domain, please see instruction below:
    - Ensure that the following configuration options in the main configuration file template:
      /home/stack/openstack/my_cloud/config/keystone/keystone.conf.j2
      [identity]
      domain_specific_drivers_enabled = True
      domain_configurations_from_database = False
    - Locate the file:
      /home/stack/openstack/my_cloud/config/keystone/keystone_configure_ldap_sample.yml
    - Save a copy of this file with a new name, for example:
      /home/stack/openstack/my_cloud/config/keystone/keystone_configure_ldap_my.yml
    - Edit the file to carry the correct definition of the LDAP server connection
    - Commit the changes and rerun playbooks of configuration processor and deployment area
      preparation (refer to section Appendix A for the detail)
    - Run reconfiguration playbook in deployment area:
      $ cd ~/scratch/ansible/next/ardana/ansible
      $ ansible-playbook -i hosts/verb_hosts keystone-reconfigure.yml
        -e@/home/stack/openstack/my_cloud/config/keystone/keystone_configure_ldap_my.yml
    - Follow these same steps for each LDAP domain with which you are integrating Keystone, creating
      a yaml file for each and running the reconfigure playbook once for each additional domain.

For 3.2: Set up or Switch to Domain-Specific Driver Configuration - Database Store

To set up Domain-Specific Driver Configuration - Database Store, the steps are to deploy the
Domain-Specific Driver Configuration - File Store first, as shown above in 3.1.
Then switch to the database store. Once switched, all of the domain-specific driver configuration
files shall be ignored by the system. No domain mixture of file and database stores is supported.
    - Ensure that the following configuration options in the main configuration file template:
      /home/stack/openstack/my_cloud/config/keystone/keystone.conf.j2
      [identity]
      domain_specific_drivers_enabled = True
      domain_configurations_from_database = True
      [domain_config]
      driver = sql
    - Commit the changes and rerun playbooks of configuration processor and deployment area
      preparation (refer to section Appendix A for the detail)
    - Run reconfiguration playbook in deployment area:
      $ cd ~/scratch/ansible/next/ardana/ansible
      $ ansible-playbook -i hosts/verb_hosts keystone-reconfigure.yml
    - Upload the domain-specific configuration files to the database if they has not been loaded.
      If they have already loaded and just like to switch back to database store mode,
      then skip this upload step.
      Otherwise,
      -- Go to either one of control nodes Keystone deployed.
         Verify domain-specific driver configuration files are located under the directory
         /etc/keystone/domains with the format: keystone.<domain name>.conf
      -- Use Keystone manager utility to load domain-specific configuration files to the
         database. You may choose to upload all or one by one as shown below:

         Upload all configuration files to the SQL database
         $ keystone-manage domain_config_upload --all

         or

         Upload individual domain-specific configuration files by specifying the domain name:
         $ keystone-manage domain_config_upload --domain-name <domain name>
         If you have more than one LDAP domains to be processed, then repeat this per-domain
         configuration loading step with corresponding appropriate configuration content for each
         LDAP domain.

         Note: Please be advised that Keystone manager utility doesn't upload domain-specific
         driver configuration file the second time for the same domain.
         For the management of the domain-specific driver configuration in the database store,
         you may refer to Domain-Specific Driver Configuration - Database Store Management
         via Identity API.

For 3.3: Updating LDAP CA certificates

    - Locate the file keystone_configure_ldap_certs_sample.yml
      /home/stack/openstack/my_cloud/config/keystone/keystone_configure_ldap_certs_sample.yml
    - Save a copy of this file with a new name, for example:
      /home/stack/openstack/my_cloud/config/keystone/keystone_configure_ldap_certs_update.yml
    - Edit the file and specify the correct single file path name for the ldap certicicates.
      This file pathname has to be consistent with the domain-specific configuration
      tls_cacertfile file pathname.
    - Edit the file and populate or update it with ldap CA certificates for all domains
    - Commit the changes and rerun playbooks of configuration processor and deployment area
      preparation (refer to section Appendix A for the detail)
    - Run reconfiguration playbook in deployment area:
      $ cd ~/scratch/ansible/next/ardana/ansible
      $ ansible-playbook -i hosts/verb_hosts keystone-reconfigure.yml
        -e@/home/stack/openstack/my_cloud/config/keystone/keystone_configure_ldap_certs_update.yml

Enabling features in Keystone

   Ardana doesn't enable all the features by default. Some of these features are tested/supported
   and some of them are non-core features. Tested features can be enabled and used in production.
   Non-core features can be enabled for POC or to get customer feedback. Non-core
   features may require few manual configuration and may have defects. We will move an
   Non-core feature to supported feature once we have resolved all the issues with it

Tested/Supported Features

Enable/Disable Keystone auditing

    Keystone audit is disabled by default. The following instruction is for keystone audit only.
    For the rest of Ardana OpenStack services auditing, please refer to Ardana OpenStack audit documentation for the detail.

    To Enable/Disable keystone audit, do the following in the deployer node:
    - Edit the file ~/openstack/my_cloud/definition/cloudConfig.yml
      (All audit related configuration is defined under `audit-settings` section.)
    - Case 1: Enable keystone audit
      Add 'keystone' in service list of enabled-services and remove or comment out 'keystone' in
      service list of disabled-services if existing. If no more item within 'disabled-services:',
      then remove or comment out 'disabled-service:' as well. For example,
      ----------------------------------
      audit-settings:
         audit-dir: /var/audit
         default: disabled
         enabled-services:
           - keystone
         disabled-services:
           - nova
           - barbican
        #  - keystone
           - cinder
           - ceilometer
           - neutron
      ----------------------------------

      Case 2: Disable keystone audit
      Add 'keystone' in service list of disabled-services and remove or comment out 'keystone' in
      service list of enabled-services if existing. If no more item within enabled-services,
      then remove or comment out 'enabled-services:' as well. For example,
      ----------------------------------
      audit-settings:
         audit-dir: /var/audit
         default: disabled
         #enabled-services:
         #  - keystone
         disabled-services:
           - nova
           - barbican
           - keystone
           - cinder
           - ceilometer
           - neutron
      ----------------------------------

    - Commit the changes and rerun playbooks of configuration processor and deployment area
      preparation (refer to section Appendix A for the detail)
    - Run reconfiguration playbook in deployment area:
      $ cd ~/scratch/ansible/next/ardana/ansible
      $ ansible-playbook -i hosts/verb_hosts keystone-reconfigure.yml

    Note:
    * It is incorrect to specify service name in both lists of enabled-services and
      disabled-services list simultaneously. If both specified, then 'enabled-services' item
      takes precedence.
    * Please note that valid yaml syntax need to be followed when specifying values. If there is
      no item specified in the enabled-services, then enabled-services has to be removed or
      commented out. Similarly for disabled-services.

Non-core Features

Changing for UUID token to Fernet Token

    - Edit the file /home/stack/openstack/my_cloud/config/keystone/keystone_deploy_config.yml.
      Change the value `keystone_configure_fernet` to True to enable Fernet Token
    - Commit the changes and rerun playbooks of configuration processor and deployment area
      preparation (refer to section Appendix A for the detail)
    - Run reconfiguration playbook in deployment area:
      $ cd ~/scratch/ansible/next/ardana/ansible
      $ ansible-playbook -i hosts/verb_hosts keystone-reconfigure.yml

[Appendix A]

Commit the change into local git repository, and rerun playbooks of configuration processor
and deployment area preparation:
      $ cd ~/ardana
      $ git checkout site
      $ git add -A
      $ git commit -m "type your commit message here..."
      $ cd ~/openstack/ardana/ansible
      $ ansible-playbook -i hosts/localhost config-processor-run.yml
      $ ansible-playbook -i hosts/localhost ready-deployment.yml
