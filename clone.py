from proxmoxer import ProxmoxAPI
from proxmoxer.core import ResourceException
import conf.config as config
import utils
import utils.cloudinit as cloudinit


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
            name = box.config['name'] 
            for i in range(box.copies):
                ipconfig = f"ip=10.111.1.{i+1}/8,gw=10.0.0.1"
                box.config['name'] = f"{name}-{i+1}"
                clone_vm(prox, env.template_node, box.id, newid = newid, target=node,**box.config)
                if box.cloud:
                    cloudinit.set_cloudinit(prox, node, newid, **box.cloud, ipconfig0=ipconfig)
                newid += 1
