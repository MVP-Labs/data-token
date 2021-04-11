"""IPFS provider Lib."""
# Copyright 2021 The dt-asset Authors
# SPDX-License-Identifier: LGPL-2.1-only

from urllib.parse import urljoin
from rfc3986 import urlparse
import ipfsapi


class IPFSProvider:
    """Asset storage provider."""

    def __init__(self):
        """Initialize the provider by using singnet ipfs gateway."""
        ipfs_rpc_endpoint = "https://ipfs.singularitynet.io:80"
        ipfs_rpc_endpoint = urlparse(ipfs_rpc_endpoint)
        ipfs_scheme = ipfs_rpc_endpoint.scheme if ipfs_rpc_endpoint.scheme else "http"
        ipfs_port = ipfs_rpc_endpoint.port if ipfs_rpc_endpoint.port else 5001

        self.ipfs_client = ipfsapi.connect(
            urljoin(ipfs_scheme, ipfs_rpc_endpoint.hostname), ipfs_port, session=True)

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
