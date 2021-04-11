"""Service Lib."""
# Copyright 2021 The dt-asset Authors
# SPDX-License-Identifier: LGPL-2.1-only

import copy


class Service:
    """Service class for storing the asset descriptor."""
    INDEX = 'index'
    ENDPOINT = 'endpoint'
    DESCRIPTOR = 'descriptor'
    ATTRIBUTES = 'attributes'

    def __init__(self, index, endpoint, descriptor, attributes):
        self._index = index
        self._endpoint = endpoint
        self._descriptor = descriptor
        self._attributes = attributes

    @property
    def index(self):
        """ Get the service index."""
        return self._index

    @property
    def endpoint(self):
        """ Get the service endpoint."""
        return self._endpoint

    @property
    def descriptor(self):
        """ Get the service descriptor."""
        return self._descriptor

    @property
    def attributes(self):
        """ Get the service attributes."""
        return self._attributes

    def to_dict(self):
        """
        Return the service as a JSON dict.

        :return: dict
        """
        descriptor = {}
        for key, value in self._descriptor.items():
            if isinstance(value, object) and hasattr(value, 'to_dict'):
                value = value.to_dict()
            elif isinstance(value, list):
                value = [v.to_dict() if hasattr(
                    v, 'to_dict') else v for v in value]
            descriptor[key] = value

        values = {
            self.INDEX: self._index,
            self.ENDPOINT: self._endpoint,
            self.DESCRIPTOR: descriptor,
            self.ATTRIBUTES: self._attributes
        }

        return values

    @classmethod
    def parse_dict(cls, value_dict):
        """Read a service dict."""
        values = copy.deepcopy(value_dict)
        _index = values.pop(cls.INDEX, None)
        _endpoint = values.pop(cls.ENDPOINT, None)
        _descriptor = values.pop(cls.DESCRIPTOR, None)
        _attributes = values.pop(cls.ATTRIBUTES, None)

        return _index, _endpoint, _descriptor, _attributes

    def validate(self, asset_type, child_dts):
        """Validator of the service composition

        :param asset_type: str
        :param child_dts: list
        :return: bool
        """
        if not self._endpoint and asset_type != 'Algorithm':
            return False
        if not self._descriptor or self._index == None or not isinstance(self._descriptor, dict):
            return False

        if bool(child_dts):
            workflow = self._descriptor.get('workflow')
            if not isinstance(workflow, dict) or set(workflow.keys()) != set(child_dts):
                return False

            for agreement in workflow.values():
                if not isinstance(agreement, dict) or agreement.get('service') == None or not isinstance(
                        agreement.get('constraint'), dict):
                    return False
        else:
            if not self._descriptor.get('template') or not isinstance(
                    self._descriptor.get('constraint'), dict):
                return False

        return True
