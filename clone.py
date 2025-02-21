from proxmoxer import ProxmoxAPI
import conf.config as config
import utils
import cloudinit

def clone_vm(prox: ProxmoxAPI, source_node: str, source_id: str, **kwargs) -> None:
    print(f"Cloning VMID {source_id} in {source_node} to VMID {kwargs['newid']} in {kwargs['target']}")
    task_id = prox.nodes(source_node).qemu(source_id).clone.create(**kwargs)
    utils.block_until_done(prox, task_id, source_node)
    return

def clone_env(prox: ProxmoxAPI, env: config.Env) -> None:
    newid: int = env.startid
    for node in env.nodes:
        for box in env.boxes:
            for _ in range(box.copies):
                clone_vm(prox, env.template_node, box.id, newid = newid, target=node, **box.config)
                if box.cloud:
                    cloudinit.set_cloudinit(prox, node, newid, **box.cloud)
                newid += 1

# prox.nodes('cuci-r730-pve01').qemu('7101').clone.create(newid='28006',target='cuci-r730-pve03')