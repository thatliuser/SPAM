from cli import CLI
import cli.arguments.options as options
import utils
import conf.config as config
class Clone(CLI):
    name = "clone"
    def __init__(self, args):
        super().__init__(args)

        self.clone_args: dict = {}
        self.environment = None


    def init_parser(self, usage: str = "", desc = None) -> None:
        super().init_parser(self.name, description="Clones VMs based on configuration file or options, used for workshops and CCDC mock environments")
        options.add_environment_file_options()
        options.add_name_options()
        options.add_new_id_options()
        options.add_node_options()
        options.add_pool_options()
        options.add_source_id_options()
        options.add_target_node_options()
        self.parser.add_argument(
        '-f', '--full',
        action='store_true',
        help='Create a full copy of all disks. This is always done when you clone a normal VM. For VM templates, it will try to create a linked clone by default.'
        )
        self.parser.add_argument(
        '-s', '--snapshot',
        type=str,
        help='The name of the snapshot to clone.'
        )

    def post_process_args(self, options):
        # do post processing here
        if not options.node:
            options.node = self.default_node
        if (not options.node or not options.source_id or not options.newid) and not options.environment:
            self.parser.error("The 'node', 'source_id' and 'newid' arguments are required unless -e is set.")
        include: set[str] = {'newid', 'snapshot', 'target', 'full', 'pool', 'name', 'bwlimit', 'node', 'vmid', 'snapname', 'storage', 'target', 'description', 'format'}
        self.clone_args: dict[str,str] = {key: (1 if value is True else 0 if value is False else value) for key, value in vars(options).items() if value is not None and key in include}
        if options.environment:
            self.environment = self.prep_config()
        return options
    
    def run(self) -> None:
        super().run()
        if self.options.environment:
            self._clone_env()
        else:
            self._clone_vm(self.options.node, self.options.source_id, **vars(self.clone_args))
        return
    
    def _clone_vm(self, source_node: str, source_id: str, **kwargs) -> None:
        try:
            task_id = self.prox.nodes(source_node).qemu(source_id).clone.create(**kwargs)
            target = source_node if 'target' not in kwargs else kwargs['target']
            print(f"Cloning VMID {source_id} in {source_node} to VMID {kwargs['newid']} in {target}")
            utils.block_until_done(self.prox, task_id, source_node)
        except Exception as e:
            print(e)
        return

    def _clone_env(self) -> None:
        for node in self.environment.nodes:
            for box in self.environment.boxes:
                self._clone_vm(self.environment.template_node, box.id, target=node,**box.config)
                if box.cloud:
                    utils.cloudinit.set_cloudinit(self.prox, node, box.config.newid, **box.cloud)
        return


def main(args=None):
    Clone.cli_executor(args)


if __name__ == "__main__":
    main()