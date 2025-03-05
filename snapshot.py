from proxmoxer import ProxmoxAPI
import utils

def rollback_snapshot(prox: ProxmoxAPI, node: str, snapname: str = "", vmid: int = -1, **kwargs) -> None:
    try:
        if snapname == "":
            snapshots = prox.nodes(node).qemu(vmid).snapshot.get()
            snapname = snapshots[0]["name"]
        task_id = prox.nodes(node).qemu(vmid).snapshot(snapname).rollback.post(**kwargs)
        utils.block_until_done(prox, task_id, node)
        print(f"Rolling back VMID {vmid} in {node} to {snapname} snapshot.")
    except Exception as e:
        print(e)
    return


def make_snapshot(prox: ProxmoxAPI, node: str, snapname: str = "base", vmid: int = -1, **kwargs):
    try:
        task_id = prox.nodes(node).qemu(vmid).snapshot.post(snapname=snapname,**kwargs)
        utils.block_until_done(prox, task_id, node)
        print(f"Snapshotting VMID {vmid} in {node} as {snapname} snapshot.")
    except Exception as e:
        print(e)
    return
