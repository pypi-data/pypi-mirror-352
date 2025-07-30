import typer
from getpass import getpass
from dektools.shell import output_data
from ..core.infisical import Infisical

app = typer.Typer(add_completion=False)


@app.command()
def fetch(site_url, client_id, project, environment, path=None, out=None, client_secret=None, fmt=None):
    _fetch(site_url, client_id, client_secret, project, environment, path, out, fmt)


@app.command()
def fetch_shortcut(url, out=None, fmt=None):
    site_url, client_id, client_secret, project, environment, path = url.split('@')
    _fetch(site_url, client_id, client_secret, project, environment, path, out, fmt)


def _fetch(site_url, client_id, client_secret, project, environment, path, out, fmt):
    if not client_secret:
        client_secret = getpass('Please input ClientSecret:')
    data = Infisical(site_url, client_id, client_secret).project_secrets(project, environment, path)
    output_data(data, out, fmt)
