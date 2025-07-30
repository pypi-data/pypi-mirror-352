from brynq_sdk_brynq import BrynQ
import os
import sys
import pandas as pd
from typing import Union, List, Literal, Optional
import requests
import json

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(basedir)


class ExtractTracket(BrynQ):

    def __init__(self, system_type: Optional[Literal['source', 'target']] = None, debug: bool = False):
        """
        For the full documentation, see: https://avisi-apps.gitbook.io/tracket/api/
        """
        super().__init__()
        self.timeout = 3600
        self.headers = self.__get_headers(system_type)
        self.base_url = "https://us.production.timesheet.avisi-apps.com/api/2.0/"

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
        tracket_response.raise_for_status()

        # Return the headers with the access_token
        access_token = tracket_response.json()['access_token']
        headers = {
            'Authorization': f"Bearer {access_token}",
            'Content-Type': 'application/json'
        }

        return headers

    def get_worklogs(self, date_start: str = None, date_end: str = None, created_since: str = None, created_up_to: str = None, updated_since: str = None, updated_up_to: str = None):
        """
        Get all the worklogs from Tracket.
        :param date_start: Get all the records from a certain date and after
        :param date_end: Get all the records until a certain date
        :param created_since: Get all the records which are created since a certain date
        :param created_up_to: Get all the records which are created before a certain date
        :param updated_since: Get all the records which are updated since a certain date
        :param updated_up_to: Get all the records which are updated before a certain date
        """
        endpoint = f'{self.base_url}timeEntries?size=100&'
        if date_start:
            endpoint = f'{endpoint}fields.date.gte={date_start}&'
        if date_end:
            endpoint = f'{endpoint}fields.date.lte={date_end}&'
        if created_since:
            endpoint = f'{endpoint}fields.createdDate.gte={created_since}&'
        if created_up_to:
            endpoint = f'{endpoint}fields.createdDate.lte={created_up_to}&'
        if updated_since:
            endpoint = f'{endpoint}fields.updatedDate.gte={updated_since}&'
        if updated_up_to:
            endpoint = f'{endpoint}fields.updatedDate.lte={updated_up_to}&'
        continue_loop = True
        df = pd.DataFrame()
        full_url = endpoint
        while continue_loop:
            response = requests.get(full_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            response_data = response.json()
            worklogs = response_data.get('items')
            worklogs = worklogs if worklogs else []
            next_cursor = response_data.get('nextCursor')
            if len(worklogs) > 0:
                df_temp = pd.DataFrame(worklogs)
                df = pd.concat([df, df_temp])
            if next_cursor:
                full_url = f'{endpoint}after={next_cursor}'
            else:
                continue_loop = False
        return df

    def get_categories(self):
        """
        Get all the hour categories from Tracket.
        """
        endpoint = f'{self.base_url}categories'
        response = requests.request("GET", endpoint, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()['categories']
        df = pd.DataFrame(data)
        return df

