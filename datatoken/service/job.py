"""Job service module."""
# Copyright 2021 The DataToken Authors
# SPDX-License-Identifier: LGPL-2.1-only

import logging

from datatoken.core.dt_helper import DTHelper
from datatoken.store.asset_resolve import resolve_asset, resolve_op
from datatoken.model.keeper import Keeper
from datatoken.service.verifier import VerifierService

logger = logging.getLogger(__name__)


class JobService():
    """The entry point for accessing the job service."""

    def __init__(self, config):
        keeper = Keeper(config.keeper_options)

        self.dt_factory = keeper.dt_factory
        self.op_template = keeper.op_template
        self.task_market = keeper.task_market
        self.verifier = VerifierService(config)

        self.config = config

    def create_task(self, name, desc, demander_wallet):
        """
        Add a new task on chain.

        :param name: refers to the task name
        :param desc: refers to the task description
        :param demander_wallet: demander account
        :return: int task_id
        """
        task_id = self.task_market.create_task(name, desc, demander_wallet)
        return task_id

    def add_job(self, task_id, cdt, solver_wallet):
        """
        Create a new job on chain with the algorithm cdt.

        :param cdt: refers to the algorithm composable data token
        :param task_id: refers to the task id that be solved
        :param from_wallet: solver account
        :return: int job_id
        """
        _id = DTHelper.dt_to_id(cdt)
        job_id = self.task_market.add_job(_id, task_id, solver_wallet)
        return job_id

    def check_remote_compute(self, cdt, dt, job_id, owner_address, signature):
        """
        Check job status and resource permissions automatically when receiving an 
        on-premise computation request, used by Compute-to-Data.

        :param cdt: refers to cdt identifier provided by solver
        :param dt: refers to dt identifier owned by the provider grid
        :param job_id: refers to job identifier in the task market
        :param owner_address: asset owner address
        :param signature: signed by solver, [solver_address, job_id]
        :return: bool
        """
        if not self.verifier.verify_job_registered(job_id, cdt):
            return False

        if not self.verifier.check_dt_owner(dt, owner_address):
            return False

        data, cdt_ddo = resolve_asset(cdt, self.dt_factory)
        if not data or not cdt_ddo:
            return False

        if not self.verifier.check_asset_type(cdt_ddo, 'Algorithm'):
            return False

        solver_address = data[1]
        checksum = data[2]

        original_msg = f'{solver_address}{job_id}'
        if not self.verifier.verify_signature(solver_address, signature, original_msg):
            return False

        if not self.verifier.verify_ddo_integrity(cdt_ddo, checksum):
            return False

        if not self.verifier.verify_perms_ready(cdt_ddo, required_dt=dt):
            return False

        return True

    def fetch_exec_code(self, cdt, leaf_dt):
        """
        Get the code template and its fulfiled arguments, given a father cdt and a 
        leaf dt. The father ddo specifies which child service/template to use.

        :param cdt: father composable data token
        :param leaf_dt: child data token, must be leaf
        :return: bool
        """
        _, cdt_ddo = resolve_asset(cdt, self.dt_factory)
        _, dt_ddo = resolve_asset(leaf_dt, self.dt_factory)

        fulfilled = cdt_ddo.services[0].descriptor['workflow'].get(leaf_dt)

        if not fulfilled:
            return None, None

        sid = fulfilled.get('service')
        args = fulfilled.get('constraint')

        tid = dt_ddo.get_service_by_index(sid).descriptor['template']

        _, op = resolve_op(tid, self.op_template)

        return op.operation, args
