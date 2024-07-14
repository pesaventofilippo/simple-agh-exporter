import os


class EnvironmentConfig:
    def __init__(self):
        self.PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", "8000"))
        self.PROMETHEUS_PREFIX = os.getenv("PROMETHEUS_PREFIX", "agh")
        self.ADGUARD_SERVER = os.getenv("ADGUARD_SERVER", "localhost")
        self.ADGUARD_USERNAME = os.getenv("ADGUARD_USERNAME")
        self.ADGUARD_PASSWORD = os.getenv("ADGUARD_PASSWORD")


env = EnvironmentConfig()
