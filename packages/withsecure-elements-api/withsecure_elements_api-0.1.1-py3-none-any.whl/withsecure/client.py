"""
WithSecure Elements API Client Module.

This module provides a Python interface to interact with the WithSecure Elements API.
It allows management of organizations, devices, security incidents, and security events.
"""

import requests
import urllib.parse
from datetime import datetime
from requests.auth import HTTPBasicAuth

from withsecure import control
from withsecure import exceptions
from withsecure.representation import DeviceRepresentation, OrganizationRepresentation, IncidentRepresentation

# Base URL for the WithSecure Elements API
API_URL = 'https://api.connect.withsecure.com'

class Client:
    """
    Main client for the WithSecure Elements API.
    
    This class handles authentication and all interactions with the API.
    It provides methods to access various API functionalities.
    """
    _auth_token = None

    def __init__(self, client_id=None, secret_id=None, url=None, json_output=False):
        """
        Initialize the WithSecure Elements client.
        
        Args:
            client_id (str): Client ID for authentication
            secret_id (str): Secret key for authentication
            url (str, optional): Custom API URL. Defaults to API_URL
            json_output (bool): If True, returns raw JSON results
            
        Raises:
            InvalidParameters: If client_id or secret_id is not provided
        """
        if not (client_id or secret_id):
            raise exceptions.InvalidParameters("client_id and secret_id must be defined")

        self.client_id = client_id
        self.secret_id = secret_id
        self.json_output = json_output
        self.url = url or API_URL

    def _headers(self):
        """
        Generate HTTP headers required for API requests.
        
        Returns:
            dict: Dictionary containing authentication headers
        """
        if not self._auth_token:
            return {}

        return {
            'Authorization': 'Bearer %s' % self._auth_token
        }

    def _handle_response(self, response):
        """
        Handle API response and raise appropriate exceptions.
        
        Args:
            response (requests.Response): The API response
            
        Returns:
            dict: The JSON response data
            
        Raises:
            AuthenticationError: If authentication fails
            ResourceNotFound: If the requested resource is not found
            RateLimitExceeded: If API rate limits are exceeded
            ServerError: If the server returns an error
            ClientError: If there's a client-side error
        """
        if response.status_code == 401:
            raise exceptions.AuthenticationError("Authentication failed")
        if response.status_code == 403:
            raise exceptions.ForbiddenError("Forbidden", status_code=403, response=response)
        elif response.status_code == 404:
            raise exceptions.ResourceNotFound("Resource not found", status_code=404, response=response)
        elif response.status_code == 429:
            raise exceptions.RateLimitExceeded("Rate limit exceeded", status_code=429, response=response)
        elif 500 <= response.status_code < 600:
            raise exceptions.ServerError(f"Server error: {response.status_code}", status_code=response.status_code, response=response)
        elif 400 <= response.status_code < 500:
            raise exceptions.ClientError(f"Client error: {response.status_code}", status_code=response.status_code, response=response)

        try:
            data = response.json()
        except ValueError as e:
            raise exceptions.ClientError(f"Invalid JSON response: {str(e)}", response=response)

        if 'error' in data:
            raise exceptions.APIError(data['error'], status_code=response.status_code, response=response)

        return data

    def call_api(self, method: str, endpoint: str, payload={}, api_limit=None, json=True, aggregate=False):
        """
        Execute an API request with pagination handling.
        
        Args:
            method (str): HTTP method ('GET' or 'POST')
            endpoint (str): API endpoint
            payload (dict): Data to send with the request
            api_limit (int): Maximum number of items per request
            
        Returns:
            list: List of results
            
        Raises:
            APIError: If the API request fails
            AuthenticationError: If authentication fails
            ResourceNotFound: If the requested resource is not found
            RateLimitExceeded: If API rate limits are exceeded
            ServerError: If the server returns an error
            ClientError: If there's a client-side error
        """
        if not self._auth_token:
            raise exceptions.AuthenticationError("Not authenticated. Call authenticate() first.")

        data = []
        nextAnchor = None
        limit = payload.get('limit')

        if not limit or limit > api_limit:
            payload['limit'] = api_limit

        while True:
            if nextAnchor:
                payload['anchor'] = nextAnchor

            url = urllib.parse.urljoin(self.url, endpoint)
            headers = self._headers()
            if aggregate:
                headers['Accept'] = 'application/vnd.withsecure.aggr+json'
            
            try:
                if method == 'GET':
                    resp = requests.get(url, params=payload, headers=headers)
                elif method == 'POST':
                    if json:
                        resp = requests.post(url, json=payload, headers=headers)
                    else:
                        resp = requests.post(url, data=payload, headers=headers)
                elif method == 'DELETE':
                    if json:
                        resp = requests.delete(url, json=payload, headers=headers)
                    else:
                        resp = requests.delete(url, data=payload, headers=headers)
                elif method == 'PATCH':
                    resp = requests.patch(url, json=payload, headers=headers)
                else:
                    raise exceptions.ClientError(f"Unsupported HTTP method: {method}")

                dj = self._handle_response(resp)
                
                if dj.get('items'):
                    data.extend(dj.get('items', []))
                elif dj.get('items') != [] and dj:
                    data = dj

                nextAnchor = dj.get('nextAnchor')
                if not nextAnchor or (limit and len(data) >= limit):
                    break

            except requests.RequestException as e:
                raise exceptions.ClientError(f"Request failed: {str(e)}")

        return data

    def authenticate(self, read_write=False):
        """
        Authenticate the client with the WithSecure Elements API.
        
        Args:
            read_write (bool): If True, requests write permissions in addition to read permissions
            
        Returns:
            bool: True if authentication successful
            
        Raises:
            AuthenticationError: If authentication fails
        """
        endpoint = '/as/token.oauth2'

        # Define scope based on read_write flag
        scope = 'connect.api.read'
        if read_write:
            scope = 'connect.api.read connect.api.write'

        # Authenticate
        try:
            basic = HTTPBasicAuth(self.client_id, self.secret_id)
            data = {
                'grant_type': 'client_credentials',
                'scope': scope
            }
            auth_url = urllib.parse.urljoin(self.url, endpoint)
            resp = requests.post(auth_url, data=data, auth=basic)
            
            auth_data = self._handle_response(resp)
            self._auth_token = auth_data.get('access_token')
            
            if not self._auth_token:
                raise exceptions.AuthenticationError("No access token in response")
            
        except requests.RequestException as e:
            raise exceptions.AuthenticationError(f"Authentication request failed: {str(e)}")

    # Organizations
    def get_organizations(self, organization_type: str = 'company', organization_id: str = None, limit: int =200):
        """           
        Retrieve the list of organizations.
        
        Args:
            organization_type (str): Type of organization to retrieve
            organization_id (str): Specific organization ID
            limit (int): Maximum number of organizations to retrieve
            
        Returns:
            list: List of organizations

        Raises:
            InvalidParameters: If organization type is invalid
        """
        # Validate organization type
        if not control.check_allowed_values(control.allowed_organization_types, organization_type):
            raise exceptions.InvalidParameters(f"Invalid organization type: {organization_type}, allowed values are: {', '.join(control.allowed_organization_types)}")

        # Retrieve organizations
        endpoint = '/organizations/v1/organizations'
        params = {
            'organizationId': organization_id,
            'type': organization_type,
            'limit': limit
        }
        organizations = self.call_api('GET', endpoint, params, api_limit=200)

        # Return raw JSON if requested
        if self.json_output:
            return organizations

        # Else, convert to Organization objects
        results = []
        for org in organizations:
            org_object = Organization.from_dict(org)
            org_object.client = self
            results.append(org_object)
        return results

    def get_organization_by_id(self, organization_id: str):
        """
        Retrieve an organization by its ID.
        """
        endpoint = '/organizations/v1/organizations'
        params = {
            'organizationId': organization_id
        }
        orgs = self.get_organizations(organization_id=organization_id, limit=1)
        if orgs:
            return orgs[0]
        else:
            raise exceptions.ResourceNotFound(f"Organization with ID {organization_id} not found")    

    # Devices
    def get_devices(self, organization_id: str = None, device_id: str = None, device_type: str = None,
                    state: str = None, name: str = None, serial_number: str = None, online: bool = None,
                    label: str = None, client_version: str = None,
                    protection_status_overview: str = None,
                    patch_overall_state=None,  public_ip_address=None,  os_name=None, ad_group=None,
                    subscription_key=None, limit=200):
        """
        Retrieve the list of devices with optional filters.
        
        Args:
            organization_id (str): Organization ID
            device_id (str): Specific device ID
            device_type (DeviceType): Device type
            state (DeviceStatus): Device state
            name (str): Device name
            serial_number (str): Serial number
            online (bool): Connection state
            label (str): Device label
            client_version (str): Client version
            protection_status_overview (ProtectionStatusOverview): Protection status
            patch_overall_state: Overall patch state
            public_ip_address (str): Public IP address
            os_name (str): Operating system name
            ad_group (str): Active Directory group
            subscription_key (str): Subscription key
            limit (int): Maximum number of devices to retrieve
            
        Returns:
            tuple: (list of devices, errors)
        """
        # Validate device type
        if device_type and device_type not in control.allowed_device_types:
            raise exceptions.InvalidParameters(f"Invalid device type: {device_type}, allowed values are: {', '.join(control.allowed_device_types)}")

        # Validate protection status overview
        if protection_status_overview and protection_status_overview not in control.allowed_protection_status_overview:
            raise exceptions.InvalidParameters(f"Invalid protection status overview: {protection_status_overview}, allowed values are: {', '.join(control.allowed_protection_status_overview)}")

        # Retrieve devices
        endpoint = '/devices/v1/devices'
        params = {
            'organizationId': organization_id,
            'deviceId': device_id,
            'type': device_type,
            'state': state,
            'name': name,
            'serialNumber': serial_number,
            'online': online,
            'label': label,
            'clientVersion': client_version,
            'protectionStatusOverview': protection_status_overview,
            'patchOverallState': patch_overall_state,
            'publicIpAddress': public_ip_address,
            'osName': os_name,
            'activeDirectoryGroup': ad_group,
            'subscriptionKey': subscription_key,
            'limit': limit
        }
        devices = self.call_api('GET', endpoint, params, api_limit=200)

        # Return raw JSON if requested
        if self.json_output:
            return devices
        
        # Else, convert to Device objects
        results = []
        for device in devices:
            dev_object = Device.from_dict(device)
            dev_object.client = self
            results.append(dev_object)

        return results
    
    def get_device_by_id(self, device_id: str):
        '''
        Retrieve a device by its ID.
        
        Args:
            device_id (str): The ID of the device to retrieve
            
        Returns:
            Device: The device object

        Raises:
            ResourceNotFound: If device is not found
        '''
        devices = self.get_devices(device_id=device_id, limit=1)
        if devices:
            return devices[0]
        else:
            raise exceptions.ResourceNotFound(f"Device with ID {device_id} not found")
    
    def devices_count(self, group_by: str = 'protectionStatus', organization_id: str = None, online: bool = None,  
                      label: str = None, client_version: str = None, protection_status_overview: str = None,):
        '''
        Count the number of devices.
        
        Args:
            count_by (str): The field to count by
            organization_id (str): Organization ID
            online (bool): Online status
            label (str): Device label
            client_version (str): Client version
            protection_status_overview (str): Protection status overview
        '''
        if group_by not in control.allowed_devices_group_by:
            raise exceptions.InvalidParameters(f"Invalid group by: {group_by}, allowed values are: {', '.join(control.allowed_devices_group_by)}")
        
        endpoint = '/devices/v1/devices'
        params = {
            'organizationId': organization_id,
            'online': online,
            'label': label,
            'clientVersion': client_version,
            'protectionStatusOverview': protection_status_overview,
            'count': group_by,
        }
        return self.call_api('GET', endpoint, params, aggregate=True)


    def devices_histogram(self, organization_id: str = None, online: bool = None, label: str = None, 
                          client_version: str = None, protection_status_overview: str = None,):
        '''
        Retrieve the histogram of devices.
        '''
        endpoint = '/devices/v1/devices'
        params = {
            'organizationId': organization_id,
            'online': online,
            'label': label,
            'clientVersion': client_version,
            'protectionStatusOverview': protection_status_overview,
            'histogram': 'protectionStatus',
        }
        return self.call_api('GET', endpoint, params, aggregate=True)

    # Operations
    def get_device_operations(self, device_id: str):
        '''
        Retrieve the list of operations for a device.
        
        Args:
            device_id (str): The ID of the device to retrieve operations for
            
        Returns:
            list: List of operations
        '''
        endpoint = '/devices/v1/operations'
        params = {
            'deviceId': device_id,
        }
        return self.call_api('GET', endpoint, params)

    def delete_devices(self, devices: list[str]):
        '''
        Delete a list of devices.
        
        Args:
            devices (list[str]): The IDs of the devices to delete
            
        Returns:
            list: List of deleted devices
        '''
        endpoint = '/devices/v1/devices'
        data = {
            'deviceId': devices
        }
        return self.call_api('DELETE', endpoint, data)
    
    def update_devices(self, devices: list[str], state: str = None, subscription_key: str = None):
        '''
        Update the state or subscription key of a list of devices.
        
        Args:
            devices (list[str]): The IDs of the devices to update
            state (str): The new state of the devices
            subscription_key (str): The new subscription key of the devices
            
        Returns:
            list: List of updated devices
        '''
        # Validate state and subscription key
        if state and subscription_key:
            raise exceptions.InvalidParameters("state and subscription_key cannot be used together")
        
        # Validate state
        if state and state not in control.allowed_device_states:
            raise exceptions.InvalidParameters(f"Invalid state: {state}, allowed values are: {', '.join(control.allowed_device_states)}")

        # Update devices
        endpoint = '/devices/v1/devices'
        data = {
            'state': state,
            'subscriptionKey': subscription_key,
            'targets': devices
        }
        return self.call_api('PATCH', endpoint, data)

    def trigger_device_operation(self, operation, targets=None, params={}):
        '''
        Trigger an operation on a list of devices.
        
        Args:
            operation (OperationType): The operation to trigger
            targets (list[str]): The IDs of the devices to target
            params (dict): Additional parameters for the operation

        Returns:
            list: List of operations
        '''
        # Validate operation
        if operation not in control.allowed_operations:
            raise exceptions.InvalidParameters(f"Invalid operation: {operation}, allowed values are: {', '.join(control.allowed_operations)}")
        
        # Trigger operation
        endpoint = '/devices/v1/operations'
        data = {
            'operation': operation,
            'targets': targets,
            'parameters': params
        }
        return self.call_api('POST', endpoint, data)

    # Security Events
    def get_security_events(self, organization_id=None, engine=None, engine_group=None, severity=None,
                            start_time=None, end_time=None, limit=200):
        '''
        Retrieve the list of security events.
        
        Args:
            organization_id (str): The ID of the organization to retrieve security events for
            engine (str): The engine to filter by
            engine_group (str): The engine group to filter by
            severity (str): The severity to filter by
            limit (int): The maximum number of events to retrieve
            start_time (str): The start time to filter by
            
        Returns:
            list: List of security events

        Raises:
            InvalidParameters: If engine, engine group, severity, start_time or end_time is invalid
        '''

        # Convert engine and engine_group to list if they are 'all'
        if engine == 'all':
            engine = control.allowed_engines
        if engine_group == 'all':
            engine_group = control.allowed_engine_groups

        # Validate start_time, end_time, engine, engine_group and severity
        if not start_time and not end_time:
            raise exceptions.InvalidParameters("At least start_time or end_time are required")
        if not engine and not engine_group:
            raise exceptions.InvalidParameters("At least engine or engine_group are required")
        if engine and engine_group:
            raise exceptions.InvalidParameters("engine and engine_group cannot be used together")        
        if engine and not control.check_allowed_values(control.allowed_engines, engine):
            raise exceptions.InvalidParameters(f"Invalid engine: {engine}, allowed values are: {', '.join(control.allowed_engines)}")
        if engine_group and not control.check_allowed_values(control.allowed_engine_groups, engine_group):
            raise exceptions.InvalidParameters(f"Invalid engine group: {engine_group}, allowed values are: {', '.join(control.allowed_engine_groups)}")
        if severity and not control.check_allowed_values(control.allowed_security_events_severities, severity):
            raise exceptions.InvalidParameters(f"Invalid severity: {severity}, allowed values are: {', '.join(control.allowed_security_events_severities)}")

        # Convert start_time and end_time to ISO format
        if start_time and isinstance(start_time, datetime):
            start_time = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        if end_time and isinstance(end_time, datetime):
            end_time = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        

        # Retrieve security events
        endpoint = '/security-events/v1/security-events'
        params = {
            'organizationId': organization_id,
            'engine': engine,
            'engineGroup': engine_group,
            'severity': severity,
            'persistenceTimestampStart': start_time,
            'persistenceTimestampEnd': end_time,
            'limit': limit
        }
        # TODO: Remove json=False when the API is fixed.
        # Currently the API does not support JSON input even if the documentation says it does.
        return self.call_api('POST', endpoint, params, api_limit=200, json=False)


    def security_events_count(self, group_by: str = '', organization_id=None, engine=None, engine_group=None, 
                              severity=None, start_time=None, end_time=None):
        '''
        Retrieve the count of security events.
        '''
        # Convert engine and engine_group to list if they are 'all'
        if engine == 'all':
            engine = control.allowed_engines
        if engine_group == 'all':
            engine_group = control.allowed_engine_groups

        # Validate group_by, start_time, end_time, engine and engine_group
        if group_by not in control.allowed_security_events_group_by:
            raise exceptions.InvalidParameters(f"Invalid group by: {group_by}, allowed values are: {', '.join(control.allowed_security_events_group_by)}")
        if not start_time and not end_time:
            raise exceptions.InvalidParameters("At least start_time or end_time are required")
        if not engine and not engine_group:
            raise exceptions.InvalidParameters("At least engine or engine_group are required")
        if engine and engine_group:
            raise exceptions.InvalidParameters("engine and engine_group cannot be used together")  
        if engine and not control.check_allowed_values(control.allowed_engines, engine):
            raise exceptions.InvalidParameters(f"Invalid engine: {engine}, allowed values are: {', '.join(control.allowed_engines)}")
        if engine_group and not control.check_allowed_values(control.allowed_engine_groups, engine_group):
            raise exceptions.InvalidParameters(f"Invalid engine group: {engine_group}, allowed values are: {', '.join(control.allowed_engine_groups)}")

        # Convert start_time and end_time to ISO format
        if start_time and isinstance(start_time, datetime):
            start_time = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        if end_time and isinstance(end_time, datetime):
            end_time = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        endpoint = '/security-events/v1/security-events'
        params = {
            'organizationId': organization_id,
            'engine': engine,
            'engineGroup': engine_group,
            'severity': severity,
            'persistenceTimestampStart': start_time,
            'persistenceTimestampEnd': end_time,
            'count': group_by,
        }
        return self.call_api('POST', endpoint, params, aggregate=True, json=False)

    # Incidents
    def get_incident_list(self,  organization_id=None, incident_id=None, start_time=None, end_time=None, status='all', 
                          risk_level=('medium', 'high', 'severe'), resolution=None, limit=20):
        
        '''
        Retrieve the list of incidents.
        
        Args:
            organization_id (str): The ID of the organization to retrieve incidents for
            incident_id (str): The ID of the incident to retrieve
            start_time (str): The start time to filter by
            end_time (str): The end time to filter by
            status (str): The status to filter by
            risk_level (str): The risk level to filter by
            resolution (str): The resolution to filter by
            limit (int): The maximum number of incidents to retrieve

        Returns:
            list: List of incidents

        Raises:
            InvalidParameters: If status, resolution, or risk level is invalid
        '''
        # Add 'all' to the list of allowed values
        if status == 'all':
            status = control.allowed_incident_statuses
        if resolution == 'all':
            resolution = control.allowed_incident_resolutions
        if risk_level == 'all':
            risk_level = control.allowed_risk_levels

        # Validate status, resolution, and risk level
        if status and not control.check_allowed_values(control.allowed_incident_statuses, status):
            raise exceptions.InvalidParameters(f"Invalid status: {status}, allowed values are: {', '.join(control.allowed_incident_statuses)}")
        if resolution and not control.check_allowed_values(control.allowed_incident_resolutions, resolution):
            raise exceptions.InvalidParameters(f"Invalid resolution: {resolution}, allowed values are: {', '.join(control.allowed_incident_resolutions)}")
        if risk_level and not control.check_allowed_values(control.allowed_risk_levels, risk_level):
            raise exceptions.InvalidParameters(f"Invalid risk level: {risk_level}, allowed values are: {', '.join(control.allowed_risk_levels)}")

        # Retrieve incidents
        endpoint = '/incidents/v1/incidents'
        params = {
            'organizationId': organization_id,
            'incidentId': incident_id,
            'createdTimestampStart': start_time,
            'createdTimestampEnd': end_time,
            'status': status,
            'limit': limit,
            'riskLevel': risk_level,
            'resolution': resolution
        }
        incidents = self.call_api('GET', endpoint, params, api_limit=50)

        # Return raw JSON if requested
        if self.json_output:
            return incidents

        # Else, convert to Incident objects
        results = []
        for incident in incidents:
            inc_object = Incident.from_dict(incident)
            inc_object.client = self
            results.append(inc_object)
        return results
    
    def get_incident_by_id(self, incident_id):
        '''
        Retrieve an incident by its ID.
        
        Args:
            incident_id (str): The ID of the incident to retrieve
            
        Returns:
            Incident: The incident object or JSON if json_output is True

        Raises:
            ResourceNotFound: If incident is not found
        '''
        results = self.get_incident_list(incident_id=incident_id, limit=1, risk_level='all', resolution='all', status='all')
        if results:
            return results[0]
        else:
            raise exceptions.ResourceNotFound(f"Incident with ID {incident_id} not found")


    def get_incident_detections(self, incident_id, organization_id=None, start_time=None, end_time=None, limit=100):
        '''
        Retrieve the list of detections for an incident.
        
        Args:
            incident_id (str): The ID of the incident to retrieve detections for
            organization_id (str): The ID of the organization to retrieve detections for
            start_time (str): The start time to filter by
            end_time (str): The end time to filter by
            limit (int): The maximum number of detections to retrieve

        Returns:
            list: List of detections
        '''
        endpoint = '/incidents/v1/detections'
        params = {
            'organizationId': organization_id,
            'incidentId': incident_id,
            'createdTimestampStart': start_time,
            'createdTimestampEnd': end_time,
            'limit': limit
        }        
        return self.call_api('GET', endpoint, params, api_limit=100)

    def add_incidents_comments(self, incident_ids, comment):
        '''
        Add a comment to multiple incidents.
        
        Args:
            incident_ids (list[str]): The IDs of the incidents to add a comment to
            comment (str): The comment to add
        '''
        endpoint = '/incidents/v1/comments'
        params = {
            'targets': incident_ids,
            'comment': comment
        }
        return self.call_api('POST', endpoint, params, api_limit=10)

    def update_incidents_status(self, incident_ids, status, resolution=None):
        '''
        Update the status or resolution of multiple incidents.
        
        Args:
            incident_ids (list[str]): The IDs of the incidents to update
            status (str): The new status of the incidents
            resolution (str): The new resolution of the incidents
        '''
        # Validate status and resolution
        if not control.check_allowed_values(control.allowed_incident_statuses, status):
            raise exceptions.InvalidParameters(f"Invalid status: {status}, allowed values are: {', '.join(control.allowed_incident_statuses)}")
        if resolution and not control.check_allowed_values(control.allowed_incident_resolutions, resolution):
            raise exceptions.InvalidParameters(f"Invalid resolution: {resolution}, allowed values are: {', '.join(control.allowed_incident_resolutions)}")
        
        # Update incidents
        endpoint = '/incidents/v1/incidents'
        params = {
            'targets': incident_ids,
            'status': status,
            'resolution': resolution
        }
        return self.call_api('PATCH', endpoint, params, api_limit=10)
    
    # Whoami
    def whoami(self):
        '''
        Retrieve the information about the current user.
        
        Returns:
            dict: Information about the current user (client id, organization id)
        '''
        endpoint = '/whoami/v1/whoami'
        return self.call_api('GET', endpoint)

    # Response actions
    def create_response_action(self, organization_id, action_type, device_ids, comment, params=None):
        '''
        Create a response action.
        
        Args:
            organization_id (str): The ID of the organization to create the response action for
            action_type (str): The type of response action to create
            device_ids (list[str]): The IDs of the devices to create the response action for
            comment (str): The comment for the response action
            params (dict): Additional parameters for the response action

        Returns:
            dict: The created response action
        '''
        # Validate action type
        if action_type not in control.allowed_response_action_types:
            raise exceptions.InvalidParameters(f"Invalid action type: {action_type}, allowed values are: {', '.join(control.allowed_response_action_types)}")

        # Create response action
        endpoint = '/response-actions/v1/response-actions'
        params = {
            'organizationId': organization_id,
            'deviceIds': device_ids,
            'comment': comment,
            'parameters': params
        }
        return self.call_api('POST', endpoint, params)
    
    def list_response_actions(self, organization_id, order='desc', type=None, action_id=None, 
                              state=None, comment=None, author=None, result=None, device_id=None, limit=10):
        '''
        List response actions.
        
        Args:
            organization_id (str): The ID of the organization to list response actions for
            order (str): The order to sort the response actions by
            type (str): The type of response action to list
            action_id (str): The ID of the response action to list
            state (str): The state of the response action to list
            comment (str): The comment of the response action to list
            author (str): The author of the response action to list
            result (str): The result of the response action to list
            device_id (str): The ID of the device to list response actions for
            limit (int): The maximum number of response actions to list

        Returns:
            list: List of response actions
        '''
        if order and not control.check_allowed_values(control.allowed_response_action_orders, order, list_allowed=False):
            raise exceptions.InvalidParameters(f"Invalid order: {order}, allowed values are: {', '.join(control.allowed_response_action_orders)}")
        if state and not control.check_allowed_values(control.allowed_response_action_states, state, list_allowed=False):
            raise exceptions.InvalidParameters(f"Invalid state: {state}, allowed values are: {', '.join(control.allowed_response_action_states)}")
        if result and not control.check_allowed_values(control.allowed_response_action_results, result, list_allowed=False):
            raise exceptions.InvalidParameters(f"Invalid result: {result}, allowed values are: {', '.join(control.allowed_response_action_results)}")

        endpoint = '/response-actions/v1/responses'
        params = {
            'organizationId': organization_id,
            'order': order,
            'type': type,
            'actionId': action_id,
            'state': state,
            'comment': comment,
            'author': author,
            'result': result,
            'deviceId': device_id,
            'limit': limit
        }
        return self.call_api('GET', endpoint, params, api_limit=100)

    # Software Updates
    def query_missing_updates(self, device_id, severity=None, category=None, limit=100):
        '''
        Query missing updates for a device.
        
        Args:
            device_id (str): The ID of the device to query missing updates for
            severity (str): The severity to filter by
            category (str): The category to filter by
            limit (int): The maximum number of updates to retrieve

        Returns:
            list: List of missing updates
        '''
        if severity == 'all':
            severity = control.allowed_update_severities
        if category == 'all':
            category = control.allowed_update_categories

        # Validate severity and category
        if severity and not control.check_allowed_values(control.allowed_update_severities, severity):
            raise exceptions.InvalidParameters(f"Invalid severity: {severity}, allowed values are: {', '.join(control.allowed_update_severities)}")
        if category and not control.check_allowed_values(control.allowed_update_categories, category):
            raise exceptions.InvalidParameters(f"Invalid category: {category}, allowed values are: {', '.join(control.allowed_update_categories)}")
        
        # Query missing updates
        endpoint = '/software-updates/v1/missing-updates'
        params = {
            'deviceId': device_id,
            'severity': severity,
            'category': category,
            'limit': limit
        }
        return self.call_api('POST', endpoint, params, api_limit=200, json=False)

    # Databases
    def get_database_version(self, database_id):
        '''
        Get the latest version of a database.
        
        Args:
            database_id (str or list[str]): The ID of the database to get the latest version of

        Returns:
            dict: The version information for the given database
        '''
        endpoint = '/databases/v1/latest-versions'
        params = {
            'id': database_id
        }
        return self.call_api('GET', endpoint, params, api_limit=1)

class Organization(OrganizationRepresentation):
    def get_devices(self, **kwargs):
        '''
        Get the devices for an organization.
        
        Args:
            **kwargs: Additional arguments to pass to the get_devices method

        Returns:
            list: List of devices
        '''
        return self.client.get_devices(organization_id=self.id, **kwargs)

    def devices_count(self, **kwargs):
        '''
        Get the count of devices for an organization.
        '''
        return self.client.devices_count(organization_id=self.id, **kwargs)
    
    def devices_histogram(self, **kwargs):
        '''
        Get the histogram of devices for an organization.
        '''
        return self.client.devices_histogram(organization_id=self.id, **kwargs)

    def get_incidents(self, **kwargs):
        '''
        Get the incidents for an organization.
        
        Args:
            **kwargs: Additional arguments to pass to the get_incident_list method

        Returns:
            list: List of incidents
        '''
        return self.client.get_incident_list(organization_id=self.id, **kwargs)

    def get_security_events(self, **kwargs):
        '''
        Get the security events for an organization.
        
        Args:
            **kwargs: Additional arguments to pass to the get_security_events method

        Returns:
            list: List of security events
        '''
        return self.client.get_security_events(organization_id=self.id, **kwargs)

    def security_events_count(self, **kwargs):
        '''
        Get the count of security events for an organization.
        '''
        return self.client.security_events_count(organization_id=self.id, **kwargs)

class Incident(IncidentRepresentation):
    def get_detections(self, start_time=None, end_time=None, limit=100):
        '''
        Get the detections for an incident.
        
        Args:
            start_time (str): The start time to filter by
            end_time (str): The end time to filter by
            limit (int): The maximum number of detections to retrieve

        Returns:
            list: List of detections
        '''
        return self.client.get_incident_detections(incident_id=self.id, start_time=start_time, end_time=end_time, limit=limit)
    
    def add_comment(self, comment):
        '''
        Add a comment to an incident.
        
        Args:
            comment (str): The comment to add
        '''
        return self.client.add_incidents_comments([self.id], comment)
    
    def update_status(self, status, resolution=None):
        '''
        Update the status or resolution of an incident.
        
        Args:
            status (str): The new status of the incident
            resolution (str): The new resolution of the incident
        '''
        return self.client.update_incidents_status([self.id], status, resolution)


class Device(DeviceRepresentation):
    def trigger_operation(self, operation, params=None):
        '''
        Trigger an operation on a device.
        
        Args:
            operation (str): The operation to trigger
            params (dict): Additional parameters for the operation
        '''
        return self.client.trigger_device_operation(operation, [self.id], params)
    
    def isolate(self, message=None):
        '''
        Isolate a device.
        
        Args:
            message (str): The message to display to the user
        '''
        return self.trigger_operation('isolateFromNetwork', params={'message': message})

    def release(self):
        '''
        Release a device from network isolation.
        '''
        return self.trigger_operation('releaseFromNetworkIsolation')
    
    def assign_profile(self, profile_id):
        '''
        Assign a profile to a device.
        
        Args:
            profile_id (str): The ID of the profile to assign
        '''
        return self.trigger_operation('assignProfile', params={'profileId': profile_id})
    
    def scan_for_malware(self):
        '''
        Scan device for malware.
        '''
        return self.trigger_operation('scanForMalware')
    
    def show_message(self, message):
        '''
        Show a message to a device.
        
        Args:
            message (str): The message to display to the user
        '''
        return self.trigger_operation('showMessage', params={'message': message})
    
    def turn_on_feature(self, feature, turn_on_timeout: int):
        '''
        Turn on a feature on a device.
        
        Args:
            feature (str): The feature to turn on
            turn_on_timeout (int): The timeout for the feature

        Returns:
            dict: The result of the operation

        Raises:
            InvalidParameters: If turn_on_timeout is not between 5 and 1440 minutes or feature is invalid
        '''
        # Validate turn_on_timeout
        if not 5 < turn_on_timeout < 1440:
            raise exceptions.InvalidParameters("turn_on_timeout must be between 5 and 1440 minutes")
        if feature not in control.allowed_features:
            raise exceptions.InvalidParameters(f"Invalid feature: {feature}, allowed values are: {', '.join(control.allowed_features)}")
        
        # Turn on feature
        return self.trigger_operation('turnOnFeature', params={'feature': feature, 'turnOnTimeout': turn_on_timeout})
    
    def collect_diagnostic_file(self, consent_message: str):
        '''
        Collect a diagnostic file from a device.
        
        Args:
            consent_message (str): The consent message to display to the user

        Returns:
            dict: The result of the operation
        '''
        return self.trigger_operation('collectDiagnosticFile', params={'consentMessage': consent_message})

    def get_operations(self):
        '''
        Get the operations for a device.
        
        Returns:
            list: List of operations
        '''
        return self.client.get_device_operations(self.id)

    def delete(self):
        '''
        Delete the device by removing subscription key.
        '''
        return self.client.delete_devices([self.id])
    
    def update_state(self, state: str):
        '''
        Update the state of a device.
        
        Args:
            state (str): The new state of the device

        Returns:
            dict: The result of the operation

        Raises:
            InvalidParameters: If state is invalid
        '''
        return self.client.update_devices([self.id], state)
    
    def change_subscription_key(self, subscription_key: str):
        '''
        Change the subscription key of a device.
        
        Args:
            subscription_key (str): The new subscription key of the device

        Returns:
            dict: The result of the operation
        '''
        return self.client.update_devices([self.id], subscription_key=subscription_key)
    
    def set_blocked(self):
        '''
        Set the device to blocked state.
        '''
        return self.client.update_devices([self.id], state='blocked')
    
    def set_inactive(self):
        '''
        Set the device to inactive state.
        '''
        return self.client.update_devices([self.id], state='inactive')

    def get_missing_updates(self, severity=None, category=None, limit=100):
        '''
        Get the missing updates for a device.
        
        Args:
            severity (str): The severity to filter by
            category (str): The category to filter by
            limit (int): The maximum number of updates to retrieve

        Returns:
            list: List of missing updates

        Raises:
            InvalidParameters: If severity or category is invalid
        '''
        return self.client.query_missing_updates(self.id, severity, category, limit)
    