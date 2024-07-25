from .yml_config_provider import YmlConfigProvider


def get_default_config_provider():
    return YmlConfigProvider("./config.yml")
