"""DT helper Lib"""
#  Modified from common-utils-py library.
#  Copyright 2018 Ocean Protocol Foundation

import re
import hashlib
import json
import uuid
from web3 import Web3
from eth_utils import remove_0x_prefix
from datatoken.asset.utils import calc_checksum, convert_to_string

PREFIX = 'dt:ownership:'


class DTHelper:
    """Class representing an asset dt."""

    @staticmethod
    def generate_new_dt():
        """
        Create a dt.

        Format of the dt:
        dt:ownership:cb36cf78d87f4ce4a784f17c2a4a694f19f3fbf05b814ac6b0b7197163888865

        :param seed: The list of checksums that is allocated in the proof, dict
        :return: Asset dt, str.
        """
        return PREFIX + uuid.uuid4().hex + uuid.uuid4().hex

    @staticmethod
    def id_to_dt(dt_id):
        """Return an Ownership dt from given a hex id."""
        if isinstance(dt_id, bytes):
            dt_id = Web3.toHex(dt_id)

        # remove leading '0x' of a hex string
        if isinstance(dt_id, str):
            dt_id = remove_0x_prefix(dt_id)
        else:
            raise TypeError("dt id must be a hex string or bytes")

        # test for zero address
        if Web3.toBytes(hexstr=dt_id) == b'':
            dt_id = '0'
        return f'{PREFIX}{dt_id}'

    @staticmethod
    def dt_to_id(dt):
        """Return an id extracted from a dt string."""
        result = DTHelper.dt_parse(dt)
        if result and result['id'] is not None:
            return result['id']
        return None

    @staticmethod
    def dt_to_id_bytes(dt):
        """
        Return an Ownership dt to it's correspondng hex id in bytes.

        So dt:ownership:<hex>, will return <hex> in byte format
        """
        if isinstance(dt, str):
            if re.match('^[0x]?[0-9A-Za-z]+$', dt):
                raise ValueError(f'{dt} must be a dt not a hex string')
            else:
                dt_result = DTHelper.dt_parse(dt)
                if not dt_result:
                    raise ValueError(f'{dt} is not a valid dt')
                if not dt_result['id']:
                    raise ValueError(f'{dt} is not a valid Ownership dt')
                id_bytes = Web3.toBytes(hexstr=dt_result['id'])
        elif isinstance(dt, bytes):
            id_bytes = dt
        else:
            raise TypeError(
                f'Unknown dt format, expected str or bytes, got {dt} of type {type(dt)}'
            )

        return id_bytes

    @staticmethod
    def id_bytes_to_dt(id_bytes):
        id = convert_to_string(id_bytes)
        return DTHelper.id_to_dt(id)

    @staticmethod
    def dt_parse(dt):
        """
        Parse a dt into it's parts.

        :param dt: Asset dt, str.
        :return: Python dictionary with the method and the id.
        """
        if not isinstance(dt, str):
            raise TypeError(
                f'Expecting dt of string type, got {dt} of {type(dt)} type')

        match = re.match('^dt:([a-z0-9]+):([a-zA-Z0-9-.]+)(.*)', dt)
        if not match:
            raise ValueError(f'dt {dt} does not seem to be valid.')

        result = {
            'method': match.group(1),
            'id': match.group(2),
        }

        return result
