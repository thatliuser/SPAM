from abc import ABC, abstractmethod
import cli.arguments.options as options
import sys
# Inspiration from Ansible code structure

class CLI(ABC):
    def __init__(self, args) -> None:
        self.args = args
        self.parser = None
        self.options = None
        self.prox = None

    @abstractmethod
    def init_parser(self, usage: str = "", desc = None) -> None:
        self.parser = options.create_base_parser(self.name, usage=usage, description=desc)

    def parse(self) -> None:
        self.init_parser()
        options = self.parser.parse_args(self.args[1:])
        self.options = self.post_process_args(options)
    
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