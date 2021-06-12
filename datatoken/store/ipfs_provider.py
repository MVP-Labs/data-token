"""IPFS provider Lib."""
# Copyright 2021 The DataToken Authors
# SPDX-License-Identifier: LGPL-2.1-only

import ipfshttpclient

class IPFSProvider:
    """Asset storage provider."""

    def __init__(self, config=None):
        """Initialize the ipfs provider."""
        if config:
            self.ipfs_client = ipfshttpclient.connect(config.ipfs_endpoint)
        else:
            self.ipfs_client = ipfshttpclient.connect()

    def add(self, json):
        """
        Add asset values to the storage.

        :param json: dict value
        :return hash: ipfs cid
        """
        hash = self.ipfs_client.add_json(json)
        return hash

    def get(self, hash):
        """
        Get asset values for a given cid.

        :param hash: ipfs cid
        :return: dict
        """
        return self.ipfs_client.get_json(hash)

    def close(self):
        """Disable the provider"""
        self.ipfs_client.close()
