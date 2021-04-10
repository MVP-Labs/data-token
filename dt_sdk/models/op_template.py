"""Trusted Operation Template"""
# Copyright 2021 The dt-web3 Authors
# SPDX-License-Identifier: LGPL-2.1-only

import logging

from dt_sdk.toolkit.contract_base import ContractBase
from dt_sdk.models.constants import ErrorCode

logger = logging.getLogger(__name__)


class OpTemplate(ContractBase):
    CONTRACT_NAME = 'OpTemplate'
    TEMPLATE_PUBLISH_EVENT = 'TemplatePublished'

    def publish_template(self, tid, name, checksum, ipfs_path, from_wallet):
        """
        Publish an off-chain code template on chain.

        :param tid: refers to the op template identifier
        :param name: refers to the op template name
        :param checksum: checksum associated with tid/metadata
        :param ipfs_path: referes to the metadata storage path
        :param from_wallet: publisher account
        :return
        """
        tx_hash = self.send_transaction(
            'publishTemplate',
            (tid, name, checksum, ipfs_path),
            from_wallet
        )

        receipt = self.get_tx_receipt(tx_hash)

        if not bool(receipt and receipt.status == 1):
            raise AssertionError(f'transaction failed with tx id {tx_hash}.')

        topic_param = self.events.TemplatePublished().processReceipt(receipt)
        error_code = topic_param[0]['args']['_code']

        if error_code == ErrorCode.SUCCESS:
            logger.debug(
                f'sucessfully publish op template {name} for tid {tid}')
        elif error_code == ErrorCode.TEMPLATE_EXISTS:
            raise AssertionError(f'The template already exists for tid {tid}')
        else:
            raise AssertionError(f'ERROR_NO_PERMISSION')

    def update_template(self, tid, name, checksum, ipfs_path, from_wallet):
        """
        Update the op template that is already exists on chain.

        :param tid: refers to the op template identifier
        :param name: refers to the op template name
        :param checksum: checksum associated with tid/metadata
        :param ipfs_path: referes to the metadata storage path
        :param from_wallet: publisher account
        :return
        """
        tx_hash = self.send_transaction(
            'updateTemplate',
            (tid, name, checksum, ipfs_path),
            from_wallet
        )

        receipt = self.get_tx_receipt(tx_hash)

        if not bool(receipt and receipt.status == 1):
            raise AssertionError(f'transaction failed with tx id {tx_hash}.')

        topic_param = self.events.TemplatePublished().processReceipt(receipt)
        error_code = topic_param[0]['args']['_code']

        if error_code == ErrorCode.SUCCESS:
            logger.debug(
                f'sucessfully update op template {name} for tid {tid}')
        elif error_code == ErrorCode.TEMPLATE_NOT_EXISTS:
            raise AssertionError(f'The template not exists for tid {tid}')
        else:
            raise AssertionError(f'ERROR_NO_PERMISSION')

    def is_template_exist(self, tid):
        """
        Check template existence.

        :param tid: refers to the address identifier
        :return: bool
        """
        return self.contract_concise.isTemplateExist(tid)

    def get_template(self, tid):
        """
        Get the template records by id.

        :param tid: refers to the address identifier
        :return: Template struct
        """
        return self.contract_concise.getTemplateById(tid)

    def blockNumberUpdated(self, tid):
        """
        Get the blockUpdated for a template.

        :param tid: refers to the address identifier
        :return: int blockUpdated
        """
        return self.contract_concise.getBlockNumberUpdated(tid)

    def get_template_num(self):
        """
        Get the total numbers of op templates.

        :return: int
        """
        return self.contract_concise.getTemplateNum()
