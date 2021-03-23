from config import read_config
from rival_regions_wrapper import LocalAuthentication, AuthenticationHandler, ApiWrapper

class Client:
    def __init__(self, config_file='config.json'):
        self.config = read_config(config_file)
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
        # self.overview = Overview(self.api_wrapper)
        # self.profile = Profile(self.api_wrapper,
        #                       self.overview.status()['profile_id'])
        # self.info = self.profile.info()