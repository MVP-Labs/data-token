"""Enterprise and Asset Provider"""
# Copyright 2021 The dt-web3 Authors
# SPDX-License-Identifier: LGPL-2.1-only

import logging

from dt_sdk.toolkit.contract_base import ContractBase
from dt_sdk.models.constants import ErrorCode

logger = logging.getLogger(__name__)


class AssetProvider(ContractBase):
    CONTRACT_NAME = 'AssetProvider'
    ENTERPRIZE_REGISTER_EVENT = 'EnterpriseRegistered'
    PROVIDER_ADD_EVENT = 'ProviderAdded'

    def register_enterprise(self, id, name, desc, from_wallet):
        """
        Register a new enterprise on chain by the admin.

        :param id: refers to the enterprise identifier
        :param name: refers to the enterprise name
        :param desc: refers to the enterprise description
        :param from_wallet: the system account
        :return
        """
        tx_hash = self.send_transaction(
            'registerEnterprise',
            (id, name, desc),
            from_wallet
        )

        receipt = self.get_tx_receipt(tx_hash)

        if not bool(receipt and receipt.status == 1):
            raise AssertionError(f'transaction failed with tx id {tx_hash}.')

        topic_param = self.events.EnterpriseRegistered().processReceipt(receipt)
        error_code = topic_param[0]['args']['_code']

        if error_code == ErrorCode.SUCCESS:
            logger.debug(f'sucessfully register enterprise {name} for id {id}')
        elif error_code == ErrorCode.ENTERPRISE_EXISTS:
            raise AssertionError(f'The enterprise already exists for id {id}')
        else:
            raise AssertionError(f'ERROR_NO_PERMISSION')

    def update_enterprise(self, id, name, desc, from_wallet):
        """
        Update the enterprise on chain by the admin.

        :param id: refers to the enterprise identifier
        :param name: refers to the enterprise name
        :param desc: refers to the enterprise description
        :param from_wallet: the system account
        :return
        """
        tx_hash = self.send_transaction(
            'updateEnterprise',
            (id, name, desc),
            from_wallet
        )

        receipt = self.get_tx_receipt(tx_hash)

        if not bool(receipt and receipt.status == 1):
            raise AssertionError(f'transaction failed with tx id {tx_hash}.')

        topic_param = self.events.EnterpriseRegistered().processReceipt(receipt)
        error_code = topic_param[0]['args']['_code']

        if error_code == ErrorCode.SUCCESS:
            logger.debug(f'sucessfully update enterprise {name} for id {id}')
        elif error_code == ErrorCode.ENTERPRISE_NOT_EXISTS:
            raise AssertionError(f'The enterprise do not exists for id {id}')
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

    def check_enterprise(self, id):
        """
        Check enterprise role.

        :param id: refers to the enterprise identifier
        :return: bool
        """
        return self.contract_concise.isEnterprise(id)

    def check_provider(self, id):
        """
        Check provider role.

        :param id: refers to the provider identifier
        :return: bool
        """
        return self.contract_concise.isProvider(id)

    def get_enterprise(self, id):
        """
        Get the enterprise info.

        :param id: refers to the enterprise identifier
        :return: Enterprise struct
        """
        return self.contract_concise.getEnterprisebyId(id)

    def get_issuer_names(self, idx):
        """
        Get the list of names of issuer enterprises.

        :return: string[]
        """
        return self.contract_concise.getIssuerNames(idx)
