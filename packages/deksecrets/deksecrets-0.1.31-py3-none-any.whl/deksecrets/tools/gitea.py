import os
import tempfile
from getpass import getpass
from gitea import Gitea
from dektools.variables import get_user_email_from_git
from dektools.serializer.yaml import yaml
from dektools.dict import assign
from dektools.file import remove_path, list_dir, sure_dir
from dektools.zip import compress_files, decompress_files
from dektools.cfg import ObjectCfg
from ..core.gitea import fetch_file, upload_file, get_packages, packages_file_type


class GiteaProxy:
    package_ext = '.zip'
    data_ext = '.yaml'

    def __init__(self, ins: Gitea):
        self.ins = ins

    def upload(self, path):
        for path_org, org_name in list_dir(path, True):
            for path_project, project_name in list_dir(path_org, True):
                for path_version, version in list_dir(path_project, True):
                    file = tempfile.mktemp(suffix=self.package_ext)
                    compress_files(path_version, file)
                    upload_file(self.ins, org_name, project_name, version, file)
                    remove_path(file)

    def fetch_data(self, org, project, version, environment, path):
        file = tempfile.mktemp(suffix=self.package_ext)
        fetch_file(self.ins, org, project, version, file)
        path_out = decompress_files(file)
        remove_path(file)
        data_base = yaml.load(os.path.join(path_out, "_base", f"{path}{self.data_ext}"), default={})
        empty = object()
        data = yaml.load(os.path.join(path_out, environment, f"{path}{self.data_ext}"), default=empty)
        remove_path(path_out)
        if data is empty:
            return {}
        return assign(data_base or {}, data or {})

    def fetch_all(self, path, *orgs):
        for org in orgs:
            path_org = os.path.join(path, org)
            remove_path(path_org)
            for data in get_packages(self.ins, org):
                if data['type'] == packages_file_type:
                    project = data['name']
                    version = data['version']
                    path_version = os.path.join(path_org, project, version)
                    file = tempfile.mktemp(suffix=self.package_ext)
                    fetch_file(self.ins, org, project, version, file)
                    decompress_files(file, os.path.join(path_version))
                    remove_path(file)


class GiteaManager:
    gitea_cls = Gitea
    gitea_proxy_cls = GiteaProxy

    def __init__(self, name):
        self.name = name
        self.cfg = ObjectCfg(__name__, 'gitea', self.name, module=True)

    @property
    def gitea(self):
        data = self.cfg.get()
        auth = data['auth']
        token, username, password = auth['token'], auth['username'], auth['password']
        return self.gitea_proxy_cls(get_gitea_ins(data['url'], token, username, password, self.gitea_cls))

    def login(self, url, auth):
        self.cfg.set(dict(
            url=url.rstrip('/ '),
            auth=auth
        ))

    def logout(self):
        self.cfg.set({})

    def init(self):
        return sure_dir(self.cfg.path_dir)

    def upload(self):
        self.gitea.upload(self.cfg.path_dir)

    def fetch(self, org, project, version, environment, path):
        return self.gitea.fetch_data(org, project, version, environment, path)

    def fetch_all(self, orgs):
        self.gitea.fetch_all(self.cfg.path_dir, *orgs)


def get_gitea_ins(url, token, username, password, gitea_cls=Gitea):
    gitea_kwargs = {}
    if username:
        gitea_kwargs = dict(auth=(username, password))
    if token:
        gitea_kwargs = dict(token_text=token)
    return gitea_cls(url, **gitea_kwargs)


def get_gitea_auth_info(token=None, username=None, password=None):
    if not username and not token:
        token = getpass('Please input token:')
    if not token:
        if not username:
            du, _ = get_user_email_from_git()
            if du:
                fmt = f"({du})"
            else:
                fmt = ""
            username = input(f'Please input username{fmt}:')
            if not username:
                username = du
        if not password:
            password = getpass('Please input password:')
    return token, username, password
