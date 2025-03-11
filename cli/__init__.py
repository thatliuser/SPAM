from abc import ABC, abstractmethod
import cli.arguments.options as options
import sys
from dotenv import load_dotenv
import os
from proxmoxer import ProxmoxAPI
import conf.config as config
# Inspiration from Ansible code structure

class CLI(ABC):
    def __init__(self, args) -> None:
        self.args = args
        self.parser = None
        self.options = None
        self.prox = None
        self.default_node = None
        self.proxmox_host = None
        self.proxmox_user = None
        self.proxmox_pass = None
        self.proxmox_realm = None
        self.default_node = None

    @abstractmethod
    def init_parser(self, usage: str = "", desc = None) -> None:
        self.parser = options.create_base_parser(self.name, usage=usage, description=desc)

    def parse(self) -> None:
        self.init_parser()
        options = self.parser.parse_args(self.args[1:])
        self.load_env()
        self.options = self.post_process_args(options)
    
    def connect(self):
        self.prox: ProxmoxAPI = ProxmoxAPI(self.promxox_host, user=f'{self.proxmox_user}@{self.proxmox_realm}', password=self.proxmox_pass, verify_ssl=False)
    
    def load_env(self) -> None:
        load_dotenv()
        self.promxox_host = os.getenv('PROXMOX_HOST')
        self.proxmox_user = os.getenv('PROXMOX_USER')
        self.proxmox_pass = os.getenv('PROXMOX_PASSWORD')
        self.proxmox_realm = os.getenv('PROXMOX_REALM')
        self.default_node = os.getenv('PROXMOX_DEFAULT_NODE')

    def prep_config(self) -> config.Env:
        conf: dict[str,str] = config.get_config(self.options.environment)
        env: config.Env = config.get_env(conf)
        return env

    @abstractmethod
    def post_process_args(self, options):
        # do post processing here
        return options
    
    @abstractmethod
    def run(self):
        self.parse()

    @classmethod
    def cli_executor(cls, args=None):
        if args is None:
            args = sys.argv
        cli = cls(args)
        cli.run()

# add method to connect to proxmox 

# add block until done here