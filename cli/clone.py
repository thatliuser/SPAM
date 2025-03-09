from cli import CLI
import cli.arguments.options as options
class Clone(CLI):
    name = "clone"
    def __init__(self, args):
        super().__init__(args)
        
    def init_parser(self, usage: str = "", desc = None) -> None:
        super().init_parser(self.name, description="Clones VMs based on configuration file or options, used for workshops and CCDC mock environments")
    
    def post_process_args(self, options):
        # do post processing here
        return options
    
    def run(self):
        super().run()
        
        pass


def main(args=None):
    Clone.cli_executor(args)


if __name__ == "__main__":
    main()