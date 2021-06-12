"""Verifier service module."""
# Copyright 2021 The DataToken Authors
# SPDX-License-Identifier: LGPL-2.1-only

import logging

from eth_utils import remove_0x_prefix
from datatoken.core.dt_helper import DTHelper
from datatoken.core.utils import convert_to_string
from datatoken.store.asset_resolve import resolve_asset, resolve_op
from datatoken.csp.agreement import validate_leaf_template, validate_service_agreement
from datatoken.model.keeper import Keeper
from datatoken.model.constants import Role
from datatoken.web3.utils import personal_ec_recover

logger = logging.getLogger(__name__)


class VerifierService(object):
    """The entry point for accessing the verifier service."""

    def __init__(self, config):
        keeper = Keeper(config.keeper_options)

        self.role_controller = keeper.role_controller
        self.asset_provider = keeper.asset_provider
        self.op_template = keeper.op_template
        self.dt_factory = keeper.dt_factory
        self.task_market = keeper.task_market

        self.config = config

    def check_admin(self, address):
        """Check Admin role for a given address."""
        return self.role_controller.check_role(address, Role.ROLE_ADMIN)

    def check_enterprise(self, id):
        """Check Enterprize role for a given address."""
        return self.asset_provider.check_enterprise(id)

    def check_provider(self, id):
        """Check Provider role for a given address."""
        return self.asset_provider.check_provider(id)

    def check_op_exist(self, tid):
        """Check template existence."""
        _tid = DTHelper.dt_to_id(tid)
        return self.op_template.is_template_exist(_tid)

    def check_dt_owner(self, dt, owner_address):
        """Check dt owner."""
        _dt = DTHelper.dt_to_id(dt)
        return self.dt_factory.get_dt_owner(_dt) == owner_address

    def check_dt_available(self, dt):
        """Check dt availability."""
        _dt = DTHelper.dt_to_id(dt)
        return self.dt_factory.check_dt_available(_dt)

    def check_cdt_composed(self, cdt):
        """Check cdt composability."""
        _cdt = DTHelper.dt_to_id(cdt)
        return self.dt_factory.check_cdt_available(_cdt)

    def check_dt_perm(self, dt, grantee):
        """Check granted permission."""
        _dt = DTHelper.dt_to_id(dt)
        _grantee = DTHelper.dt_to_id(grantee)
        return self.dt_factory.check_dt_perm(_dt, _grantee)

    def check_asset_type(self, ddo, asset_type):
        """Check asset type for a given ddo."""
        return ddo.asset_type == asset_type

    def verify_signature(self, signer_address, signature, original_msg):
        """Check the given address has signed on the given data"""
        address = personal_ec_recover(original_msg, signature)
        return address.lower() == signer_address.lower()

    def verify_ddo_integrity(self, ddo, checksum_evidence):
        """Check the equallty of the ddo checksum and its on-chain evidence."""
        checksum_evidence = remove_0x_prefix(
            convert_to_string(checksum_evidence))
        return ddo.proof['checksum'] == checksum_evidence

    def verify_services(self, ddo, wrt_dts=None, integrity_check=True):
        """ 
        Ensure the service constraints are fulfilled. For a given leaf ddo, we check 
        the parameter consistency of its constraints and used templates. For a given 
        composable ddo, we first check the availability of its childs, and then check 
        the fulfilled constraints for each workflow service.

        :param ddo: a candidate DDO object, composable or leaf
        :param wrt_dts: a list of dts to be fulfilled, all child dts if None
        :param integrity_check: verify child ddo integrity if True
        :return: bool
        """
        if not ddo.is_cdt:
            return validate_leaf_template(ddo, self.op_template)

        if not wrt_dts:
            wrt_dts = ddo.child_dts

        for dt in wrt_dts:
            data, child_ddo = resolve_asset(dt, self.dt_factory)
            if not data or not child_ddo:
                return False

            if integrity_check and not self.verify_ddo_integrity(child_ddo, data[2]):
                return False

            if not child_ddo.is_cdt:
                if not validate_leaf_template(child_ddo, self.op_template):
                    return False
            else:
                if not self.check_cdt_composed(child_ddo.dt) or (
                        not self.verify_perms_ready(child_ddo)):
                    return False

            if not validate_service_agreement(ddo, child_ddo):
                return False

        return True

    def verify_job_registered(self, job_id, cdt):
        """Ensure the cdt is submitted to the market with a given job id."""
        job = self.task_market.get_job(job_id)
        if not (job and job[2]):
            return False

        return DTHelper.dt_to_id_bytes(cdt) == job[2]

    def verify_perms_ready(self, cdt_ddo, required_dt=None):
        """ 
        Ensure the given cdt has got all child permissions.

        :param cdt_ddo: DDO object for a cdt, previously activated on chain
        :param required_dt: dt identifier required to be the cdt child
        :return: bool
        """
        child_dts = []
        found = False

        for dt in cdt_ddo.child_dts:
            child_dts.append(DTHelper.dt_to_id(dt))
            if dt == required_dt:
                found = True

        if required_dt and found == False:
            return False

        _cdt = DTHelper.dt_to_id(cdt_ddo.dt)

        return self.dt_factory.check_clinks(_cdt, child_dts)
