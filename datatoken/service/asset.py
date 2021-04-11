"""Asset service module."""
# Copyright 2021 The dt-sdk Authors
# SPDX-License-Identifier: LGPL-2.1-only

import logging

from datatoken.asset.ddo import DDO
from datatoken.asset.dt_helper import DTHelper
from datatoken.asset.storage.ipfs_provider import IPFSProvider
from datatoken.asset.storage.asset_resolve import resolve_asset, resolve_asset_by_url
from datatoken.model.keeper import Keeper
from datatoken.service.verifier import VerifierService
from datatoken.service.tracer import TracerService

logger = logging.getLogger(__name__)


class AssetService(object):
    """The entry point for accessing the asset service."""

    def __init__(self, config):
        keeper = Keeper(config.keeper_options)

        self.dt_factory = keeper.dt_factory
        self.asset_provider = keeper.asset_provider
        self.verifier = VerifierService(config)
        self.tracer = TracerService(config)

        self.config = config

    def generate_ddo(self, metadata, services, owner_address, child_dts=None, verify=True):
        """
        Create an asset document and declare its services.

        :param metadata: refers to the asset metadata
        :param services: list of asset services
        :param owner_address: refers to the asset owner
        :param child_dts: list of child asset identifiers
        :param verify: check the correctness of asset services 
        :return ddo: DDO instance
        """
        ddo = DDO()
        ddo.add_metadata(metadata, child_dts)
        ddo.add_creator(owner_address)

        for service in services:
            ddo.add_service(service)

        ddo.assign_dt(DTHelper.generate_new_dt())
        ddo.create_proof()

        # make sure the generated ddo is under system constraits
        if verify and not self.verifier.verify_services(ddo):
            raise AssertionError(f'Service agreements are not satisfied')

        return ddo

    def publish_dt(self, ddo, issuer_wallet):
        """
        Publish a ddo to the decentralized storage network and register its 
        data token on the smart-contract chain.

        :param ddo: refers to the asset DDO document 
        :param issuer_wallet: issuer account, enterprize now
        :return
        """
        ipfs_client = IPFSProvider()
        ipfs_path = ipfs_client.add(ddo.to_dict())

        dt = DTHelper.dt_to_id(ddo.dt)
        owner = ddo.creator
        isLeaf = not bool(ddo.child_dts)
        checksum = ddo.proof['checksum']

        self.dt_factory.mint_dt(dt, owner, isLeaf, checksum,
                                ipfs_path, issuer_wallet)

        return

    def grant_dt_perm(self, dt, grantee, owner_wallet):
        """
        Grant one dt to other dt.

        :param dt: refers to data token identifier
        :param grantee: refers to granted dt identifier
        :param owner_wallet: owner account
        :return
        """
        _dt = DTHelper.dt_to_id(dt)
        _grantee = DTHelper.dt_to_id(grantee)

        self.dt_factory.grant_dt(_dt, _grantee, owner_wallet)

        return

    def activate_cdt(self, cdt, child_dts, aggregator_wallet):
        """
        Activate cdt when all perms are ready.

        :param cdt: refers to cdt identifier
        :param child_dts: associated with child_dts identifier
        :param aggregator_wallet: aggregator account
        :return
        """
        _cdt = DTHelper.dt_to_id(cdt)
        _child_dts = [DTHelper.dt_to_id(dt) for dt in child_dts]

        self.dt_factory.start_compose_dt(_cdt, _child_dts, aggregator_wallet)

        return

    def check_service_terms(self, cdt, dt, owner_address, signature):
        """
        Check service agreements automatically when receiving a remote permission 
        authorization request, used by Compute-to-Data.

        :param cdt: refers to cdt identifier provided by aggregator
        :param dt: refers to dt identifier owned by the provider grid
        :param owner_address: asset owner address
        :param signature: signed by aggregator, [consume_address, cdt]
        :return: bool
        """
        if self.verifier.check_dt_perm(dt, cdt):
            return True

        if not self.verifier.check_dt_owner(dt, owner_address):
            return False

        data, cdt_ddo = resolve_asset(cdt, self.dt_factory)
        if not data or not cdt_ddo:
            return False

        consume_address = data[1]
        original_msg = f'{consume_address}{cdt}'
        if not self.verifier.verify_signature(consume_address, signature, original_msg):
            return False

        checksum = data[2]
        if not self.verifier.verify_ddo_integrity(cdt_ddo, checksum):
            return False

        if not self.verifier.verify_services(cdt_ddo, [dt], False):
            return False

        return True

    def get_dt_marketplace(self):
        """
        Get all available dts in the marketplace.

        :return: list
        """
        dt_idx, _, issuers, checksums, _, ipfs_paths, _ = self.dt_factory.get_available_dts()

        issuer_names = self.asset_provider.get_issuer_names(issuers)

        marketplace_list = []
        for dt, issuer_name, ipfs_path, checksum in zip(dt_idx, issuer_names, ipfs_paths, checksums):
            ddo = resolve_asset_by_url(ipfs_path)

            if ddo and self.verifier.verify_ddo_integrity(ddo, checksum):
                asset_name = ddo.metadata["main"].get("name")
                asset_fig = "test"
                union_or_not = ddo.is_cdt

                marketplace_list.append(
                    (dt, issuer_name, asset_name, asset_fig, union_or_not))

        return marketplace_list

    def get_dt_details(self, dt):
        """
        Get the detailed information given a datatoken.

        :param dt: refers to dt identifier
        :return: tuple
        """
        data, ddo = resolve_asset(dt, self.dt_factory)
        if not data or not ddo:
            return None

        checksum = data[2]
        if not self.verifier.verify_ddo_integrity(ddo, checksum):
            return None

        owner = data[0]
        issuer = data[1]
        issuer_name = self.asset_provider.get_enterprise(issuer)[0]

        asset_name = ddo.metadata["main"].get("name")
        asset_desc = ddo.metadata["main"].get("desc")
        asset_type = ddo.metadata["main"].get("type")
        # asset_fig = ddo.metadata["main"].get("fig")
        asset_fig = "test"

        dt_info = (asset_name, owner, issuer_name,
                   asset_desc, asset_type, asset_fig)

        union_data = self.tracer.trace_data_union(ddo, [ddo.dt])

        service_lists = []
        for service in ddo.services:
            sid = service.index
            # op_name = service.attributes['op_name']
            op_name = "test"
            price = service.attributes['price']
            constrains = service.descriptor

            service_lists.append((sid, op_name, price, constrains))

        return (dt_info, service_lists, union_data)
