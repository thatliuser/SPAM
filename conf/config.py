import yaml
class Box:
    def __init__(self, box):
        self.config = box['config']
        self.id = box['id']
        self.copies = int(box['copies'])
        self.cloud = box['cloud']

class Env:
    def __init__(self, env: dict):
        self.startid = int(env['startid'])
        self.template_node = env['template_node']
        self.nodes = env['nodes']
        self.boxes = [Box(box) for box in env['boxes']]

def get_config(path: str) -> dict:
    with open(path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def get_env(config: dict) -> Env:
    return Env(config["env"])




if __name__ == "__main__":
    config = get_config('./box.yaml')
    print(config['env'])
