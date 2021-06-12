"""Config module."""
# Copyright 2021 The dt-sdk Authors
# SPDX-License-Identifier: LGPL-2.1-only

import os
import logging
from os import getenv
from pathlib import Path
from configparser import ConfigParser
from datatoken.web3.web3_provider import Web3Provider

NAME_ARTIFACTS_PATH = 'artifacts_path'
NAME_ADDRESS_FILE = 'address_file'
NAME_NETWORK_URL = 'network_url'
NAME_NETWORK = 'network_name'
NAME_IPFS_ENDPOINT = 'ipfs_endpoint'

class Config(ConfigParser):
    def __init__(self, filename=None, options_dict=None):
        """
        Initialize Config class.

        :param filename: Path of the config file, str.
        :param options_dict: Python dict with the config, dict.
        """
        ConfigParser.__init__(self)

        self._keeper_section = 'keeper'
        self._logger = logging.getLogger('config')

        if not filename:
            filename = getenv('CONFIG_FILE', './config.ini')

        if not os.path.exists(filename) and not options_dict:
            raise FileNotFoundError(f'please provider the config first')

        if os.path.exists(filename):
            self._logger.debug(f'Config: loading config file {filename}')
            self.read(filename)

        if options_dict:
            self._logger.debug(f'Config: loading from dict {options_dict}')
            self.read_dict(options_dict)

    @property
    def network_url(self):
        """Get the url of the network."""
        return self.get(self._keeper_section, NAME_NETWORK_URL)

    @property
    def network_name(self):
        """get the name of the network."""
        return self.get(self._keeper_section, NAME_NETWORK)

    @property
    def ipfs_endpoint(self):
        """get the name of the network."""
        return self.get(self._keeper_section, NAME_IPFS_ENDPOINT)

    @property
    def artifacts_path(self):
        """get the contracts artifact file path."""
        path = None
        _path_string = self.get(self._keeper_section, NAME_ARTIFACTS_PATH)
        if _path_string:
            path = Path(_path_string).expanduser().resolve()

        if path and os.path.exists(path):
            return path

        if not os.path.exists(path):
            path = Path('~/.dt/artifacts').expanduser().resolve()

        return path

    @property
    def address_file(self):
        """get the contracts address file path."""
        file_path = self.get(self._keeper_section, NAME_ADDRESS_FILE)
        if file_path:
            file_path = Path(file_path).expanduser().resolve()

        if not file_path or not os.path.exists(file_path):
            file_path = os.path.join(self.artifacts_path, 'address.json')

        return file_path

    @property
    def keeper_options(self):
        """Prepare the option dict for the dt-web3 keeper."""
        return {self._keeper_section: {NAME_NETWORK_URL: self.network_url,
                                       NAME_NETWORK: self.network_name,
                                       NAME_ARTIFACTS_PATH: self.artifacts_path,
                                       NAME_ADDRESS_FILE: self.address_file}}

    @property
    def web3(self):
        """Get the web3 provider of the network."""
        return Web3Provider.get_web3(network_url=self.network_url)
