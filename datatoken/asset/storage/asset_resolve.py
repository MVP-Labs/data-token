"""Asset resolve Lib."""
# Copyright 2021 The dt-asset Authors
# SPDX-License-Identifier: LGPL-2.1-only

from datatoken.asset.ddo import DDO
from datatoken.asset.dt_helper import DTHelper
from datatoken.asset.operator import OpTemplate
from datatoken.asset.storage.ipfs_provider import IPFSProvider


def resolve_asset(dt, keeper_dt_factory):
    """
    Resolve an asset dt to its corresponding DDO.

    :param dt: the asset dt to resolve, e.g., dt:ownership:<32 byte value>
    :param keeper_dt_factory: keeper instance of the dt-factory smart contract

    :return data: dt info on the chain
    :return ddo: DDO of the resolved asset dt
    """
    dt_bytes = DTHelper.dt_to_id_bytes(dt)
    data = keeper_dt_factory.get_dt_register(dt_bytes)
    if not (data and data[4]):
        return None, None

    metadata_url = data[4]
    ipfs_client = IPFSProvider()
    ddo_json = ipfs_client.get(metadata_url)
    if not ddo_json:
        return data, None

    ddo = DDO()
    ddo.from_dict(ddo_json)

    return data, ddo


def resolve_asset_by_url(metadata_url):
    ipfs_client = IPFSProvider()
    ddo_json = ipfs_client.get(metadata_url)
    if not ddo_json:
        return None

    ddo = DDO()
    ddo.from_dict(ddo_json)

    return ddo


def resolve_op(tid, keeper_op_template):
    """
    Resolve a tid to its corresponding OpTemplate.

    :param tid: the op tid to resolve, e.g., dt:ownership:<32 byte value>
    :param keeper_op_template: keeper instance of the op-template smart contract

    :return data: tid info on the chain
    :return op: OpTemplate of the resolved tid
    """
    tid_bytes = DTHelper.dt_to_id_bytes(tid)

    data = keeper_op_template.get_template(tid_bytes)
    if not (data and data[3]):
        return None, None

    metadata_url = data[3]
    ipfs_client = IPFSProvider()
    op_json = ipfs_client.get(metadata_url)
    if not op_json:
        return data, None

    op = OpTemplate()
    op.from_dict(op_json)

    return data, op
