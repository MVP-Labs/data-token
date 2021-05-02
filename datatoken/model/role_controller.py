"""Role Controller"""
# Copyright 2021 The dt-web3 Authors
# SPDX-License-Identifier: LGPL-2.1-only

import logging

from datatoken.web3.contract_base import ContractBase
from datatoken.model.constants import ErrorCode

logger = logging.getLogger(__name__)


class RoleController(ContractBase):
    CONTRACT_NAME = 'RoleController'
    ROLE_ADD_EVENT = 'RoleAdded'

    def check_role(self, id, role):
        """
        Check role for a given address.

        :param id: refers to address identifier
        :param role: refers to the certain role
        :return: bool
        """
        return self.contract_concise.checkRole(id, role)

    def check_permission(self, id, operation):
        """
        Check operation permission for a given address.

        :param id: refers to address identifier
        :param operation: refers to the certain operation
        :return: bool
        """
        return self.contract_concise.checkPermission(id, operation)

    def add_role(self, id, role, from_wallet):
        """
        Add a role for given id.

        :param id: refers to address identifier
        :param role: refers to the certain role
        :return
        """
        tx_hash = self.send_transaction(
            'addRole',
            (id, role),
            from_wallet
        )

        receipt = self.get_tx_receipt(tx_hash)

        if not bool(receipt and receipt.status == 1):
            raise AssertionError(f'transaction failed with tx id {tx_hash}.')

        topic_param = self.events.RoleAdded().processReceipt(receipt)
        error_code = topic_param[0]['args']['_code']

        if error_code == ErrorCode.SUCCESS:
            logger.debug(f'sucessfully add role {role} for id {id}')
        elif error_code == ErrorCode.ROLE_EXISTS:
            raise AssertionError(f'The role {role} already exists for id {id}')
        else:
            raise AssertionError(f'ERROR_NO_PERMISSION')
