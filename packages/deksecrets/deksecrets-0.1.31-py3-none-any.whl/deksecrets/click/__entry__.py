from dektools.typer import command_version
from . import app
from .infisical import app as infisical_app
from .k8s import app as k8s_app
from .gitea import app as gitea_app

command_version(app, __name__)
app.add_typer(infisical_app, name='infisical')
app.add_typer(k8s_app, name='k8s')
app.add_typer(gitea_app, name='gitea')


def main():
    app()
