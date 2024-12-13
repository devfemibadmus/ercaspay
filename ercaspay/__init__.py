from .helper import Helper
from .payments import Payments

import os

def load_env_vars(env_file_path):
    with open(env_file_path, 'r') as file:
        for line in file:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
