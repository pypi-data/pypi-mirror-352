from collections import OrderedDict
from infisical_client import ClientSettings, InfisicalClient, ListSecretsOptions


class Infisical:
    def __init__(self, site_url, client_id, client_secret):
        self.site_url = site_url
        self.client_id = client_id
        self.client_secret = client_secret

    @property
    def client(self):
        return InfisicalClient(ClientSettings(
            site_url=self.site_url,
            client_id=self.client_id,
            client_secret=self.client_secret,
        ))

    def project_secrets(self, project, environment, path=None):
        secrets = self.client.listSecrets(options=ListSecretsOptions(
            project_id=project,
            environment=environment,
            path=path
        ))
        return OrderedDict(((s.secret_key, s.secret_value) for s in secrets))
