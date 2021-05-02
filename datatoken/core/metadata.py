"""Metadata Lib."""
#  Modified from common-utils-py library.
#  Copyright 2018 Ocean Protocol Foundation

import logging

logger = logging.getLogger(__name__)


class MetadataMain(object):
    """The main attributes that need to be included in the Asset Metadata."""
    KEY = 'main'
    VALUES_KEYS = {
        'type',
        'author',
        'name',
        'created',
        'license'
    }
    REQUIRED_VALUES_KEYS = {'type'}
    # type e.g., Dataset/Computa/Model/Algorithm/Operation
    # future: need to specify different usage properties for different type


class Metadata(object):
    REQUIRED_SECTIONS = {MetadataMain.KEY}
    MAIN_SECTIONS = {
        MetadataMain.KEY: MetadataMain
    }

    @staticmethod
    def validate(metadata):
        """Validator of the metadata composition

        :param metadata: dict
        :return: bool
        """

        for section_key in Metadata.REQUIRED_SECTIONS:
            if section_key not in metadata or not metadata[section_key] or not isinstance(
                    metadata[section_key], dict):
                return False

            section = Metadata.MAIN_SECTIONS[section_key]
            section_metadata = metadata[section_key]
            for subkey in section.REQUIRED_VALUES_KEYS:
                if subkey not in section_metadata or section_metadata[subkey] is None:
                    return False

        return True
