"""System service module."""
# Copyright 2021 The DataToken Authors
# SPDX-License-Identifier: LGPL-2.1-only

import logging

from datatoken.core.operator import OpTemplate
from datatoken.core.dt_helper import DTHelper
from datatoken.store.ipfs_provider import IPFSProvider
from datatoken.model.keeper import Keeper
from datatoken.model.constants import Role
from datatoken.service.verifier import VerifierService

logger = logging.getLogger(__name__)


class SystemService:
    """The entry point for accessing the system service."""

    def __init__(self, config):
        keeper = Keeper(config.keeper_options)

        self.asset_provider = keeper.asset_provider
        self.op_template = keeper.op_template
        self.verifier = VerifierService(config)

        self.config = config

    def register_enterprise(self, address, name, desc, from_wallet):
        """
        Register a new enterprise on-chain.

        :param address: refers to the enterprise address
        :param name: refers to the enterprise name
        :param desc: refers to the enterprise description
        :param from_wallet: the system account
        :return
        """
        if not self.verifier.check_enterprise(address):
            self.asset_provider.register_enterprise(
                address, name, desc, from_wallet)
        else:
            self.asset_provider.update_enterprise(
                address, name, desc, from_wallet)

        return

    def add_provider(self, address, from_wallet):
        """
        Add a new provider on-chain.

        :param address: refers to the provider address
        :param from_wallet: the system account
        :return
        """
        if not self.verifier.check_provider(address):
            self.asset_provider.add_provider(address, from_wallet)
        else:
            self.asset_provider.update_provider(address, from_wallet)

        return

    def publish_template(self, metadata, operation, params, from_wallet):
        """
        Publish the op template on chain.

        :param metadata: refers to the template metadata
        :param operation: refers to the code template
        :param params: refers to the code parameters
        :param from_wallet: the system account
        :return
        """
        op = OpTemplate()

        op.add_metadata(metadata)
        op.add_template(operation, params)
        op.add_creator(from_wallet.address)
        op.assign_tid(DTHelper.generate_new_dt())
        op.create_proof()

        ipfs_client = IPFSProvider(self.config)
        ipfs_path = ipfs_client.add(op.to_dict())

        tid = DTHelper.dt_to_id(op.tid)
        name = metadata['main']['name']
        checksum = op.proof['checksum']

        if not self.verifier.check_op_exist(op.tid):
            self.op_template.publish_template(
                tid, name, checksum, ipfs_path, from_wallet)
        else:
            self.op_template.update_template(
                tid, name, checksum, ipfs_path, from_wallet)

        return op
