import yaml


class YmlConfigProvider:
    def __init__(self, path):
        self.path = path

    def get_config(self):
        with open(self.path, 'r') as file:
            return yaml.load(file, Loader=yaml.FullLoader)
