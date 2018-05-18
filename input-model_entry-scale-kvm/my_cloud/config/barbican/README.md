README
======

## First Time Initial Master Key Setup
When Barbican is used with *simple_crypto_plugin* as secret store backend, its
master key needs to be defined **before initial deployment**. This backend is
used when secrets are stored in its database. If you don't specify key before
deployment, default master key is used (not recommended practice).

** Once master key is set, it must not be modified. **

** Earlier if you defined your own encrypted master key, Before you run any playbooks **
** remember that you need to export that encryption key in the following environment variable: **
** export ARDANA_USER_PASSWORD_ENCRYPT_KEY=<encryption key> **
** For more details on this, please refer to official Ardana OpenStack/Barbican documentation **

** If you are upgrading and already have the master key defined from previous version or installation, check **
** ~/openstack/ardana/ansible/roles/barbican-common/vars/barbican_deploy_config.yml **
** for *barbican_customer_master_key* value, if the value does not have a prefix "@ardana@" **
** that means it is not encrypted. It is highly recommended to encrypt this value **
* Encrypt the existing key during upgrade
  * setup the environment variable ARDANA_USER_PASSWORD_ENCRYPT_KEY which contain the key
  used to encrypt barbican master key.
  * Note: Before you run any playbooks, remember that you need to export the encryption key in the
  following environment variable. For instructions *
  * export ARDANA_USER_PASSWORD_ENCRYPT_KEY=<USER_ENCRYPTION_KEY>
  * execute
    * python *roles/KEYMGR-API/templates/generate_kek <barbican_customer_master_key>*
  * Master key is generated at stdout
  * Set above master key in file  ~/openstack/ardana/ansible/roles/barbican-common/vars/barbican_deploy_config.yml
    * Replace existing *barbican_customer_master_key* value with above generated
      master key
    * Commit the change in git repository.
    * *cd ~/openstack/ardana/ansible/*
    * *ansible-playbook -i hosts/localhost ready-deployment.yml*
    * Once master key is set, continue with cloud deployment.

** It is not recommended to change the master key during the upgrade process **
** Changing master key will result in read error for existing secrets as they were **
** encrypted using previous master key. **

* Generate master key using provided python *generate_kek* script on deployer node
  * setup the environment variable ARDANA_USER_PASSWORD_ENCRYPT_KEY which contain the key
  used to encrypt barbican master key.
  * export ARDANA_USER_PASSWORD_ENCRYPT_KEY=<USER_ENCRYPTION_KEY>
  * python  *roles/KEYMGR-API/templates/generate_kek*
* Master key is generated at stdout from previous command
* Set above master key in file  ~/openstack/ardana/ansible/roles/barbican-common/vars/barbican_deploy_config.yml
  * Replace existing *barbican_customer_master_key* value with above generated
  master key
  * Commit the change in git repository.
  * *cd ~/openstack/ardana/ansible/*
  * *ansible-playbook -i hosts/localhost ready-deployment.yml*
* Once master key is set, continue with cloud deployment.

# Configurable Values

There are different configurable entries for Barbican.

1. Configuration entries that are available upstream in *barbican.conf*. This has upstream defined configurable values.
2. Deployment specific configuration which are not part of *barbican.conf* like
log_level, process count etc.

The following section describes the mechanism used for overriding or changing those
configuration entries.

* To change configuration entries used by Barbican API service config i.e. barbican.conf
   * Edit the files *roles/KEYMGR-API/templates/barbican.conf.j2*  to add or
   change any config settings
   * Make sure that you don't change any values under {{ }} in above mentioned file.

* To change, configurable properties which are not part of Barbican API service config
  such as log level
    * Edit the files  *roles/barbican-common/vars/barbican_deploy_config.yml* to
    change any config settings
    * Here you can only change values, can't add any new settings
    * For log level, replace current value with new log level e.g.
        * *barbican_loglevel: "DEBUG"*

To make above changes effective, Barbican reconfigure playbook needs to be executed
which deploys the new settings on its API nodes.

* cd ~/openstack/ardana/ansible/
* ansible-playbook -i hosts/localhost ready-deployment.yml
* cd ~/scratch/ansible/next/ardana/ansible
* *ansible-playbook -i hosts/verb_hosts barbican-reconfigure.yml*

## Tested/Supported Features

### Enable or Disable Auditing
  * Auditing feature can be disabled or enabled by following steps.
    * Edit the file  ~/openstack/my_cloud/definition/cloudConfig.yml
    * All audit related configuration is defined under `audit-settings` section.
        * Please note that valid yaml syntax need to be followed when specifying values.
    * Service name defined under `enabled-services` or `disabled-services` override
      the default setting (i.e. `default: enabled` or `default: disabled`)
    * To enable auditing, make sure that `barbican` service name is within
      `enabled-services` list of `audit-settings` section or is **not** present in
      `disabled-services` list when `default: enabled`.
    * To disable auditing for barbican service specifically, make sure that `barbican`
      service name is within `disabled-services` list of `audit-settings`
      section or is **not** present in `enabled-services` list when
      `default: disabled`.
    * It is incorrect to specify service name in both list. If its specified, then
      `enabled-services` value takes precedence.
    * Commit the change in git repository.
    * *cd ~/openstack/ardana/ansible/*
    * *ansible-playbook -i hosts/localhost config-processor-run.yml*
    * *ansible-playbook -i hosts/localhost ready-deployment.yml*
    * *cd ~/scratch/ansible/next/ardana/ansible*
  * *ansible-playbook -i hosts/verb_hosts barbican-reconfigure.yml*


### Enable or Disable KMIP Plugin
  * (Step 1) To populate or change clients certificate on Barbican nodes.
      * For KMIP device, SSL client certificate is needed as generally HSM devices
        require 2-way SSL for security reasons.
        * Get needed client certificate, client private key and client root CA recognized
        by HSM device.
        * These certificate information is provided to Barbican service via reconfigure
        playbook.
        * Look into KMIP certificates sample file barbican_kmip_plugin_config_sample.yml
        * Copy this file to a temporary directory e.g. /tmp/kmip_plugin_certs.yml
        * Edit the file to provide either client certificates as absolute file paths (i.e.
        `client_cert_file_path`, `client_key_file_path`, `client_cacert_file_path`) or
         pasting certificate content directly into the file (i.e. in `client_cert_content`,
         `client_key_content`, `client_cacert_content`).
       * *ansible-playbook  -i hosts/verb_hosts barbican-reconfigure.yml -e@/tmp/kmip_plugin_certs.yml*

  * (Step 2) To provide or update HSM connection credential for Barbican service
      * In this step, KMIP plugin connection details are provided to service.
          * Edit the files  ~/openstack/ardana/ansible/roles/barbican-common/vars/barbican_deploy_config.yml
          * Change the value `use_kmip_secretstore_plugin` to True to use KMIP
            plugin or False to use default secret store plugin (`store_crypto`).
          * Provide KMIP client connection credentials and KMIP server
            hostname and port.
          * Commit the change in git repository.
          * *cd ~/openstack/ardana/ansible/*
          * ansible-playbook -i hosts/localhost ready-deployment.yml
          * *cd ~/scratch/ansible/next/ardana/ansible*
      * *ansible-playbook -i hosts/verb_hosts barbican-reconfigure.yml*

```
Note: If preferred, actions described in step 1 can be executed without reconfigure
playbook execution. And reconfigure playbook action can be executed at the end of
step 2 actions. This can reduce reconfigure need in initial setup.

ansible-playbook  -i hosts/verb_hosts barbican-reconfigure.yml -e@/tmp/kmip_plugin_certs.yml

Individual step 1 and step 2 are needed when client certificates or HSM connection
information needs to be updated.
```

#### Troubleshooting KMIP Plugin Setup

1.  Make sure that in Certificate Signing Request (CSR) 'Common Name' field must
match the *barbican_kmip_username* value defined in
*roles/barbican-common/vars/barbican_deploy_config.yml*. Otherwise you may see
*Internal Server Error* in Barbican for create secret request which does not
translate well into this issue.

2. Currently Barbican does not return clear related error with regards to client
certificate setup and its connectivity with KMIP server. During secret create
request, general *Internal Server Error* is returned when certificate is invalid
or missing any of needed client certificate data (client certificate, key and CA
root certificate).

### Enable or Disable PKCS11 Plugin

  * (Step 1) Import and install the PKCS11 library debian package.
    * This is a one-time setup to install pkcs11 package on barbican nodes.
    * Make sure you are on deployer node
    * If not present, Create the directory
      /home/stack/third-party/barbican/pkgs/debian
    * Populate the directory with the full set of debian packages which has
      HSM specific PKCS11 library
    * Run the 3rd-party import playbook:
      *cd ~/openstack/ardana/ansible/
      *ansible-playbook -i hosts/localhost third-party-import.yml*
      *cd ~/scratch/ansible/next/ardana/ansible
      *ansible-playbook -i hosts/verb_hosts osconfig-run.yml*
    * This will import the above packages to the Ardana thirdparty repo,
      and ready for installation, this will ensure that
      /etc/apt/source.list.d entry exists for the third-party apt repo.
      For example
      You can import hppkcs11 (<eskm_pkcs11_package_version>.deb), which is PKCS11
      library for ESKM (Enterprise Secure Key Manager) HSM
    * Once the library package is imported into third party repository
      you can install the library package by running barbican playbook
      by passing extra ansible variable `barbican_pkcs11_package_name,
      if the given package is not present on the controller nodes
      it will install the latest version from the 3rd party repository, like
    * *ansible-playbook  -i hosts/verb_hosts barbican-reconfigure.yml --extra-vars "barbican_pkcs11_package_name=hppkcs11"*
    * Or if you want to install specific version of the package, or
      upgrade or downgrade from the one you have on the controller nodes,
      you can pass the version info to the playbook, like
      *ansible-playbook  -i hosts/verb_hosts barbican-reconfigure.yml --extra-vars "barbican_pkcs11_package_name=hppkcs11=0.2.1"*
    * Above step would install provided package on controller node in its
      default location.

  * (Step 2) To provide or update HSM connection credential for Barbican service
      * In this step, PKCS11 plugin connection details are provided to service.
          * Edit the files  ~/openstack/ardana/ansible/roles/barbican-common/vars/barbican_deploy_config.yml
          * Change the value `use_pkcs11_crypto_plugin` to True to use PKCS11
            plugin crypto setup. False is used to indicate other plugin setup usage.
          * Provide details for PKCS11 client connection. Details needed are
            * session password
            * expected location for vendor specific pkcs11 shared library on
              Barbican nodes. Provide absolute path on **controller** node.
            * label used for master kek
            * label used for hmac key
          * If PKCS11 provider is ESKM, then `barbican_pkcs11_provider_is_eskm`
            flag can be set to True and playbooks will use default paths for
            library and its certificate location.
          * Commit the change in git repository.
          * *cd ~/openstack/ardana/ansible/*
          * ansible-playbook -i hosts/localhost ready-deployment.yml
          * *cd ~/scratch/ansible/next/ardana/ansible*
      * *ansible-playbook -i hosts/verb_hosts barbican-reconfigure.yml*
      * If PKCS11 provider is ESKM, then `barbican_pkcs11_provider_is_eskm` flag can be set to True
        and playbooks will use default paths for library and its certificate location

  * (Step 3) *** Atalla ESKM Specific Setup Only ***
     Please note that PKCS11 provider may have some custom configuration steps
     and those needs to be done manually. This specific step is just provided
     for ESKM PKCS11 connector.
     In this step, ESKM KMIP server address is set or updated.
    * For ESKM PKCS11 connector, there is connection configuration information
      needed by its PKCS11 connector e.g. KMIP server address, token firmware
      version and various flags needed for PKCS11 session.
    * Customer is expected to provide KMIP server address.
    * Barbican playbook provides following mechanism to generate related
      configuration with customer provided KMIP server address. For any other
      customization, customer is expected to refer ESKM PKCS11 documentation and
      make those changes manually on controller nodes hosting Barbican service.
    * Edit the files  ~/openstack/ardana/ansible/roles/barbican-common/vars/barbican_deploy_config.yml
    * Set the value for `barbican_pkcs11_eskm_kmip_host`, `barbican_pkcs11_eskm_kmip_port`
    * Commit the change in git repository.
    * *cd ~/openstack/ardana/ansible/*
    * ansible-playbook -i hosts/localhost ready-deployment.yml
    * *cd ~/scratch/ansible/next/ardana/ansible*
    * *ansible-playbook  -i hosts/verb_hosts barbican-reconfigure.yml --extra-vars "barbican_pkcs11_eskm_generate_conf=True"*

  * (Step 4) To populate or change clients certificate on Barbican nodes.
      * For PKCS11 device, SSL client certificate is needed as generally HSM devices
        require 2-way SSL for security reasons.
        * Get needed client certificate, client private key and client root CA recognized
        by HSM device.
        * These certificate information is provided to Barbican service via reconfigure
        playbook.
        * Look into HSM certificates sample file barbican_pkcs11_plugin_config_sample.yml
        * Copy this file to a temporary directory e.g. /tmp/pkcs11_plugin_certs.yml
        * Edit the file to provide either client certificates as absolute file paths (i.e.
        `client_cert_file_path`, `client_key_file_path`, `client_cacert_file_path`) or
         pasting certificate content directly into the file (i.e. in `client_cert_content`,
         `client_key_content`, `client_cacert_content`).
        * Edit the file  ~/openstack/ardana/ansible/roles/barbican-common/vars/barbican_deploy_config.yml
          for pkcs11 certificate locations.
        * Provide expected path for client side certificates on barbican nodes.
            * `barbican_pkcs11_client_cert_path` - client certificate file path
            * `barbican_pkcs11_client_key_path` - Private key file path created
                via CSR generation
            * `barbican_pkcs11_client_cacert_path` - root CA recognized by HSM
                device and used for CSR signing.
        * Commit the change in git repository.
        * *cd ~/openstack/ardana/ansible/*
        * ansible-playbook -i hosts/localhost ready-deployment.yml
        * *cd ~/scratch/ansible/next/ardana/ansible*
      * *ansible-playbook -i hosts/verb_hosts barbican-reconfigure.yml -e@/tmp/pkcs11_plugin_certs.yml*

  * (Step 5) Generate labels for master kek and hmac key used for PKCS11 plugin.
    This is one-time setup which generates needed mkek and hmac labels. As a
    pre-requisite, Step 2, (+ Step 2b in ESKM HSM case) and Step 3 needs to be done
    beforehand.
    * *ansible-playbook -i hosts/verb_hosts barbican-reconfigure.yml --extra-vars "barbican_pkcs11_generate_labels=True"*


```
Note: If preferred, actions described in step 1 (except running 3rd-party import playbook), 2, 3 and 4 can be executed
together. Just make sure that all PKCS11 specific variables are configured
correctly in barbican_deploy_config.yml and single space is present between
variables defined via 'extra-vars' option

ansible-playbook  -i hosts/verb_hosts barbican-reconfigure.yml \
    --extra-vars "barbican_pkcs11_package_name=hppkcs11 \
    barbican_pkcs11_generate_labels=True" \
    -e@/tmp/pkcs11_plugin_certs.yml

For ESKM, combined step is as follows (with generate conf file option).

ansible-playbook  -i hosts/verb_hosts barbican-reconfigure.yml \
    --extra-vars "barbican_pkcs11_package_name=hppkcs11 \
    barbican_pkcs11_eskm_generate_conf=True \
    barbican_pkcs11_generate_labels=True" \
    -e@/tmp/pkcs11_plugin_certs.yml

Individual step 1, step 2, step 3 or step 4 are needed when pkc11 library,
client certificates or HSM connection information needs to be updated.
```

#### Troubleshooting PKCS11 Plugin Setup

1. With ESKM device, make sure that in Certificate Signing Request (CSR)
'Common Name' field must exist in HSM as a local user. Otherwise you may see
*Internal Server Error* in Barbican for create secret request which does not
translate well into this issue.
