import argparse

from proxmoxer import ProxmoxAPI
from dotenv import load_dotenv
import clone
import os
import conf.config as config
import status
import snapshot
import utils

def setup() -> None:
    pass


#TODO cleanup into multiple parser subclasses

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
        type=int,
        help='ID of VM to be cloned. Optional if -e is set.'
    )
    clone_parser.add_argument(
        'newid',
        nargs='?',
        type=int,
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
    clone_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    start_parser = subparsers.add_parser('start', help='Start VMs')

    start_parser.add_argument(
        'node',
        type=str,
        help='Name of node that the VM to be started is on.'
    )
    start_parser.add_argument(
        'vmid',
        nargs='?',
        type=int,
        help='VMID of the VM. Optional if -r is set.'
    )
    start_parser.add_argument(
        '-r', '--range',
        nargs=2,
        metavar=('first', 'last'),
        type=int,
        help='Range of VMIDs to start (inclusive).'
    )

    stop_parser = subparsers.add_parser('stop', help='Stop VMs')

    stop_parser.add_argument(
        'node',
        type=str,
        help='Name of node that the VM to be stopped is on.'
    )
    stop_parser.add_argument(
        'vmid',
        nargs='?',
        type=int,
        help='VMID of the VM. Optional if -r is set.'
    )
    stop_parser.add_argument(
        '-r', '--range',
        nargs=2,
        metavar=('first', 'last'),
        type=int,
        help='Range of VMIDs to stop (inclusive).'
    )

    snapshot_parser = subparsers.add_parser('snapshot', help='Snapshot Utility')

    snapshot_parser.add_argument(
        'node',
        type=str,
        help='Name of node that the VM is on'
    )
    snapshot_parser.add_argument(
        'vmid',
        nargs='?',
        type=int,
        help='VMID of the VM. Optional if -r is set.'
    )
    snapshot_parser.add_argument(
        '-n', '--name',
        type=str,
        help='Name of the snapshot. Default is base.'
    )
    snapshot_parser.add_argument(
        '-r', '--range',
        nargs=2,
        metavar=('first', 'last'),
        type=int,
        help='Range of VMIDs to modify (inclusive).'
    )
    snapshot_parser.add_argument(
        '-s', '--start',
        action='store_true',
        help='Start the VM after rolling back.'
    )
    snapshot_parser.add_argument(
        '-b', '--rollback',
        action='store_true',
        help='Rollback VM'
    )
    snapshot_parser.add_argument(
        '-m', '--vmstate',
        action='store_true',
        help='Start the VM after rolling back.'
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
            include: set[str] = {'newid', 'snapshot', 'target', 'full', 'pool', 'name'}
            args_dict: dict[str,str] = {key: (1 if value is True else 0 if value is False else value) for key, value in vars(args).items() if value is not None and key in include}
            clone.clone_vm(prox, args.node, args.source_id, **args_dict)
    elif args.command == 'start':
        if not args.vmid and not args.range:
            parser.error("The 'vmid' argument are required unless -r is set.")
        if not args.range:
            status.start_vm(prox, args.node, args.vmid)
        else:
            utils.function_over_range(status.start_vm, args.range[0], args.range[1], prox, args.node)
    elif args.command == 'stop':
        if not args.vmid and not args.range:
            parser.error("The 'vmid' argument are required unless -r is set.")

        if not args.range:
            status.stop_vm(prox, args.node, args.vmid)
        else:
            utils.function_over_range(status.stop_vm, args.range[0], args.range[1], prox, args.node)
    elif args.command == 'snapshot':
        if not args.vmid and not args.range:
            parser.error("The 'vmid' argument are required unless -r is set.")

        # make this into function
        if args.rollback:
            include: set[str] = {'start', 'name'}
            args_dict: dict[str,str] = {key: (1 if value is True else 0 if value is False else value) for key, value in vars(args).items() if value is not None and key in include}
            if not args.range:
                snapshot.rollback_to_snapshot(prox, args.node, args.vmid, **args_dict)
            else:
                utils.function_over_range(snapshot.rollback_to_snapshot, args.range[0], args.range[1], prox, args.node, **args_dict)
        else:
            include: set[str] = {'vmstate', 'name'}
            args_dict: dict[str,str] = {key: (1 if value is True else 0 if value is False else value) for key, value in vars(args).items() if value is not None and key in include}
            if not args.range:
                snapshot.make_snapshot(prox, args.node, args.vmid, **args_dict)
            else:
                utils.function_over_range(snapshot.make_snapshot, args.range[0], args.range[1], prox, args.node, **args_dict)
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
    # snapshot.rollback_first_snapshot(prox, "cuci-r730-pve03", 23021) 
    # conf: dict = config.get_config("conf/box.yaml")
    # env: config.Env = config.get_env(conf)
    # # Testing
    #  #x = prox.nodes('cuci-r730-pve01').qemu('7101').clone.create(newid='28006',target='cuci-r730-pve03')
    # #print(x)
    # clone.clone_env(prox, env)
        
    