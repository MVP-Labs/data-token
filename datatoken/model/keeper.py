"""Keeper module."""
# Copyright 2021 The DataToken Authors
# SPDX-License-Identifier: LGPL-2.1-only

import os
import logging
from os import getenv
from configparser import ConfigParser

from datatoken.web3.contract_handler import ContractHandler
from datatoken.web3.web3_provider import Web3Provider
from datatoken.model.role_controller import RoleController
from datatoken.model.asset_provider import AssetProvider
from datatoken.model.op_template import OpTemplate
from datatoken.model.dt_factory import DTFactory
from datatoken.model.task_market import TaskMarket

logger = logging.getLogger('datatoken')


class Keeper:
    """The entry point for accessing datatoken contracts."""

    def __init__(self, options_dict=None):

        filename = getenv('CONFIG_FILE', './config.ini')
        if not os.path.exists(filename) and not options_dict:
            raise FileNotFoundError(f'please provider the config first')

        config_parser = ConfigParser()
        if os.path.exists(filename):
            config_parser.read(filename)
        if options_dict:
            config_parser.read_dict(options_dict)

        artifacts_path = config_parser.get('keeper', 'artifacts_path')
        network_url = config_parser.get('keeper', 'network_url')
        network_name = config_parser.get('keeper', 'network_name')
        address_file = config_parser.get('keeper', 'address_file')

        ContractHandler.set_artifacts_path(artifacts_path)
        addresses = ContractHandler.get_contracts_addresses(
            network_name, address_file)

        self._web3 = Web3Provider.get_web3(network_url=network_url)

        self.role_controller = RoleController(
            addresses.get(RoleController.CONTRACT_NAME))
        self.asset_provider = AssetProvider(
            addresses.get(AssetProvider.CONTRACT_NAME))
        self.op_template = OpTemplate(addresses.get(OpTemplate.CONTRACT_NAME))
        self.dt_factory = DTFactory(addresses.get(DTFactory.CONTRACT_NAME))
        self.task_market = TaskMarket(addresses.get(TaskMarket.CONTRACT_NAME))

        logger.debug('Keeper instance initialized: ')

    @property
    def web3(self):
        return self._web3
