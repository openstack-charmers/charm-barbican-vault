# Copyright 2016 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
from __future__ import print_function

import mock

import reactive.barbican_vault_handlers as handlers

import charms_openstack.test_utils as test_utils


class TestRegisteredHooks(test_utils.TestRegisteredHooks):

    def test_hooks(self):
        defaults = [
            'charm.installed',
            'config.changed',
            'update-status']
        hook_set = {
            'when': {
                'secret_backend_vault_request': (
                    'secrets-storage.connected',),
            },
            'when_all': {
                'plugin_info_barbican_publish': (
                    'endpoint.secrets.joined', 'secrets-storage.available',
                    'endpoint.secrets-storage.changed',),
            },
            'when_not': {
                'secret_backend_vault_request': (
                    'secrets-storage.available',),
            },
        }
        # test that the hooks were registered via the
        # reactive.barbican_handlers
        self.registered_hooks_test_helper(handlers, hook_set, defaults)


class TestBarbicanVaultHandlers(test_utils.PatchHelper):

    def patch_charm(self):
        barbican_vault_charm = mock.MagicMock()
        self.patch_object(handlers.charm, 'provide_charm_instance',
                          new=mock.MagicMock())
        self.provide_charm_instance().__enter__.return_value = \
            barbican_vault_charm
        self.provide_charm_instance().__exit__.return_value = None
        return barbican_vault_charm

    def test_secret_backend_vault_request(self):
        barbican_vault_charm = self.patch_charm()
        self.patch_object(handlers.reactive, 'endpoint_from_flag')
        secrets_storage = mock.MagicMock()
        self.endpoint_from_flag.return_value = secrets_storage
        barbican_vault_charm.secret_backend_name = 'charm-barbican-vault'
        self.patch_object(handlers.reactive, 'clear_flag')

        handlers.secret_backend_vault_request()
        self.endpoint_from_flag.assert_called_once_with(
            'secrets-storage.connected')
        secrets_storage.request_secret_backend.assert_called_once_with(
            'charm-barbican-vault', isolated=False)

    def test_plugin_info_barbican_publish(self):
        barbican_vault_charm = self.patch_charm()
        self.patch_object(handlers.reactive, 'endpoint_from_flag')
        barbican = mock.MagicMock()
        secrets_storage = mock.MagicMock()
        self.endpoint_from_flag.side_effect = [barbican, secrets_storage]
        self.patch_object(handlers.vault_utils, 'retrieve_secret_id')
        self.patch_object(handlers.reactive, 'clear_flag')

        handlers.plugin_info_barbican_publish()
        self.endpoint_from_flag.assert_has_calls([
            mock.call('endpoint.secrets.joined'),
            mock.call('secrets-storage.available'),
        ])
        vault_data = {
            'approle_role_id': secrets_storage.unit_role_id,
            'approle_secret_id': self.retrieve_secret_id(),
            'vault_url': secrets_storage.vault_url,
            'kv_mountpoint': barbican_vault_charm.secret_backend_name,
            'ssl_ca_crt_file': barbican_vault_charm.installed_ca_name,
        }
        barbican_vault_charm.install_ca_cert.assert_called_once_with(
            secrets_storage.vault_ca)
        barbican.publish_plugin_info.assert_called_once_with(
            'vault', vault_data)
        self.clear_flag.assert_called_once_with(
            'endpoint.secrets-storage.changed')
