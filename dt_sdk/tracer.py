"""Tracer service module."""
# Copyright 2021 The dt-sdk Authors
# SPDX-License-Identifier: LGPL-2.1-only

import logging

from dt_web3.keeper import Keeper
from dt_asset.document.dt_helper import DTHelper
from dt_asset.storage.ipfs_provider import IPFSProvider
from dt_asset.storage.asset_resolve import resolve_asset, resolve_op
from dt_sdk.verifier import VerifierService

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

    def get_enterprize(self, id):
        """Get the enterprize info."""
        return self.asset_provider.get_enterprize(id)

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

    def trace_dt_lifecycle(self, prefix_path: list):
        """
        Trace the whole lifecycle for a dt using dfs recursive search. Only when an 
        algorithm cdt is submitted for solving tasks, the terminal state is reached.

        :param prefix_path: fixed prefix path, then find its subsequent paths.
        :return all_paths: a list of found prefix + subsequent paths
        """
        dt = prefix_path[-1]
        grantees = self.trace_dt_grantees(dt)

        all_paths = []

        for cdt in grantees:

            new_path = prefix_path.copy()
            new_path.append(cdt)

            _, ddo = resolve_asset(cdt, self.dt_factory)

            if self.verifier.check_asset_type(ddo, self.TERMINAL):
                jobs = self.trace_cdt_jobs(cdt)
                if len(jobs):
                    new_path.append(jobs)
                    all_paths.append(new_path)
            else:
                path_lists = self.trace_dt_lifecycle(new_path)
                all_paths.extend(path_lists)

        return all_paths

    def tracer_print(self, paths, detailed=True):
        """
        Output the hierarchical tree in which each leaf is a terminal job.

        :param paths: a list of authorization chains, with the same root dt
        :param detailed: output more information, e.g., aggregators/agreements/tasks
        :return
        """
        if len(paths) == 0:
            print('Do not find any asset sharing path')
        else:
            tree = self._tree_format(paths)
            self._print_tree(tree, indent=[], final_node=True)

    def _tree_format(self, paths):
        """
        Convert paths to a formated tree using Node class.

        :param paths: a list of dt->...->dt->[job,...,job] authorization chains
        :return: root Node instance
        """
        root = paths[0][0]

        for path in paths:
            if path[0] != root:
                raise AssertionError(f'A tree can only contai one root')

        root_node = Node(text=root, level=0)
        for path in paths:
            tmp_node = root_node
            level = 1
            index = 0

            for id_bytes in path[1:-1]:
                owner = self.get_dt_owner(id_bytes)
                owner_info = self.get_enterprize(owner)
                dt = DTHelper.id_bytes_to_dt(id_bytes)

                text = dt + f' (aggregator: {owner_info[0]})'
                child_node = tmp_node.get_child(text=text)
                if not child_node:
                    child_node = Node(text=text, level=level)
                    tmp_node.add_child(child_node)

                tmp_node = child_node
                level += 1
                index += 1

            for job in path[-1]:
                job_id, _, task_id, demander, task_name, _ = job
                demander_info = self.get_enterprize(demander)
                text = f' (task_name: {task_name}, demander: {demander_info[0]}, task_id: {task_id}, job_id: {job_id})'
                child_node = Node(text=text, level=level)
                tmp_node.add_child(child_node)

        return root_node

    def _print_tree(self, node, indent: list, final_node=True):
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
                self._print_tree(n, indent, last_node)
                del indent[-1]


###################
class Node:
    """The Node class used for linking child and father dts."""

    def __init__(self, text, level):
        self._text = text       # dt in this level
        self._level = level     # current tree depth
        self._child_nodes = []  # its granted father dt

    @property
    def text(self):
        return self._text

    @property
    def level(self):
        return self._level

    @property
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
