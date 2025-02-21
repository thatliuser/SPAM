from proxmoxer import ProxmoxAPI
from proxmoxer.core import ResourceException
import conf.config as config
import utils
import cloudinit


def clone_vm(prox: ProxmoxAPI, source_node: str, source_id: str, **kwargs) -> None:
    try:
        task_id = prox.nodes(source_node).qemu(source_id).clone.create(**kwargs)
        target = source_node if 'target' not in kwargs else kwargs['target']
        print(f"Cloning VMID {source_id} in {source_node} to VMID {kwargs['newid']} in {target}")
        utils.block_until_done(prox, task_id, source_node)
    except Exception as e:
        print(e)
    return

def clone_env(prox: ProxmoxAPI, env: config.Env) -> None:
    newid: int = env.startid
    for node in env.nodes:
        for box in env.boxes:
            for _ in range(box.copies):
                clone_vm(prox, env.template_node, box.id, newid = newid, target=node,**box.config)
                if box.cloud:
                    cloudinit.set_cloudinit(prox, node, newid, **box.cloud)
                newid += 1
