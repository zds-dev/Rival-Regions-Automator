import os
import json


CONFIG_STRING = {
    'USERNAME':'usernamehere',
    'PASSWORD':'passwordhere',
    'LOGIN_METHOD':'g/v/f'
}

def read_config(CONFIG):
    if os.path.exists(CONFIG):
        with open(CONFIG, "r") as fp:
            config = json.load(fp)

    else:
        with open(CONFIG, "w") as fp:
            json.dump(CONFIG_STRING,fp)
        return False

    return config
