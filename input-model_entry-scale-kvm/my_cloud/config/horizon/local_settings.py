#
# (c) Copyright 2015-2017 Hewlett Packard Enterprise Development LP
# (c) Copyright 2017-2018 SUSE LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from openstack_dashboard import exceptions
from openstack_dashboard.settings import HORIZON_CONFIG

DEBUG = False
COMPRESS_OFFLINE = True
_LOG_LEVEL = '{{ horizon_log_level }}'

STATIC_ROOT = '{{ horizon_static_dir }}'

ALLOWED_HOSTS = ['*']

# Enable the angular work in Kilo that reimplements 'launch instance',
# and disable the legacy Django implementation.
LAUNCH_INSTANCE_LEGACY_ENABLED = False
LAUNCH_INSTANCE_NG_ENABLED = True

with open('{{ horizon_conf_dir }}/.secret_key_store', 'r') as f:
    SECRET_KEY = f.read()

#TODO Modify this link to current doc path
HORIZON_CONFIG['help_url'] = "https://www.suse.com/documentation/suse-openstack-cloud-7"

# Turn off browser autocompletion for forms including the login form and
# the database creation workflow if so desired.
HORIZON_CONFIG["password_autocomplete"] = False

# Setting this to True will disable the reveal button for password fields,
# including on the login form.
HORIZON_CONFIG["disable_password_reveal"] = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
    }
}


# Send email to the console by default
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Enable/Disable Keystone V3 with multi-domain support
OPENSTACK_API_VERSIONS = {
    "identity": 3,
}
OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT = True
OPENSTACK_KEYSTONE_DEFAULT_DOMAIN = 'default'

OPENSTACK_ENDPOINT_TYPE = "{{ horizon_openstack_endpoint_type }}"
OPENSTACK_SSL_CACERT = "{{ trusted_ca_bundle }}"
# The CA certificate for the external endpoints
ARDANA_EXTERNAL_SSL_CACERT = "{{ external_cacert_filename }}"

# HORI-3288: set SECURE_PROXY_SSL_HEADER
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTOCOL", "https")

{% if horizon_public_protocol == 'https' -%}
  {% if horizon_private_protocol == 'https' %}
# http://docs.openstack.org/security-guide/dashboard/checklist.html
USE_SSL = True
# Set SECURE for csrf and session cookies so they're only sent
# over HTTPS connections.
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
# Harden cookies to prevent XSS attacks
SESSION_COOKIE_HTTPONLY = True
  {% else %}
# WARNING - Horizon is configured such that its public endpoint is
# behind HTTPS but its internal one is not. It is strongly recommended
# that the internal endpoint be secured, and the settings below set to True.
# They cannot be set unless BOTH endpoints are secured.
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
  {% endif %}
{%- endif %}

OPENSTACK_KEYSTONE_URL = "{{ horizon_keystone_url }}"

OPENSTACK_KEYSTONE_DEFAULT_ROLE = "_member_"

OPENSTACK_KEYSTONE_BACKEND = {
    'name': 'native',
    'can_edit_user': True,
    'can_edit_group': True,
    'can_edit_project': True,
    'can_edit_domain': True,
    'can_edit_role': True
}

OPENSTACK_HYPERVISOR_FEATURES = {
    'can_set_mount_point': True,

    # NOTE: as of Grizzly this is not yet supported in Nova so enabling this
    # setting will not do anything useful
    'can_encrypt_volumes': False
}


# HORI-4120 - setting enable_quotas to False, or not including it
# will result in Create Network, Create Subnet, Create Router buttons
# not showing up
#
# The OPENSTACK_NEUTRON_NETWORK settings can be used to enable optional
# services provided by neutron. Options currently available are load
# balancer service, security groups, quotas, VPN service.
OPENSTACK_NEUTRON_NETWORK = {
    'enable_router': True,
    'enable_quotas': True,
    'enable_ipv6': True,
    'enable_distributed_router': False,
    'enable_ha_router': False,
    'enable_lb': True,
    'enable_fip_topology_check': True,

    # Set which provider network types are supported. Only the network types
    # in this list will be available to choose from when creating a network.
    # Network types include local, flat, vlan, gre, and vxlan.
    'supported_provider_types': ['*'],

    # Set which VNIC types are supported for port binding. Only the VNIC
    # types in this list will be available to choose from when creating a
    # port.
    # VNIC types include 'normal', 'macvtap' and 'direct'.
    # Set to empty list or None to disable VNIC type selection.
    'supported_vnic_types': ['*']
}

API_RESULT_LIMIT = 1000
API_RESULT_PAGE_SIZE = 20

SWIFT_FILE_TRANSFER_CHUNK_SIZE = 1024 * 1024

DROPDOWN_MAX_ITEMS = 30

TIME_ZONE = "UTC"

SITE_BRANDING = 'SUSE Ardana OpenStack'

AVAILABLE_THEMES = [
    ('default', 'Default', 'themes/default'),
]

DEFAULT_THEME = 'default'

OPENSTACK_CINDER_FEATURES = {
    'enable_backup': True,
}

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '{{ mysql.host }}',
        'NAME': '{{ mysql.horizon_db }}',
        'USER': '{{ mysql.horizon_user }}',
        'PASSWORD': '{{ mysql.horizon_password }}',
        {% if mysql.use_ssl | bool %}
        'OPTIONS': {'ssl': {'ca': '{{ ca_file}}' }},
        {% endif %}
    }
}

LOGGING = {
    'version': 1,
    # When set to True this will disable all logging except
    # for loggers specified in this configuration dictionary. Note that
    # if nothing is specified here and disable_existing_loggers is True,
    # django.db.backends will still log unless it is disabled explicitly.
    'disable_existing_loggers': False,
    'formatters': {
        'context': {
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'format': '%(asctime)s.%(msecs)03d %(process)d %(levelname)s ' +
                      '%(name)s %(message)s'
        },
        'logstash': {
            '()': 'logstash.LogstashFormatterVersion1',
            'message_type': 'horizon'
        },
    },
    'handlers': {
        'null': {
            'level': 'INFO',
            'class': 'logging.NullHandler',
        },
        'console': {
            # Set the level to "DEBUG" for verbose output logging.
            'formatter': 'context',
            'level': _LOG_LEVEL,
            'class': 'logging.StreamHandler',
        },
        'logstash': {
            'formatter': 'logstash',
            'class': 'logging.handlers.WatchedFileHandler',
            'level': _LOG_LEVEL,
            'filename': '/var/log/horizon/horizon-json.log',
        },
    },
    'loggers': {
        # Logging from django.db.backends is VERY verbose, send to null
        # by default.
        'django.db.backends': {
            'handlers': ['null'],
            'propagate': False,
        },
        'requests': {
            'handlers': ['null'],
            'propagate': False,
        },
        'iso8601': {
            'handlers': ['null'],
            'propagate': False,
        },
        'scss': {
            'handlers': ['null'],
            'propagate': False,
        },
        '': {
            'handlers': ['console', 'logstash'],
            'level': _LOG_LEVEL,
            'propagate': False,
        },
    }
}


# If running management commands, don't initialize the full logging palava
if os.environ.get('HORIZON_LOG_TO_CONSOLE', None):
    LOGGING = {
        'version': 1,
        'formatters': {
            'logstash': {
                '()': 'logstash.LogstashFormatterVersion1',
                'message_type': 'horizon-management'
            }
        },
        'handlers': {
            'console': {
                'level': _LOG_LEVEL,
                'class': 'logging.StreamHandler',
            },
            'logstash': {
                'formatter': 'logstash',
                'class': 'logging.handlers.WatchedFileHandler',
                'level': _LOG_LEVEL,
                'filename': '/var/log/horizon/management/management-json.log'
            }
        },
        'loggers': {
            '': {
                'handlers': ['console', 'logstash'],
                'level': _LOG_LEVEL,
                'propagate': False
            }
        }
    }

WEBSSO_ENABLED = {{ horizon_websso_enabled }}
WEBSSO_CHOICES = (
("credentials", "Keystone Credentials"),
{% for choice in horizon_websso_choices %}
("{{ choice.protocol }}", "{{ choice.description }}"),
{% endfor %}
)
WEBSSO_KEYSTONE_URL = "{{ horizon_websso_keystone_url }}"

# DISALLOW_IFRAME_EMBED can be used to prevent Horizon from being embedded
# within an iframe. Legacy browsers are still vulnerable to a Cross-Frame
# Scripting (XFS) vulnerability, so this option allows extra security hardening
# where iframes are not used in deployment. Default setting is True.
# For more information see:
# http://tinyurl.com/anticlickjack
DISALLOW_IFRAME_EMBED = True

REST_API_REQUIRED_SETTINGS = ['OPENSTACK_HYPERVISOR_FEATURES',
                              'LAUNCH_INSTANCE_DEFAULTS',
                              'OPENSTACK_IMAGE_FORMATS']
