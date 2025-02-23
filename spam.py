import argparse

from proxmoxer import ProxmoxAPI
from dotenv import load_dotenv
import clone
import os
import conf.config as config

def setup() -> None:
    pass

def main() -> None:
    parser = argparse.ArgumentParser(description="SPAM")

    subparsers = parser.add_subparsers(dest='command')
    
    parser.add_argument(
        '-s', '--setup',
        action='store_true',
        help='Prompt for Proxmox environment variables and create .env file'
    )

    clone_parser = subparsers.add_parser('clone', help='Clone VMs')

    clone_parser.add_argument(
        '-e', '--environment',
        type=str,
        nargs='?',
        const='conf/env.yaml',
        help='Specify and use configuration file to define targets for running the scripts against. Default file is conf/env.yaml'
    )  
    clone_parser.add_argument(
        'node',
        nargs='?',
        type=str,
        help='Name of node that the VM to be cloned is on. Optional if -e is set.'
    )
    clone_parser.add_argument(
        'source_id',
        nargs='?',
        type=str,
        help='ID of VM to be cloned. Optional if -e is set.'
    )
    clone_parser.add_argument(
        'newid',
        nargs='?',
        type=str,
        help='ID of target VM that will be created. Optional if -e is set.'
    )
    clone_parser.add_argument(
        '-n', '--name',
        type=str,
        help='Set a name for the new VM.'
    )
    clone_parser.add_argument(
        '-p', '--pool',
        type=str,
        help='Add the new VM to the specified pool.'
    )
    clone_parser.add_argument(
        '-f', '--full',
        action='store_true',
        help='Create a full copy of all disks. This is always done when you clone a normal VM. For VM templates, it will try to create a linked clone by default.'
    )
    clone_parser.add_argument(
        '-t', '--target',
        type=str,
        help='Target node. Only allowed if the original VM is on shared storage.'
    )
    clone_parser.add_argument(
        '-s', '--snapshot',
        type=str,
        help='The name of the snapshot.'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    load_dotenv()
    PROXMOX_HOST: str = os.getenv('PROXMOX_HOST')
    PROXMOX_USER: str = os.getenv('PROXMOX_USER')
    PROXMOX_PASSWORD: str = os.getenv('PROXMOX_PASSWORD')
    PROXMOX_REALM: str = os.getenv('PROXMOX_REALM')
    prox: ProxmoxAPI = ProxmoxAPI(PROXMOX_HOST, user=f'{PROXMOX_USER}@{PROXMOX_REALM}', password=PROXMOX_PASSWORD, verify_ssl=False)

    args = parser.parse_args()

    if args.command == 'clone':
        if (not args.node or not args.source_id or not args.newid) and not args.environment:
            parser.error("The 'node', 'source_id' and 'newid' arguments are required unless -e is set.")

        if args.environment:
            conf: dict[str,str] = config.get_config(args.environment)
            env: config.Env = config.get_env(conf)
            clone.clone_env(prox, env)
        else:
            include = {'newid', 'snapshot', 'target', 'full', 'pool', 'name'}
            args_dict: dict[str,str] = {key: (1 if value is True else 0 if value is False else value) for key, value in vars(args).items() if value is not None and key in include}
            clone.clone_vm(prox, args.node, args.source_id, **args_dict)
    else:
        if args.setup:
            setup()
        else:
            parser.print_help()
            return
if __name__ == "__main__":
    main()
    # load_dotenv()
    # PROXMOX_HOST = os.getenv('PROXMOX_HOST')
    # PROXMOX_USER = os.getenv('PROXMOX_USER')
    # PROXMOX_PASSWORD = os.getenv('PROXMOX_PASSWORD')
    # PROXMOX_REALM = os.getenv('PROXMOX_REALM')
    # prox = ProxmoxAPI(PROXMOX_HOST, user=f'{PROXMOX_USER}@{PROXMOX_REALM}', password=PROXMOX_PASSWORD, verify_ssl=False)
    # conf: dict = config.get_config("conf/box.yaml")
    # env: config.Env = config.get_env(conf)
    # # Testing
    #  #x = prox.nodes('cuci-r730-pve01').qemu('7101').clone.create(newid='28006',target='cuci-r730-pve03')
    # #print(x)
    # clone.clone_env(prox, env)
        
    