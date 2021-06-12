"""Tracer service module."""
# Copyright 2021 The DataToken Authors
# SPDX-License-Identifier: LGPL-2.1-only

import logging

from datatoken.core.dt_helper import DTHelper
from datatoken.store.asset_resolve import resolve_asset
from datatoken.model.keeper import Keeper
from datatoken.service.verifier import VerifierService

logger = logging.getLogger(__name__)


class TracerService(object):
    """The entry point for accessing the tracer service."""
    TERMINAL = 'Algorithm'

    def __init__(self, config):
        keeper = Keeper(config.keeper_options)

        self.asset_provider = keeper.asset_provider
        self.op_template = keeper.op_template
        self.dt_factory = keeper.dt_factory
        self.task_market = keeper.task_market
        self.verifier = VerifierService(config)

        self.config = config

    def get_enterprise(self, id):
        """Get the enterprise info."""
        return self.asset_provider.get_enterprise(id)

    def get_task(self, task_id):
        """Get task info."""
        return self.task_market.get_task(task_id)

    def get_job(self, job_id):
        """Get job info."""
        return self.task_market.get_job(job_id)

    def get_dt_owner(self, dt):
        """Get the owner for a data token."""
        _dt = DTHelper.dt_to_id_bytes(dt)
        return self.dt_factory.get_dt_owner(_dt)

    def get_marketplace_stat(self):
        """Get the statistics information."""
        dt_nums = self.dt_factory.get_dt_num()
        template_nums = self.op_template.get_template_num()
        task_nums = self.task_market.get_task_num()
        job_nums = self.task_market.get_job_num()

        stats = (dt_nums, template_nums, task_nums, job_nums)

        return stats

    def trace_owner_assets(self, address):
        """Get all assets for a given owner."""
        return self.dt_factory.get_owner_assets(address)

    def trace_dt_grantees(self, dt):
        """Get the list of granteed father for a dt."""
        _dt = DTHelper.dt_to_id_bytes(dt)
        return self.dt_factory.get_dt_grantees(_dt)

    def trace_cdt_jobs(self, cdt):
        """Get the list of previous jobs for a given cdt."""
        return self.task_market.get_cdt_jobs(cdt)

    def trace_data_union(self, ddo, prefix):
        """
        Trace the data union structure.

        :param ddo: metadata object.
        :param prefix: fixed prefix path, then find its subsequent paths.
        :return all_paths: a list of found prefix + subsequent paths
        """
        all_paths = []

        if ddo.is_cdt:
            for child_dt in ddo.child_dts:
                new_path = prefix.copy()

                _, child_ddo = resolve_asset(child_dt, self.dt_factory)

                asset_name = child_ddo.metadata["main"].get("name")

                if child_ddo.is_cdt:
                    owner = self.get_dt_owner(child_ddo.dt)
                    owner_info = self.get_enterprise(owner)[0]

                    new_path.append(
                        {"dt": child_dt, "name": asset_name, "aggregator": owner_info})
                    path_lists = self.trace_data_union(child_ddo, new_path)
                    all_paths.extend(path_lists)
                else:
                    asset_type = child_ddo.metadata['main'].get('type')
                    new_path.append(
                        {"dt": child_dt, "name": asset_name, "type": asset_type})
                    all_paths.append(new_path)

        return all_paths

    def trace_dt_lifecycle(self, dt, prefix: list):
        """
        Trace the whole lifecycle for a dt using dfs recursive search. Only when an
        algorithm cdt is submitted for solving tasks, the terminal state is reached.

        :param dt: data token identifier.
        :param prefix: fixed prefix path, then find its subsequent paths.
        :return all_paths: a list of found prefix + subsequent paths
        """

        prefix = prefix.copy()
        if len(prefix):
            owner = self.get_dt_owner(dt)
            owner_info = self.get_enterprise(owner)[0]
            prefix.append({"dt": DTHelper.id_bytes_to_dt(
                dt), "aggregator": owner_info, "aggrement": 0})
        else:
            prefix.append({"dt": dt})
            dt = DTHelper.dt_to_id_bytes(dt)

        _, ddo = resolve_asset(dt, self.dt_factory)

        all_paths = []

        if self.verifier.check_asset_type(ddo, self.TERMINAL):
            jobs = self.trace_cdt_jobs(dt)

            if len(jobs):
                for job in jobs:
                    job_id, solver, task_id, demander, task_name, task_desc = job
                    demander_info = self.get_enterprise(demander)[0]
                    solver_info = self.get_enterprise(solver)[0]

                    text = {"task_name": task_name, "task_desc": task_desc, "solver": solver_info,
                            "demander": demander_info, "task_id": task_id, "job_id": job_id}

                    new_path = prefix.copy()
                    new_path.append(text)
                    all_paths.append(new_path)

            return all_paths

        grantees = self.trace_dt_grantees(dt)

        for cdt in grantees:

            path_lists = self.trace_dt_lifecycle(cdt, prefix)
            all_paths.extend(path_lists)

        return all_paths

    def job_list_format(self, paths):
        """
        Convert paths to a formated job list table.

        :param paths: a list of dt->...->dt-> [job, ..., job] authorization chains, with the same root dt
        :return: list
        """
        if len(paths) == 0:
            print('Do not find any data linking path')
            return None

        job_list = []
        root = paths[0][0]

        for path in paths:
            if path[0] != root:
                raise AssertionError(f'A tree can only contain one root')

            job_list.append(path[-1])

        return job_list

    def tree_format(self, paths):
        """
        Convert paths to a formated hierarchical tree using Node class.

        :param paths: a list of dt->...->dt->... authorization chains, with the same root dt
        :return: root Node instance
        """
        if len(paths) == 0:
            print('Do not find any data linking path')
            return None

        root = paths[0][0]

        for path in paths:
            if path[0] != root:
                raise AssertionError(f'A tree can only contain one root')

        root_node = Node(text=root, level=0)
        for path in paths:
            tmp_node = root_node
            level = 1
            index = 0

            for path_value in path[1:]:
                child_node = tmp_node.get_child(text=path_value)
                if not child_node:
                    child_node = Node(text=path_value, level=level)
                    tmp_node.add_child(child_node)

                tmp_node = child_node
                level += 1
                index += 1

        return root_node

    def tree_to_json(self, node):

        data = {"values": node.text}

        if len(node.child_nodes):
            data["children"] = []

        for n in node.child_nodes:
            data["children"].append(self.tree_to_json(n))

        return data

    def print_tree(self, node, indent: list, final_node=True):
        """Recursively output the node text and its child node."""
        for i in range(node.level):
            print(indent[i], end='')

        if final_node:
            print('└──', end='')
        else:
            print('├──', end='')

        print(node.text)

        if node.empty():
            return
        else:
            cnt = len(node.child_nodes)
            for i, n in enumerate(node.child_nodes):
                c = '    ' if final_node else '│   '
                indent.append(c)
                last_node = i == cnt - 1
                self.print_tree(n, indent, last_node)
                del indent[-1]


###################
class Node:
    """The Node class used for linking child and father dts."""

    def __init__(self, text, level):
        self._text = text       # dt in this level
        self._level = level     # current tree depth
        self._child_nodes = []  # its granted father dt

    @ property
    def text(self):
        return self._text

    @ property
    def level(self):
        return self._level

    @ property
    def child_nodes(self):
        return self._child_nodes

    def add_child(self, node):
        self._child_nodes.append(node)

    def get_child(self, text):
        for node in self._child_nodes:
            if node.text == text:
                return node
        return None

    def empty(self):
        return len(self._child_nodes) == 0

    def __str__(self):
        return self.text
