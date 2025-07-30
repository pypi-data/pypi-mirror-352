from typing import Dict

from nacos_ai.common.auth import StaticCredentialsProvider, CredentialsProvider
from nacos_ai.common.ai_client_config import AIClientConfig


class AIClientConfigBuilder:
    def __init__(self):
        self._config = AIClientConfig()

    def server_address(self, server_address: str) -> "AIClientConfigBuilder":
        if server_address is not None and server_address.strip() != "":
            for server_address in server_address.strip().split(','):
                self._config.server_list.append(server_address.strip())
        return self

    def timeout_ms(self, timeout_ms) -> "AIClientConfigBuilder":
        self._config.timeout_ms = timeout_ms
        return self

    def log_level(self, log_level) -> "AIClientConfigBuilder":
        self._config.log_level = log_level
        return self

    def log_dir(self, log_dir: str) -> "AIClientConfigBuilder":
        self._config.log_dir = log_dir
        return self

    def access_key(self, access_key: str) -> "AIClientConfigBuilder":
        if not self._config.credentials_provider:
            self._config.credentials_provider = StaticCredentialsProvider(access_key_id=access_key)
        else:
            self._config.credentials_provider.set_access_key_id(access_key)
        return self

    def secret_key(self, secret_key: str) -> "AIClientConfigBuilder":
        if not self._config.credentials_provider:
            self._config.credentials_provider = StaticCredentialsProvider(access_key_secret=secret_key)
        else:
            self._config.credentials_provider.set_access_key_secret(secret_key)
        return self

    def credentials_provider(self, credentials_provider: CredentialsProvider) -> "AIClientConfigBuilder":
        self._config.credentials_provider = credentials_provider
        return self

    def username(self, username: str) -> "AIClientConfigBuilder":
        self._config.username = username
        return self

    def password(self, password: str) -> "AIClientConfigBuilder":
        self._config.password = password
        return self

    def app_conn_labels(self, app_conn_labels: dict) -> "AIClientConfigBuilder":
        if self._config.app_conn_labels is None:
            self._config.app_conn_labels = {}
        self._config.app_conn_labels.update(app_conn_labels)
        return self

    def build(self):
        return self._config