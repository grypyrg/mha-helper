# (c) 2015, Kenny Gryp <gryp@dakin.be>
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
from ssh_helper import SSHHelper
from config_helper import ConfigHelper
import re

class MySQLConfigHelper(object):
    def __init__(self, host, host_ip=None, ssh_user=None, ssh_port=None, ssh_options=None):
        config_helper = ConfigHelper(host)
        self._requires_sudo = config_helper.get_requires_sudo()
        self._read_only_config = config_helper.get_read_only_config()
        self._super_read_only = config_helper.get_super_read_only()
        self._ssh_client = SSHHelper(host, host_ip, ssh_user, ssh_port, ssh_options)

    def generate_read_only_config_content(self):
        if self._super_read_only == 'no'
            return "# generated by mha_helper, do not touch\n[mysqld]\nread_only=on\n"
        else
            return "# generated by mha_helper, do not touch\n[mysqld]\nsuper_read_only=on\n"

    def set_read_only_config(self):
        command = "echo '%s' > %s" % (self.generate_read_only_config_content(), self._read_only_config)
        return self.execute_ssh_command(command)

    def unset_read_only_config(self):
        command = "echo '' > %s" % self._read_only_config
        return self.execute_ssh_command(command)

    def has_read_only_config(self):
        command = "cat %s" % self._read_only_config
        if self.execute_ssh_command(command, True) == self.generate_read_only_config_content
            return True
        else
            return False

    def execute_ssh_command(self, command, return_output=False):
        if self._requires_sudo:
            final_command = "sudo %s" % command

        # Connect to the host over SSH
        if not self._ssh_client.make_ssh_connection():
            return False

        # Send Command to the Host
        ret_code, stdout_lines = self._ssh_client.execute_ssh_command(final_command)
        if not ret_code:
            if len(stdout_lines) > 0:
                print("Command output: %s" % "\n".join(stdout_lines))
                return False
        if return_output
            return "\n".join(stdout_lines)