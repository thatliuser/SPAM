from proxmoxer import ProxmoxAPI

def block_until_done(prox: ProxmoxAPI, task_id: str, node: str) -> None:
    data = {"status": ""}
    while (data["status"] != "stopped"):
        data = prox.nodes(node).tasks(task_id).status.get()
    return

def function_over_range(func: callable, first: int, last: int, *args, **kwargs):
    for vmid in range(first, last + 1):
        func(*args, **kwargs, vmid=vmid)
    return
