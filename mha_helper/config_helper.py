# (c) 2013, Ovais Tariq <ovaistariq@gmail.com>
#
# This file is part of mha_helper
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import fnmatch
import os
import ConfigParser
import re


class ConfigHelper(object):
    MHA_HELPER_CONFIG_DIR = '/etc/mha-helper'
    MHA_HELPER_CONFIG_OPTIONS = ['writer_vip_cidr', 'vip_type', 'report_email', 'requires_sudo', 'cluster_interface']
    VIP_PROVIDER_TYPES = ['none', 'metal', 'aws', 'openstack']

    # This stores the configuration for every host
    host_config = dict()


    @staticmethod
    def load_config():
        pattern = '*.conf'

        for root, dirs, files in os.walk(ConfigHelper.MHA_HELPER_CONFIG_DIR):
            for filename in fnmatch.filter(files, pattern):
                config_file_path = os.path.join(ConfigHelper.MHA_HELPER_CONFIG_DIR, filename)
                print("Reading config file: %s" % config_file_path)

                config_parser = ConfigParser.RawConfigParser()
                config_parser.read(config_file_path)

                # Read the default config values first. The default config values are used when a config option is not
                # defined for the specific host
                if not config_parser.has_section('default'):
                    return False

                default_config = dict()
                for opt in ConfigHelper.MHA_HELPER_CONFIG_OPTIONS:
                    opt_value = config_parser.get('default', opt)
                    if not ConfigHelper.validate_config_value(opt, opt_value):
                        print("Parsing the option '%s' with value '%s' failed" % (opt, opt_value))
                        return False

                    default_config[opt] = opt_value

                # Setup host based configs. Initially hosts inherit config from the default section but override them
                # within their own sections
                for hostname in config_parser.sections():
                    ConfigHelper.host_config[hostname] = dict()

                    # We read the options from the host section of the config
                    for opt in ConfigHelper.MHA_HELPER_CONFIG_OPTIONS:
                        if config_parser.has_option(hostname, opt) and opt != 'writer_vip_cidr':
                            ConfigHelper.host_config[hostname][opt] = config_parser.get(hostname, opt)

                    # We now read the options from the default section and if any option has not been set by the host
                    # section we set that to what is defined in the default section, writer_vip_cidr is always read from
                    # the default section because it has to be global for the entire replication cluster
                    # If the option is not defined in both default and host section, we throw an error
                    for opt in ConfigHelper.MHA_HELPER_CONFIG_OPTIONS:
                        if opt not in ConfigHelper.host_config[hostname] or opt == 'writer_vip_cidr':
                            # If the host section did not define the config option and the default config also does
                            # not define the config option then we bail out
                            if opt not in default_config:
                                print("Missing required option '%s'. The option should either be set in default "
                                      "section or the host section of the config" % opt)
                                return False

                            ConfigHelper.host_config[hostname][opt] = default_config[opt]

        return True

    @staticmethod
    def validate_config_value(config_key, config_value):
        if config_key == 'writer_vip_cidr':
            return ConfigHelper.validate_ip_address(config_value)

        if config_key == 'vip_type':
            return config_value in ConfigHelper.VIP_PROVIDER_TYPES

        if config_key == 'report_email':
            return ConfigHelper.validate_email_address(config_value)

        if config_key == 'requires_sudo':
            return config_value in ['yes', 'no']

        if config_key == 'cluster_interface':
            return config_value is not None and len(config_value) > 0

    @staticmethod
    def validate_ip_address(ip_address):
        pattern = '^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(/([0-9]|[1-2][0-9]|3[0-2]))$'
        return bool(re.match(pattern, ip_address))

    @staticmethod
    def validate_email_address(email_address):
        pattern = '^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$'
        return bool(re.match(pattern, email_address))

    def __init__(self, host):
        self._host = host
        self._host_config = self.__class__.host_config[host]

    def get_writer_vip(self):
        return self.get_writer_vip_cidr().split('/')[0]

    def get_writer_vip_cidr(self):
        return self._host_config['writer_vip_cidr']

    def get_vip_type(self):
        return self._host_config['vip_type']

    def get_manage_vip(self):
        return self._host_config['vip_type'] != 'none'

    def get_report_email(self):
        return self._host_config['report_email']

    def get_requires_sudo(self):
        return self._host_config['requires_sudo']

    def get_cluster_interface(self):
        return self._host_config['cluster_interface']
