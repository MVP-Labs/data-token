"""Data Token Factory"""
# Copyright 2021 The dt-web3 Authors
# SPDX-License-Identifier: LGPL-2.1-only

import logging

from datatoken.model.web3_toolkit.contract_base import ContractBase
from datatoken.model.web3_toolkit.event_filter import EventFilter
from datatoken.model.constants import ErrorCode

logger = logging.getLogger(__name__)


class DTFactory(ContractBase):
    CONTRACT_NAME = 'DTFactory'
    DT_MINT_EVENT = 'DataTokenMinted'
    DT_GRANT_EVENT = 'DataTokenGranted'
    CDT_MINT_EVENT = 'CDTMinted'

    def mint_dt(self, dt, owner, is_leaf, checksum, ipfs_path, from_wallet):
        """
        Create new data token on chain.

        :param dt: refers to data token identifier
        :param owner: refers to data token owner
        :param is_leaf: leaf dt or composable dt
        :param checksum: checksum associated with dt/metadata
        :param ipfs_path: refers to the metadata storage path
        :param from_wallet: issuer account
        :return
        """
        tx_hash = self.send_transaction(
            'mintDataToken',
            (dt, owner, is_leaf, checksum, ipfs_path),
            from_wallet
        )

        receipt = self.get_tx_receipt(tx_hash)

        if not bool(receipt and receipt.status == 1):
            raise AssertionError(f'transaction failed with tx id {tx_hash}.')

        topic_param = self.events.DataTokenMinted().processReceipt(receipt)
        error_code = topic_param[0]['args']['_code']

        if error_code == ErrorCode.SUCCESS:
            logger.debug(f'sucessfully mint data token for dt {dt}')
        elif error_code == ErrorCode.DT_EXISTS:
            logger.warning(f'The data token already exists for dt {dt}')
        else:
            raise AssertionError(f'ERROR_NO_PERMISSION')

    def start_compose_dt(self, cdt, child_dts, from_wallet):
        """
        Activate cdt when all perms are ready.

        :param cdt: refers to cdt identifier
        :param child_dts: associated with child_dts identifier
        :param from_wallet: aggregator account
        :return
        """
        tx_hash = self.send_transaction(
            'startComposeDT',
            (cdt, child_dts),
            from_wallet
        )

        receipt = self.get_tx_receipt(tx_hash)

        if not bool(receipt and receipt.status == 1):
            raise AssertionError(f'transaction failed with tx id {tx_hash}.')

        topic_param = self.events.CDTMinted().processReceipt(receipt)
        error_code = topic_param[0]['args']['_code']

        if error_code == ErrorCode.SUCCESS:
            logger.debug(
                f'sucessfully mint composable data token for cdt {cdt}')
        elif error_code == ErrorCode.CDT_EXISTS:
            logger.warning(
                f'The composable data token already exists for cdt {cdt}')
        else:
            raise AssertionError(f'ERROR_NO_PERMISSION')

    def grant_dt(self, dt, grantee, from_wallet):
        """
        Grant one dt to other dt.

        :param dt: refers to data token identifier
        :param grantee: refers to granted dt identifier
        :param from_wallet: owner account
        :return
        """
        tx_hash = self.send_transaction(
            'grantPermission',
            (dt, grantee),
            from_wallet
        )

        receipt = self.get_tx_receipt(tx_hash)

        if not bool(receipt and receipt.status == 1):
            raise AssertionError(f'transaction failed with tx id {tx_hash}.')

        topic_param = self.events.DataTokenGranted().processReceipt(receipt)
        error_code = topic_param[0]['args']['_code']

        if error_code == ErrorCode.SUCCESS:
            logger.debug(
                f'sucessfully grant permission for pair of dt {dt} and cdt {grantee} ')
        elif error_code == ErrorCode.DT_GRATED:
            logger.warning(f'The permission already granted')
        elif error_code == ErrorCode.DT_NOT_EXISTS:
            raise AssertionError(f'error, some dt assets are not found')
        elif error_code == ErrorCode.CDT_NOT_EXISTS:
            raise AssertionError(f'error, some cdt assets are not found')
        else:
            raise AssertionError(f'ERROR_NO_PERMISSION')

    def check_dt_available(self, dt):
        """
        Get dt availability.

        :param dt: refers to the dt identifier
        :return: bool
        """
        return self.contract_concise.isDTAvailable(dt)

    def check_cdt_available(self, cdt):
        """
        Get cdt availability.

        :param cdt: refers to the cdt identifier
        :return: bool
        """
        return self.contract_concise.isCDTAvailable(cdt)

    def check_dt_perm(self, dt, grantee):
        """
        Check permission.

        :param dt: refers to data token identifier
        :param grantee: refers to granted dt identifier
        :return: bool
        """
        return self.contract_concise.getPermission(dt, grantee)

    def get_dt_owner(self, dt):
        """
        Get the owner for a data token.

        :param dt: refers to data token identifier
        :return: owner address
        """
        return self.contract_concise.getDTOwner(dt)

    def get_dt_register(self, dt):
        """
        Get the dt records.

        :param dt: refers to data token identifier
        :return: DataToken struct
        """
        return self.contract_concise.getDTRegister(dt)

    def blockNumberUpdated(self, dt):
        """
        Get the blockUpdated for a dt

        :param dt: refers to data token identifier
        :return: int blockUpdated
        """
        return self.contract_concise.getBlockNumberUpdated(dt)

    def check_clinks(self, cdt, child_dts):
        """
        Check permission for related parties of a Composable DT.

        :param cdt: refers to cdt identifier
        :param child_dts: refers to child_dts identifiers
        :return: bool
        """
        return self.contract_concise.CLinksCheck(cdt, child_dts)

    def get_dt_num(self):
        """
        Get the total numbers of datatokens.

        :return: int
        """
        return self.contract_concise.getDTNum()

    def get_available_dts(self):
        """
        Get all the available datatokens.

        :return: DataToken[]
        """
        return self.contract_concise.getDTMap()

    ######################
    def get_owner_assets(self, address):
        """
        Get all assets for a given owner.

        :param address: refers to owner address
        :return: List Datatoken
        """
        _filters = {'_owner': address, '_code': ErrorCode.SUCCESS}

        block_filter = EventFilter(
            DTFactory.DT_MINT_EVENT,
            getattr(self.events, DTFactory.DT_MINT_EVENT),
            from_block=0,
            to_block='latest',
            argument_filters=_filters
        )

        log_items = block_filter.get_all_entries(max_tries=5)
        dt_list = []
        for log_i in log_items:
            dt_list.append(log_i.args['_dt'])

        return dt_list

    def get_dt_grantees(self, dt):
        """
        Get the granteed father for a dt.

        :param dt: refers to the data token identifier
        :return: List granteed dts
        """
        _filters = {'_dt': dt, '_code': ErrorCode.SUCCESS}

        block_filter = EventFilter(
            DTFactory.DT_GRANT_EVENT,
            getattr(self.events, DTFactory.DT_GRANT_EVENT),
            from_block=0,
            to_block='latest',
            argument_filters=_filters
        )

        log_items = block_filter.get_all_entries(max_tries=5)
        grantee_list = []
        for log_i in log_items:
            grantee_list.append(log_i.args['_grantee'])

        return grantee_list
