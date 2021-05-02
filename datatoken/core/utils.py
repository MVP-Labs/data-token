"""Utilities module."""
# Copyright 2021 The dt-asset Authors
# SPDX-License-Identifier: LGPL-2.1-only

import hashlib
import json
import uuid
from web3 import Web3
from datetime import datetime


def convert_to_bytes(data):
    return Web3.toBytes(text=data)


def convert_to_string(data):
    return Web3.toHex(data)


def get_timestamp():
    """Return the current system timestamp."""
    return f'{datetime.utcnow().replace(microsecond=0).isoformat()}Z'


def calc_checksum(seed):
    """Calculate the hash3_256."""

    def _sort_dict(dict_value: dict):
        dict_value = dict(sorted(dict_value.items(), reverse=False))

        for key, value in dict_value.items():
            if isinstance(value, dict):
                value = _sort_dict(value)
                dict_value[key] = value
            elif isinstance(value, list):
                for index, sub_value in enumerate(value):
                    if isinstance(sub_value, dict):
                        sub_value = _sort_dict(sub_value)
                        value[index] = sub_value

        return dict_value

    return hashlib.sha3_256((json.dumps(_sort_dict(seed)).replace(
        " ", "")).encode('utf-8')).hexdigest()
