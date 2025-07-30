import typer
from getpass import getpass
from dektools.shell import shell_wrapper

app = typer.Typer(add_completion=False)


@app.command()
def auth(
        host, ca=None, token=None, port=6443,
        tsn='kubernetes', cluster='deksecrets', context='deksecrets',
        user='deksecrets'):
    if not ca:
        ca = getpass('Please input content of ca.crt:')
    if not token:
        token = getpass('Please input token:')
    shell_wrapper(
        f"kubectl config set-cluster {cluster} "
        f"--server=https://{host}:{port} "
        f"--tls-server-name={tsn}"
    )
    shell_wrapper(f"kubectl config set clusters.{cluster}.certificate-authority-data {ca}")
    shell_wrapper(f"kubectl config set-context {context} --cluster={cluster}")
    shell_wrapper(f"kubectl config set-credentials {user} --token={token}")
    shell_wrapper(f"kubectl config set-context {context} --user={user}")
    shell_wrapper(f"kubectl config use-context {context}")


@app.command()
def auth_remove(cluster='deksecrets', context='deksecrets', user='deksecrets'):
    shell_wrapper(f"kubectl config delete-user {user}")
    shell_wrapper(f"kubectl config delete-cluster {cluster}")
    shell_wrapper(f"kubectl config delete-context {context}")


@app.callback()
def callback():
    pass
