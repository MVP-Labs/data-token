"""Constraint module."""
# Copyright 2021 The dt-asset Authors
# SPDX-License-Identifier: LGPL-2.1-only

import json

from datatoken.store.asset_resolve import resolve_op


def validate_leaf_template(leaf_ddo, keeper_op_template):
    """
    Check whether the leaf ddo contains illegal services. In this case, 
    leaf constraints must provide the same parameters of used templates.

    :param leaf_ddo: DDO object for a leaf asset
    :param keeper_op_template: keeper instance of the op-template smart contract
    :return: bool
    """
    for service in leaf_ddo.services:
        op_descriptor = service.descriptor

        tid = op_descriptor.get('template')
        constraint = op_descriptor.get('constraint')
        if not tid:
            return False

        data, op = resolve_op(tid, keeper_op_template)
        if not data or not op:
            return False

        params = json.loads(op.params)
        if not _check_params(params, constraint):
            return False

        return True


def validate_service_agreement(cdt_ddo, required_ddo):
    """
    Check whether a father ddo satisfies service requirements of a child ddo. 
    In this case, the low-level constraints must be fulfilled and satisfied.

    :param cdt_ddo: DDO object for a high-level composable asset
    :param required_ddo: child DDO that needs to be satisfied.
    :return: bool
    """
    is_cdt = required_ddo.is_cdt
    terminal = (cdt_ddo.asset_type == 'Algorithm')

    if required_ddo.asset_type == 'Algorithm':
        return False

    for service in cdt_ddo.services:
        fulfilled = service.descriptor['workflow'].get(required_ddo.dt)

        if not fulfilled:
            return False

        sid = fulfilled.get('service')
        constraint = fulfilled.get('constraint')

        child_service = required_ddo.get_service_by_index(sid)
        if not child_service:
            return False

        if is_cdt:
            sub_constraint = dict()
            for key, value in child_service.descriptor['workflow'].items():
                sub_constraint[key] = value['constraint']
        else:
            sub_constraint = child_service.descriptor['constraint']

        if not _check_fulfills(sub_constraint, constraint, terminal):
            return False

    return True


def _check_params(params: dict, constraint: dict):
    """
    Check whether a leaf asset provide the required parameters when it
    uses a trusted op template.

    :param params: required parameters for a op template
    :param constraint: leaf contraints.
    :return: bool
    """
    if set(params.keys()) != set(constraint.keys()):
        return False

    return True


def _check_fulfills(required_constraint: dict, fulfill_constraint: dict, terminal=False):
    """
    Check whether the low-level constraints are satisfied.

    :param required_constraint: low-level requirements
    :param fulfill_constraint: high-level fulfills
    :param terminal: true when it is an Algorithm asset.
    :return: bool
    """
    if set(required_constraint.keys()) != set(fulfill_constraint.keys()):
        return False

    for key, value in fulfill_constraint.items():
        required = required_constraint[key]
        if isinstance(value, dict):
            if not isinstance(required, dict):
                return False

            if required and set(value.keys()) != set(required.keys()):
                return False

            for sub_key, sub_value in value.items():
                if terminal and sub_value == None:
                    return False

                sub_required = required.get(sub_key)
                if sub_required and sub_value != sub_required:
                    return False
        else:
            if (terminal and value == None) or (required and value != required):
                return False

    return True
