from proxmoxer import ProxmoxAPI
from dotenv import load_dotenv
import clone
import os
import conf.config as config


if __name__ == "__main__":
    load_dotenv()
    PROXMOX_HOST = os.getenv('PROXMOX_HOST')
    PROXMOX_USER = os.getenv('PROXMOX_USER')
    PROXMOX_PASSWORD = os.getenv('PROXMOX_PASSWORD')
    PROXMOX_REALM = os.getenv('PROXMOX_REALM')
    prox = ProxmoxAPI(PROXMOX_HOST, user=f'{PROXMOX_USER}@{PROXMOX_REALM}', password=PROXMOX_PASSWORD, verify_ssl=False)
    conf: dict = config.get_config("conf/box.yaml")
    env: config.Env = config.get_env(conf)
    # Testing
     #x = prox.nodes('cuci-r730-pve01').qemu('7101').clone.create(newid='28006',target='cuci-r730-pve03')
    #print(x)
    clone.clone_env(prox, env)
        
    