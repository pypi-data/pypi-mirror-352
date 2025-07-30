"""This module includes the configuration folder-path/credentials """
import os
import configparser

import irr_uncertainty
from pathlib import Path

ROOT = Path(irr_uncertainty.__path__[0])

DATA_PATH = ROOT / 'local_data'


class Config:
    """ Class to get credentials for BSRN and CAMS data """

    def __init__(self, path: str = (DATA_PATH / "secret.ini")):
        self.path = path
        self.config = configparser.ConfigParser()

        if os.path.exists(path):
            self.config.read(path)
        else:
            print("Config file not found")

    def bsrn(self):
        user = self.config["BSRN"]["user"]
        password = self.config["BSRN"]["password"]

        return user, password

    def cams(self):
        user = self.config["CAMS"]["user"]

        return user
