"""DDO Lib."""
#  Modified from common-utils-py library.
#  Copyright 2018 Ocean Protocol Foundation

import copy
import json

from datatoken.core.dt_helper import PREFIX
from datatoken.core.metadata import Metadata
from datatoken.core.service import Service
from datatoken.core.utils import get_timestamp, calc_checksum


class DDO:
    """DDO class to create, import and export DDO objects."""

    def __init__(self, json_text=None, json_filename=None, dictionary=None):
        self._dt = None
        self._creator = None
        self._metadata = {}
        self._services = []
        self._proof = None

        self._asset_type = None
        self._child_dts = None

        if not json_text and json_filename:
            with open(json_filename, 'r') as file_handle:
                json_text = file_handle.read()

        if json_text:
            self.from_dict(json.loads(json_text))
        elif dictionary:
            self.from_dict(dictionary)

    @property
    def dt(self):
        """ Get the DT identifier."""
        return self._dt

    @property
    def creator(self):
        """ Get the creator address."""
        return self._creator

    @property
    def metadata(self):
        """Get the metadata service."""
        return self._metadata

    @property
    def services(self):
        """Get the list of services."""
        return self._services

    @property
    def asset_type(self):
        """Get the asset type."""
        return self._asset_type

    @property
    def child_dts(self):
        """Get the child dts."""
        return self._child_dts

    @property
    def is_cdt(self):
        """Check cdt or not."""
        return bool(self._child_dts)

    @property
    def proof(self):
        """Get the static proof, or None."""
        return self._proof

    def get_service_by_index(self, index):
        """
        Get service for a given index.

        :param index: Service id, str
        :return: Service
        """
        for service in self._services:
            if service.index == index:
                return service

        return None

    def assign_dt(self, dt: str):
        """
        Assign dt to the DDO.
        """
        assert dt.startswith(PREFIX), \
            f'"dt" seems invalid, must start with {PREFIX} prefix.'
        self._dt = dt
        return dt

    def add_creator(self, creator_address: str):
        """
        Add creator.

        :param creator_address: str
        """
        self._creator = creator_address

    def add_metadata(self, value_dict, child_dts=None):
        """
        Add metadata to the DDO.

        :param values: dict
        """
        values = copy.deepcopy(value_dict) if value_dict else {}
        assert Metadata.validate(values), \
            f'values {values} seems invalid.'

        asset_type = values['main']['type']
        if asset_type == 'Algorithm' and not child_dts:
            raise AssertionError('Algorithm must be composable DT.')

        self._metadata = values
        self._asset_type = asset_type
        self._child_dts = child_dts

    def add_service(self, value_dict):
        """
        Add a service to the list of services on the DDO.

        :param value_dict: Python dict with setvice index, endpoint, descriptor, attributes.
        """
        assert self._asset_type, \
            f'asset type seems unknown, please add metadata first.'
        if self._asset_type == 'Algorithm':
            if len(self._services):
                raise AssertionError(
                    'Algorithm can only contain one service for termination.')

        values = copy.deepcopy(value_dict) if value_dict else {}

        _index, _endpoint, _descriptor, _attributes = Service.parse_dict(
            values)
        if self.get_service_by_index(_index) != None:
            raise AssertionError(f'service index already exists.')

        service = Service(_index, _endpoint, _descriptor, _attributes)
        if not service.validate(self._asset_type, self._child_dts):
            raise AssertionError(f'values {values} seems invalid.')

        self._services.append(service)

        return

    def create_proof(self):
        """create the proof for this template."""
        data = {
            'dt': self._dt,
            'creator': self._creator,
            'metadata': self._metadata,
            'child_dts': self._child_dts
        }

        if self._services:
            values = []
            for service in self._services:
                values.append(service.to_dict())
            data['services'] = values

        checksum = calc_checksum(data)

        self._proof = {
            'created': get_timestamp(),
            'checksum': checksum
        }

        return checksum

    def to_dict(self):
        """
        Return the DDO as a JSON dict.

        :return: dict
        """
        data = {
            'dt': self._dt,
            'creator': self._creator,
            'metadata': self._metadata,
            'child_dts': self._child_dts,
            'proof': self._proof
        }
        if self._services:
            values = []
            for service in self._services:
                values.append(service.to_dict())
            data['services'] = values

        return data

    def from_dict(self, value_dict):
        """Import a JSON dict into this DDO."""
        values = copy.deepcopy(value_dict)

        dt = values.pop('dt')
        creator = values.pop('creator')
        metadata = values.pop('metadata')
        child_dts = values.pop('child_dts')
        proof = values.pop('proof')

        self.assign_dt(dt)
        self.add_creator(creator)
        self.add_metadata(metadata, child_dts)

        self._services = []
        for value in values.pop('services'):
            self.add_service(value)

        checksum = self.create_proof()

        if not isinstance(proof, dict) or proof.get(
                'checksum') == None or proof['checksum'] != checksum:
            raise AssertionError(f'wrong template checksum')

        self._proof = proof
