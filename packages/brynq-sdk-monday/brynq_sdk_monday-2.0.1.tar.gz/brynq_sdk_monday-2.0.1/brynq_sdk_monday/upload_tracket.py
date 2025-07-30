from brynq_sdk_brynq import BrynQ
import os
import sys
import pandas as pd
from typing import Union, List, Literal, Optional
import warnings
import requests
import json

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(basedir)


class UploadTracket(BrynQ):

    def __init__(self, system_type: Optional[Literal['source', 'target']] = None, debug: bool = False):
        """
        For the full documentation, see: https://avisi-apps.gitbook.io/tracket/api/
        """
        super().__init__()
        self.timeout = 3600
        self.headers = self.__get_headers(system_type)
        self.base_url = "https://us.production.timesheet.avisi-apps.com/api/2.0/"
        self.debug = debug

    def __get_headers(self, system_type):
        """
        Get the credentials for the Traket API from BrynQ, with those credentials, get the access_token for Tracket.
        Return the headers with the access_token.
        """
        # Get credentials from BrynQ
        credentials = self.interfaces.credentials.get(system="monday", system_type=system_type)
        credentials = credentials.get('data')

        # With those credentials, get the access_token from Tracket
        endpoint = 'https://us.production.timesheet.avisi-apps.com/api/2.0/oauth2/token'
        payload = json.dumps({
            "grant-type": "client-credentials",
            "monday/account-id": credentials['account_id'],
            "client-id": credentials['client_id'],
            "client-secret": credentials['client_secret']
        })
        headers = {'Content-Type': 'application/json'}
        tracket_response = requests.request("POST", endpoint, headers=headers, data=payload, timeout=self.timeout)

        # Return the headers with the access_token
        access_token = tracket_response.json()['access_token']
        headers = {
            'Authorization': f"Bearer {access_token}",
            'Content-Type': 'application/json'
        }

        return headers

    @staticmethod
    def __check_fields(data: Union[dict, List], required_fields: List, allowed_fields: List):
        if isinstance(data, dict):
            data = data.keys()

        for field in data:
            if field not in allowed_fields and field not in required_fields:
                warnings.warn('Field {field} is not implemented. Optional fields are: {allowed_fields}'.format(field=field, allowed_fields=tuple(allowed_fields)))

        for field in required_fields:
            if field not in data:
                raise ValueError('Field {field} is required. Required fields are: {required_fields}'.format(field=field, required_fields=tuple(required_fields)))

    def create_worklog(self, data: dict) -> requests.Response:
        """
        Create a new worklog in Tracket.
        :param data: A dictionary with all the required fields to create a worklog.
        """
        required_fields = ['worklogMinutes', 'worklogDate', 'itemId', 'userId']
        allowed_fields = ['worklogCategory', 'description', 'worklogBillableMinutes', 'team']
        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        url = f'{self.base_url}timeEntries'

        base_body = {
            "minutes": data['worklogMinutes'],
            "date": data['worklogDate'],
            "item": data['itemId'],
            "user": data['userId']
        }
        fields_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"category": data['worklogCategory']}) if 'worklogCategory' in data else fields_to_update
        fields_to_update.update({"description": data['description']}) if 'description' in data else fields_to_update
        fields_to_update.update({"billableMinutes": data['worklogBillableMinutes']}) if 'worklogBillableMinutes' in data else fields_to_update
        fields_to_update.update({"team": data['team']}) if 'team' in data else fields_to_update
        base_body.update(fields_to_update)

        if self.debug:
            print(json.dumps(base_body))

        response = requests.request("POST", url, data=json.dumps(base_body), headers=self.headers, timeout=self.timeout)
        return response

    def update_worklog(self, worklog_id: str, data: dict) -> requests.Response:
        """
        Get all the worklogs from Tracket.
        :param worklog_id: The ID of the worklog that you want to update.
        :param data: A dictionary with all the required fields to update a worklog.
        """
        required_fields = ['worklogMinutes', 'worklogDate', 'itemId', 'userId']
        allowed_fields = ['worklogCategory', 'description', 'worklogBillableMinutes', 'team']
        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        url = f'{self.base_url}timeEntries/{worklog_id}'

        base_body = {
            "minutes": data['worklogMinutes'],
            "date": data['worklogDate'],
            "item": data['itemId'],
            "user": data['userId']
        }
        fields_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"category": data['worklogCategory']}) if 'worklogCategory' in data else fields_to_update
        fields_to_update.update({"description": data['description']}) if 'description' in data else fields_to_update
        fields_to_update.update({"billableMinutes": data['worklogBillableMinutes']}) if 'worklogBillableMinutes' in data else fields_to_update
        fields_to_update.update({"team": data['team']}) if 'team' in data else fields_to_update
        base_body.update(fields_to_update)

        if self.debug:
            print(json.dumps(base_body))

        response = requests.request("PUT", url, data=json.dumps(base_body), headers=self.headers, timeout=self.timeout)
        return response

    def delete_worklog(self, worklog_id: str) -> requests.Response:
        """
        Get all the worklogs from Tracket.
        :param worklog_id: The ID of the worklog that you want to delete.
        """
        url = (f'{self.base_url}timeEntries/{worklog_id}')
        response = requests.request("DELETE", url, headers=self.headers, timeout=self.timeout)
        return response