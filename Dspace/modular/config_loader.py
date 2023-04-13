import yaml

class ConfigLoader:

    def __init__(self, filename):
        self.config = self.load_config(filename)

    def load_config(self, filename):
        try:
            with open(filename, 'r') as file:
                config = yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Could not find {filename}.")
            return {}

        return config

    def get(self, key, default=None):
        return self.config.get(key, default)
