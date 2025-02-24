from proxmoxer import ProxmoxAPI
import utils

def start_vm(prox: ProxmoxAPI, node: str, vmid: str) -> None:
    try:
        task_id = prox.nodes(node).qemu(vmid).status.start.post()
        utils.block_until_done(prox, task_id, node)
        print(f"Starting VMID {vmid} in {node}")
    except Exception as e:
        print(e)
    return

def start_vm_range(prox: ProxmoxAPI, node: str, first: int, last: int) -> None:

    for vmid in range(first, last + 1):
        start_vm(prox, node, vmid)
    return

def stop_vm(prox: ProxmoxAPI, node: str, vmid: str) -> None:
    try:
        task_id = prox.nodes(node).qemu(vmid).status.stop.post()
        utils.block_until_done(prox, task_id, node)
        print(f"Stopping VMID {vmid} in {node}")
    except Exception as e:
        print(e)
    return

def stop_vm_range(prox: ProxmoxAPI, node: str, first: int, last: int) -> None:

    for vmid in range(first, last + 1):
        stop_vm(prox, node, vmid)
    return