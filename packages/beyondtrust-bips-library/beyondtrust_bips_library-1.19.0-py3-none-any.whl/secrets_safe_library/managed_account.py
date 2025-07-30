"""ManagedAccount Module, all the logic to retrieve managed accounts from PS API"""

import logging

import requests
from cerberus import Validator

from secrets_safe_library import exceptions, utils
from secrets_safe_library.core import APIObject


class ManagedAccount(APIObject):

    _authentication = None
    _logger = None
    _separator = None
    _sign_app_out_error_message = "Error in sign_app_out"

    def __init__(self, authentication, logger=None, separator="/"):
        self._authentication = authentication
        self._logger = logger

        # Schema rules used for validations
        self._schema = {
            "system_name": {"type": "string", "maxlength": 129, "nullable": True},
            "account_name": {"type": "string", "maxlength": 246, "nullable": True},
            "system_id": {"type": "integer", "nullable": True},
            "workgroup_name": {"type": "string", "maxlength": 256, "nullable": True},
            "application_display_name": {
                "type": "string",
                "maxlength": 256,
                "nullable": True,
            },
            "ip_address": {"type": "string", "maxlength": 45, "nullable": True},
            "type": {
                "type": "string",
                "allowed": [
                    "system",
                    "recent",
                    "domainlinked",
                    "database",
                    "cloud",
                    "application",
                ],
                "nullable": True,
            },
            "limit": {"type": "integer", "min": 1, "max": 1000, "default": 1000},
            "offset": {"type": "integer", "min": 0, "default": 0},
        }
        self._validator = Validator(self._schema)

        if len(separator.strip()) != 1:
            raise exceptions.LookupError(f"Invalid separator: {separator}")
        self._separator = separator

    def get_secret(self, path):
        """
        Get Managed account by path
        Arguments:
            path
        Returns:
            Retrieved managed account string
        """

        utils.print_log(
            self._logger,
            "Running get_secret method in ManagedAccount class",
            logging.DEBUG,
        )
        managed_account_dict = self.managed_account_flow([path])
        return managed_account_dict[path]

    def get_secret_with_metadata(self, path):
        """
        Get Managed account with metadata by path
        Arguments:
            path
        Returns:
             Retrieved managed account in dict format
        """

        utils.print_log(
            self._logger,
            "Running get_secret method in ManagedAccount class",
            logging.DEBUG,
        )
        managed_account_dict = self.managed_account_flow([path], get_metadata=True)
        return managed_account_dict

    def get_secrets(self, paths):
        """
        Get Managed accounts by paths
        Arguments:
            paths list
        Returns:
            Retrieved managed account in dict format
        """

        utils.print_log(
            self._logger,
            "Running get_secrets method in ManagedAccount class",
            logging.INFO,
        )
        managed_account_dict = self.managed_account_flow(paths)
        return managed_account_dict

    def get_secrets_with_metadata(self, paths):
        """
        Get Managed accounts with metadata by paths
        Arguments:
            paths list
        Returns:
            Retrieved managed account in dict format
        """

        utils.print_log(
            self._logger,
            "Running get_secrets method in ManagedAccount class",
            logging.INFO,
        )
        managed_account_dict = self.managed_account_flow(paths, get_metadata=True)
        return managed_account_dict

    def get_request_id(self, system_id, account_id):
        create_request_response = self.create_request(system_id, account_id)
        request_id = create_request_response.json()
        return request_id

    def managed_account_flow(self, paths, get_metadata=False):
        """
        Managed account by path flow
        Arguments:
            paths list
        Returns:
            Response (Dict)
        """

        response = {}

        for path in paths:

            utils.print_log(
                self._logger,
                f"**************** managed account path: {path} ****************",
                logging.INFO,
            )
            data = path.split(self._separator)

            if len(data) != 2:
                raise exceptions.LookupError(
                    f"Invalid managed account path: {path}. Use '{self._separator}' as "
                    f"a delimiter: system_name{self._separator}managed_account_name"
                )

            system_name = data[0]
            managed_account_name = data[1]

            manage_account = self.get_managed_accounts(
                system_name=system_name, account_name=managed_account_name
            )

            if get_metadata:
                response[f"{path}-metadata"] = manage_account

            utils.print_log(
                self._logger, "Managed account info retrieved", logging.DEBUG
            )

            request_id = self.get_request_id(
                manage_account["SystemId"], manage_account["AccountId"]
            )

            utils.print_log(
                self._logger,
                f"Request id retrieved: {'*' * len(str(request_id))}",
                logging.DEBUG,
            )

            if not request_id:
                raise exceptions.LookupError("Request Id not found")

            credential = self.get_credential_by_request_id(request_id)

            response[path] = credential

            utils.print_log(
                self._logger, "Credential was successfully retrieved", logging.INFO
            )

            self.request_check_in(request_id)
        return response

    def create_request(self, system_id: int, account_id: int) -> requests.Response:
        """
        Create request by system ID and account ID.

        API: POST Requests

        Args:
            system_id (int): ID of the managed system to request.
            account_id (int): ID of the managed account to request.

        Returns:
            request.Response: Response object.
        """
        payload = {
            "SystemID": system_id,
            "AccountID": account_id,
            "DurationMinutes": 5,
            "Reason": "Secrets Safe Integration",
            "ConflictOption": "reuse",
        }

        endpoint = "/Requests"
        utils.print_log(
            self._logger, f"Calling create_request endpoint: {endpoint}", logging.DEBUG
        )
        response = self._run_post_request(
            endpoint,
            payload=payload,
            expected_status_code=[200, 201],
            include_api_version=False,
        )
        return response

    def get_credential_by_request_id(self, request_id: int):
        """
        Retrieves the credentials for an approved and active (not expired) credentials
        release request.

        API: GET Credentials/{requestId}

        Args:
            request_id (int): The request ID.

        Returns:
            requests.Response: The response object containing the credential details.
        """

        endpoint = f"/Credentials/{request_id}"
        print_url = (
            f"{self._authentication._api_url}/Credentials/{'*' * len(str(request_id))}"
        )

        utils.print_log(
            self._logger,
            f"Calling get_credential_by_request_id endpoint: {print_url}",
            logging.DEBUG,
        )
        response = self._run_get_request(endpoint, include_api_version=False)

        credential = response.json()
        return credential

    def request_check_in(self, request_id: int, reason: str = "") -> None:
        """
        Checks-in/releases a request before it has expired.

        API: PUT Requests/{id}/checkin.

        Args:
            request_id (int): The ID of the request to check-in/release.
            reason (str, optional): A reason or comment why the request is being
                approved. Max string length is 1000.

        Returns:
            None
        """
        endpoint = f"/Requests/{request_id}/checkin"
        print_url = (
            f"{self._authentication._api_url}/Requests/"
            f"{'*' * len(str(request_id))}/checkin"
        )

        utils.print_log(
            self._logger,
            f"Calling request_check_in endpoint: {print_url}",
            logging.DEBUG,
        )
        _ = self._run_put_request(
            endpoint,
            payload={},
            expected_status_code=204,
        )

        utils.print_log(self._logger, "Request checked in", logging.DEBUG)

    def list_by_managed_system(self, managed_system_id: int) -> list:
        """
        Returns a list of managed accounts by managed system ID.

        API: GET ManagedSystems/{systemID}/ManagedAccounts

        Args:
            managed_system_id (int): Managed system ID.

        Returns:
            list: List of managed accounts.
        """

        endpoint = f"/managedsystems/{managed_system_id}/managedaccounts"

        utils.print_log(
            self._logger,
            f"Calling list_by_managed_system endpoint: {endpoint}",
            logging.DEBUG,
        )
        response = self._run_get_request(endpoint)

        return response.json()

    def get_by_id(self, managed_account_id: int) -> dict:
        """
        Returns a managed account by ID.

        API: GET ManagedAccounts/{id}

        Args:
            managed_account_id (int): Managed account ID.

        Returns:
            dict: Managed account details.
        """

        endpoint = f"/managedaccounts/{managed_account_id}"

        utils.print_log(
            self._logger, f"Calling get_by_id endpoint: {endpoint}", logging.DEBUG
        )
        response = self._run_get_request(endpoint)

        return response.json()

    def get_managed_accounts(
        self,
        *,
        system_name: str = None,
        account_name: str = None,
        system_id: str = None,
        workgroup_name: str = None,
        application_display_name: str = None,
        ip_address: str = None,
        type: str = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> list | dict:
        """
        Get managed account(s) by system name, account name and other fields.

        API: GET ManagedAccounts.

        Args:
            system_name (str): The name of the system where the account is managed.
            account_name (str): The name of the account to retrieve.
            system_id (str): The ID of the managed system.
            workgroup_name (str): The name of the workgroup.
            application_display_name (str): The display name of the application.
            ip_address (str): The IP address of the managed asset.
            type (str): The type of the managed account to return. Options are:
                system, recent, domainlinked, database, cloud, application.
            limit (int): The number of records to return. Default is 1000.
            offset (int): The number of records to skip before returning records.
                Default is 0.

        Returns:
            list | dict: List of managed accounts if multiple accounts are found,
                otherwise, a dictionary containing a single accound data will be
                returned.

        Raises:
            exceptions.OptionsError: If provided arguments are not valid.
        """
        attributes = {
            "system_name": system_name,
            "account_name": account_name,
            "system_id": system_id,
            "workgroup_name": workgroup_name,
            "application_display_name": application_display_name,
            "ip_address": ip_address,
            "type": type,
            "limit": limit,
            "offset": offset,
        }

        params = {key.replace("_", ""): value for key, value in attributes.items()}

        if self._validator.validate(attributes, update=True):
            query_string = self.make_query_string(params)
            endpoint = f"/managedaccounts?{query_string}"
            utils.print_log(
                self._logger,
                f"Calling get_managed_accounts endpoint {endpoint}",
                logging.DEBUG,
            )
            response = self._run_get_request(endpoint, include_api_version=False)
            return response.json()
        else:
            raise exceptions.OptionsError(f"Please check: {self._validator.errors}")

    def list_by_smart_rule_id(self, smart_rule_id: int) -> list:
        """
        Returns a list of managed accounts by Smart Rule ID.

        API: GET SmartRules/{smartRuleID}/ManagedAccounts

        Args:
            smart_rule_id (int): Smart Rule ID.

        Returns:
            list: List of managed accounts.
        """

        endpoint = f"/smartrules/{smart_rule_id}/managedaccounts"

        utils.print_log(
            self._logger,
            f"Calling list_by_smart_rule_id endpoint: {endpoint}",
            logging.DEBUG,
        )
        response = self._run_get_request(endpoint)

        return response.json()

    def list_by_quick_rule_id(self, quick_rule_id: int) -> list:
        """
        Returns a list of managed accounts by Quick Rule ID.

        API: GET QuickRules/{quickRuleID}/ManagedAccounts

        Args:
            quick_rule_id (int): Quick rule ID.

        Returns:
            list: List of managed accounts.
        """

        endpoint = f"/quickrules/{quick_rule_id}/managedaccounts"

        utils.print_log(
            self._logger,
            f"Calling list_by_quick_rule_id endpoint: {endpoint}",
            logging.DEBUG,
        )
        response = self._run_get_request(endpoint)

        return response.json()
