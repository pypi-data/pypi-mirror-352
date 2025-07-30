"""
Address groups module, all the logic to manage address groups from BeyondInsight API
"""

import logging

from cerberus import Validator

from secrets_safe_library import utils
from secrets_safe_library.authentication import Authentication
from secrets_safe_library.core import APIObject


class AddressGroup(APIObject):

    def __init__(self, authentication: Authentication, logger: logging.Logger = None):
        super().__init__(authentication, logger)

        # Schema rules used for validations
        self._schema = {
            "name": {"type": "string", "maxlength": 256, "nullable": True},
            "description": {"type": "string", "maxlength": 256, "nullable": True},
        }
        self._validator = Validator(self._schema)

    def get_address_group_by_id(self, address_group_id: int) -> dict:
        """
        Find an address group by ID.

        API: GET AddressGroups/{id}

        Args:
            address_group_id (int): The address group ID.

        Returns:
            dict: Address group object according requested API version.
        """

        endpoint = f"/addressgroups/{address_group_id}"

        utils.print_log(
            self._logger,
            f"Calling get_address_group_by_id endpoint: {endpoint}",
            logging.DEBUG,
        )
        response = self._run_get_request(endpoint, include_api_version=False)

        return response.json()

    def list_address_groups(self) -> list:
        """
        List the address groups.

        API: GET AddressGroups

        Returns:
            list: List of address groups.
        """

        endpoint = "/addressgroups"

        utils.print_log(
            self._logger,
            f"Calling list_address_groups endpoint: {endpoint}",
            logging.DEBUG,
        )
        response = self._run_get_request(endpoint)

        return response.json()

    def get_address_group_by_name(self, address_group_name: str) -> dict:
        """
        Returns an address group by name.

        API: GET AddressGroups/?name={name}

        Args:
            address_group_name (str): Name of the address group.

        Returns:
            dict: Address group.
        """

        endpoint = f"/AddressGroups?name={address_group_name}"

        utils.print_log(
            self._logger,
            f"Calling get_address_group_by_name endpoint: {endpoint}",
            logging.DEBUG,
        )
        response = self._run_get_request(endpoint, include_api_version=False)

        return response.json()
