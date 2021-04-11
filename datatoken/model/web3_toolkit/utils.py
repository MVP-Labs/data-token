#  Modified from Ocean.py library.
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import json
import logging
import os
from collections import namedtuple

from alaya.packages import eth_utils
from alaya.packages.eth_utils import big_endian_to_int

from alaya.packages import platon_keys as eth_keys
from alaya.packages.platon_keys import KeyAPI
from alaya.packages import platon_account as eth_account

from alaya import Web3
from alaya.contract import ContractEvent

from datatoken.model.web3_toolkit.web3_provider import Web3Provider
from datatoken.model.web3_toolkit.web3_overrides.signature import SignatureFix

Signature = namedtuple('Signature', ('v', 'r', 's'))

logger = logging.getLogger(__name__)


def hash_and_sign(msg, wallet):
    """
    This method use `personal_sign`for signing a message. This will always prepend the
    `\x19Ethereum Signed Message:\n32` prefix before signing.
    :param msg_hash:
    :param wallet: Wallet instance
    :return: signature
    """
    msg_hash = add_ethereum_prefix_and_hash_msg(msg)
    s = wallet.sign(msg_hash)
    return s.signature.hex()


def ec_recover(message, signed_message):
    """
    This method does not prepend the message with the prefix `\x19Ethereum Signed Message:\n32`.
    The caller should add the prefix to the msg/hash before calling this if the signature was
    produced for an ethereum-prefixed message.
    :param message:
    :param signed_message:
    :return:
    """
    w3 = Web3Provider.get_web3()
    v, r, s = split_signature(w3, w3.toBytes(hexstr=signed_message))
    signature_object = SignatureFix(
        vrs=(v, big_endian_to_int(r), big_endian_to_int(s)))
    return w3.eth.account.recoverHash(message, signature=signature_object.to_hex_v_hacked())


def personal_ec_recover(message, signed_message):
    prefixed_hash = add_ethereum_prefix_and_hash_msg(message)
    return ec_recover(prefixed_hash, signed_message)


def add_ethereum_prefix_and_hash_msg(text):
    """
    This method of adding the ethereum prefix seems to be used in web3.personal.sign/ecRecover.

    :param text: str any str to be signed / used in recovering address from a signature
    :return: hash of prefixed text according to the recommended ethereum prefix
    """
    prefixed_msg = f"\x19Ethereum Signed Message:\n{len(text)}{text}"
    return Web3.sha3(text=prefixed_msg)


def to_32byte_hex(web3, val):
    """

    :param web3:
    :param val:
    :return:
    """
    return web3.toBytes(val).rjust(32, b'\0')


def split_signature(web3, signature):
    """

    :param web3:
    :param signature: signed message hash, hex str
    :return:
    """
    assert len(signature) == 65, f'invalid signature, ' \
                                 f'expecting bytes of length 65, got {len(signature)}'
    v = web3.toInt(signature[-1])
    r = to_32byte_hex(web3, int.from_bytes(signature[:32], 'big'))
    s = to_32byte_hex(web3, int.from_bytes(signature[32:64], 'big'))
    if v != 27 and v != 28:
        v = 27 + v % 2

    return Signature(v, r, s)


def privateKeyToAddress(private_key: str) -> str:
    return eth_account.Account().privateKeyToAccount(private_key).address


def privateKeyToPublicKey(private_key: str):
    private_key_bytes = eth_utils.decode_hex(private_key)
    private_key_object = eth_keys.keys.PrivateKey(private_key_bytes)
    return private_key_object.public_key
