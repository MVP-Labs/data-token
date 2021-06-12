"""OpTemplate Lib."""
# Copyright 2021 The DataToken Authors
# SPDX-License-Identifier: LGPL-2.1-only

import copy
import json
from datatoken.core.metadata import Metadata
from datatoken.core.dt_helper import PREFIX
from datatoken.core.utils import get_timestamp, calc_checksum


class OpTemplate:
    """OpTemplate class for describing trusted operations."""

    def __init__(self, dictionary=None):
        self._tid = None
        self._creator = None
        self._metadata = None
        self._operation = None
        self._params = None
        self._proof = None

        if dictionary:
            self.from_dict(dictionary)

    @property
    def tid(self):
        """ Get the op tid."""
        return self._tid

    @property
    def creator(self):
        """ Get the creator address."""
        return self._creator

    @property
    def metadata(self):
        """Get the op metadata."""
        return self._metadata

    @property
    def operation(self):
        """Get the op code."""
        return self._operation

    @property
    def params(self):
        """Get the op params."""
        return self._params

    @property
    def proof(self):
        """Get the static proof, or None."""
        return self._proof

    def assign_tid(self, tid: str):
        """
        Add tid to this template.

        :param values: dict
        """
        assert tid.startswith(PREFIX), \
            f'"tid" seems invalid, must start with {PREFIX} prefix.'
        self._tid = tid

    def add_creator(self, creator_address: str):
        """
        Add creator.

        :param creator_address: str
        """
        self._creator = creator_address

    def add_metadata(self, values: dict):
        """
        Add metadata.

        :param values: dict
        """
        values = copy.deepcopy(values) if values else {}
        assert Metadata.validate(values), \
            f'values {values} seems invalid.'

        asset_type = values['main']['type']
        if asset_type != 'Operation':
            raise AssertionError('Template must be Operation type.')

        self._metadata = values

    def add_template(self, operation, params):
        """
        Add template to this instance.

        :param operation: trusted code, str
        :param params: required parameters for the code, dict
        """
        if not self._metadata:
            raise AssertionError(f'please add metadata first')

        self._operation = operation
        self._params = params

    def create_proof(self):
        """create the proof for this template."""
        data = {
            'tid': self._tid,
            'creator': self._creator,
            'metadata': self._metadata,
            'operation': self._operation,
            'params': self._params
        }

        checksum = calc_checksum(data)

        self._proof = {
            'created': get_timestamp(),
            'checksum': checksum
        }

        return checksum

    def to_dict(self):
        """Return the template as a JSON dict."""
        data = {
            'tid': self._tid,
            'creator': self._creator,
            'metadata': self._metadata,
            'operation': self._operation,
            'params': self._params,
            'proof': self._proof
        }

        return data

    def from_dict(self, value_dict):
        """Import a JSON dict into this template."""
        values = copy.deepcopy(value_dict)

        tid = values.pop('tid')
        creator = values.pop('creator')
        metadata = values.pop('metadata')
        operation = values.pop('operation')
        params = values.pop('params')
        proof = values.pop('proof')

        self.assign_tid(tid)
        self.add_creator(creator)
        self.add_metadata(metadata)
        self.add_template(operation, params)

        checksum = self.create_proof()

        if not isinstance(proof, dict) or proof.get(
                'checksum') == None or proof['checksum'] != checksum:
            raise AssertionError(f'wrong template checksum')

        self._proof = proof
