"""Task Market for Data Collaboration"""
# Copyright 2021 The dt-web3 Authors
# SPDX-License-Identifier: LGPL-2.1-only

import logging

from datatoken.model.web3_toolkit.contract_base import ContractBase
from datatoken.model.web3_toolkit.event_filter import EventFilter
from datatoken.model.constants import ErrorCode

logger = logging.getLogger(__name__)


class TaskMarket(ContractBase):
    CONTRACT_NAME = 'TaskMarket'
    TASK_ADD_EVENT = 'TaskAdded'
    JOB_ADD_EVENT = 'JobAdded'

    def create_task(self, name, desc, from_wallet):
        """
        Add a new task on chain.

        :param name: refers to the task name
        :param desc: refers to the task description
        :param from_wallet: demander account
        :return: int task_id
        """
        tx_hash = self.send_transaction(
            'createTask',
            (name, desc),
            from_wallet
        )
        receipt = self.get_tx_receipt(tx_hash)

        if not bool(receipt and receipt.status == 1):
            raise AssertionError(f'transaction failed with tx id {tx_hash}.')

        topic_param = self.events.TaskAdded().processReceipt(receipt)
        error_code = topic_param[0]['args']['_code']

        if error_code == ErrorCode.SUCCESS:
            logger.debug(f'sucessfully create task for name {name}')
        else:
            raise AssertionError(f'ERROR_NO_PERMISSION')

        return topic_param[0]['args']['_taskId']

    def add_job(self, cdt, task_id, from_wallet):
        """
        Create a new job on chain with the algorithm cdt.

        :param cdt: refers to the composable data token identifier
        :param task_id: refers to the task id
        :param from_wallet: solver account
        :return: int job_id
        """
        tx_hash = self.send_transaction(
            'addJob',
            (cdt, task_id),
            from_wallet
        )

        receipt = self.get_tx_receipt(tx_hash)

        if not bool(receipt and receipt.status == 1):
            raise AssertionError(f'transaction failed with tx id {tx_hash}.')

        topic_param = self.events.JobAdded().processReceipt(receipt)
        error_code = topic_param[0]['args']['_code']

        if error_code == ErrorCode.SUCCESS:
            logger.debug(f'sucessfully add job for cdt {cdt}')
        else:
            raise AssertionError(f'ERROR_NO_PERMISSION')

        return topic_param[0]['args']['_jobId']

    def get_task(self, task_id):
        """
        Get task info.

        :param task_id: refers to the task id
        :return: Task struct
        """
        return self.contract_concise.getTaskbyId(task_id)

    def get_job(self, job_id):
        """
        Get job info.

        :param job_id: refers to the job id
        :return: Job struct
        """
        return self.contract_concise.getJobbyId(job_id)

    def get_task_num(self):
        """
        Get the total numbers of tasks.

        :return: int
        """
        return self.contract_concise.getTaskNum()

    def get_job_num(self):
        """
        Get the total numbers of jobs.

        :return: int
        """
        return self.contract_concise.getJobNum()

    ######################
    def get_cdt_jobs(self, cdt):
        """
        Get previous jobs for a given cdt.

        :param cdt: refers to the composable data token identifier
        :return: List Job
        """
        _filters = {'_cdt': cdt, '_code': ErrorCode.SUCCESS}

        block_filter = EventFilter(
            TaskMarket.JOB_ADD_EVENT,
            getattr(self.events, TaskMarket.JOB_ADD_EVENT),
            from_block=0,
            to_block='latest',
            argument_filters=_filters
        )

        log_items = block_filter.get_all_entries(max_tries=5)
        job_list = []
        for log_i in log_items:
            _jobId = log_i.args['_jobId']
            _taskId = log_i.args['_taskId']
            _solver = log_i.args['_solver']
            _task = self.get_task(_taskId)
            _demander = _task[0]
            _name = _task[1]
            _desc = _task[2]

            job_list.append(
                (_jobId, _solver, _taskId, _demander, _name, _desc))

        return job_list
