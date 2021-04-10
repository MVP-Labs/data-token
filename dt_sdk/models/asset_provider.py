"""Enterprize and Asset Provider"""
# Copyright 2021 The dt-web3 Authors
# SPDX-License-Identifier: LGPL-2.1-only

import logging

from dt_sdk.toolkit.contract_base import ContractBase
from dt_sdk.models.constants import ErrorCode

logger = logging.getLogger(__name__)


class AssetProvider(ContractBase):
    CONTRACT_NAME = 'AssetProvider'
    ENTERPRIZE_REGISTER_EVENT = 'EnterprizeRegistered'
    PROVIDER_ADD_EVENT = 'ProviderAdded'

    def register_enterprize(self, id, name, desc, from_wallet):
        """
        Register a new enterprize on chain by the admin.

        :param id: refers to the enterprize identifier
        :param name: refers to the enterprize name
        :param desc: refers to the enterprize description
        :param from_wallet: the system account
        :return
        """
        tx_hash = self.send_transaction(
            'registerEnterprize',
            (id, name, desc),
            from_wallet
        )

        receipt = self.get_tx_receipt(tx_hash)

        if not bool(receipt and receipt.status == 1):
            raise AssertionError(f'transaction failed with tx id {tx_hash}.')

        topic_param = self.events.EnterprizeRegistered().processReceipt(receipt)
        error_code = topic_param[0]['args']['_code']

        if error_code == ErrorCode.SUCCESS:
            logger.debug(f'sucessfully register enterprize {name} for id {id}')
        elif error_code == ErrorCode.ENTERPRIZE_EXISTS:
            raise AssertionError(f'The enterprize already exists for id {id}')
        else:
            raise AssertionError(f'ERROR_NO_PERMISSION')

    def update_enterprize(self, id, name, desc, from_wallet):
        """
        Update the enterprize on chain by the admin.

        :param id: refers to the enterprize identifier
        :param name: refers to the enterprize name
        :param desc: refers to the enterprize description
        :param from_wallet: the system account
        :return
        """
        tx_hash = self.send_transaction(
            'updateEnterprize',
            (id, name, desc),
            from_wallet
        )

        receipt = self.get_tx_receipt(tx_hash)

        if not bool(receipt and receipt.status == 1):
            raise AssertionError(f'transaction failed with tx id {tx_hash}.')

        topic_param = self.events.EnterprizeRegistered().processReceipt(receipt)
        error_code = topic_param[0]['args']['_code']

        if error_code == ErrorCode.SUCCESS:
            logger.debug(f'sucessfully update enterprize {name} for id {id}')
        elif error_code == ErrorCode.ENTERPRIZE_NOT_EXISTS:
            raise AssertionError(f'The enterprize do not exists for id {id}')
        else:
            raise AssertionError(f'ERROR_NO_PERMISSION')

    def add_provider(self, id, from_wallet):
        """
        Add a new provider on chain by the admin.

        :param id: refers to the provider identifier
        :param from_wallet: the system account
        :return
        """
        tx_hash = self.send_transaction(
            'addProvider', (id,), from_wallet
        )

        receipt = self.get_tx_receipt(tx_hash)

        if not bool(receipt and receipt.status == 1):
            raise AssertionError(f'transaction failed with tx id {tx_hash}.')

        topic_param = self.events.ProviderAdded().processReceipt(receipt)
        error_code = topic_param[0]['args']['_code']

        if error_code == ErrorCode.SUCCESS:
            logger.debug(f'sucessfully add provide for id {id}')
        elif error_code == ErrorCode.PROVIDER_EXISTS:
            raise AssertionError(f'The provider already exists for id {id}')
        else:
            raise AssertionError(f'ERROR_NO_PERMISSION')

    def update_provider(self, id, from_wallet):
        """
        Update the provider on chain by the admin.

        :param id: refers to the provider identifier
        :param from_wallet: the system account
        :return
        """
        tx_hash = self.send_transaction('updateProvider', (id,), from_wallet)

        receipt = self.get_tx_receipt(tx_hash)

        if not bool(receipt and receipt.status == 1):
            raise AssertionError(f'transaction failed with tx id {tx_hash}.')

        topic_param = self.events.ProviderAdded().processReceipt(receipt)
        error_code = topic_param[0]['args']['_code']

        if error_code == ErrorCode.SUCCESS:
            logger.debug(f'sucessfully update provide for id {id}')
        elif error_code == ErrorCode.PROVIDER_NOT_EXISTS:
            raise AssertionError(f'The provider do not exists for id {id}')
        else:
            raise AssertionError(f'ERROR_NO_PERMISSION')

    def check_enterprize(self, id):
        """
        Check enterprize role.

        :param id: refers to the enterprize identifier
        :return: bool
        """
        return self.contract_concise.isEnterprize(id)

    def check_provider(self, id):
        """
        Check provider role.

        :param id: refers to the provider identifier
        :return: bool
        """
        return self.contract_concise.isProvider(id)

    def get_enterprize(self, id):
        """
        Get the enterprize info.

        :param id: refers to the enterprize identifier
        :return: Enterprize struct
        """
        return self.contract_concise.getEnterprizebyId(id)
