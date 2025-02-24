from proxmoxer import ProxmoxAPI
import utils

def rollback_to_snapshot(prox: ProxmoxAPI, node: str, vmid: str, snapname: str, **kwargs) -> None:
    try:
        task_id = prox.nodes(node).qemu(vmid).snapshot(snapname).rollback.post(**kwargs)
        utils.block_until_done(prox, task_id, node)
        print(f"Rolling back VMID {vmid} in {node} to {snapname} snapshot.")
    except Exception as e:
        print(e)
    return

def rollback_first_snapshot(prox: ProxmoxAPI, node: str, vmid: int, **kwargs) -> None:
    try:
        snapshots = prox.nodes(node).qemu(vmid).snapshot.get()
        first_snapshot = snapshots[0]["name"]
        task_id = prox.nodes(node).qemu(vmid).snapshot(first_snapshot).rollback.post(**kwargs)
        utils.block_until_done(prox, task_id, node)
        print(f"Rolling back VMID {vmid} in {node} to {first_snapshot} snapshot.")
    except Exception as e:
        print(e)
    return

def rollback_first_snapshot_range(prox: ProxmoxAPI, node: str, first: int, last: int, **kwargs) -> None:
    for vmid in range(first, last + 1):
        rollback_first_snapshot(prox, node, vmid, **kwargs)
    return