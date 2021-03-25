from config import read_config
from rival_regions_wrapper import LocalAuthentication, AuthenticationHandler, ApiWrapper
from rival_regions_wrapper.api_wrapper import Overview


class Client:
    def __init__(self, settings):
        self.config = settings.config
        middleware = LocalAuthentication(
            self.config["USERNAME"],
            self.config["PASSWORD"],
            self.config["LOGIN_METHOD"]
        )

        middleware.client = AuthenticationHandler()
        middleware.client.set_credentials({
            'username': self.config["USERNAME"],
            'password': self.config["PASSWORD"],
            'login_method': self.config["LOGIN_METHOD"]
        })

        self.middleware = middleware
        self.api_wrapper = ApiWrapper(middleware)
        self.details = self.details()

    def details(self):
        self.details = Overview(self.api_wrapper).status()
        return self.details
