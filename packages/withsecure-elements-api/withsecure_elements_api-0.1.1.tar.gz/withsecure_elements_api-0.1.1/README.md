# WithSecure Elements API Client

A Python client library for interacting with the WithSecure Elements API. This library provides a simple interface to manage organizations, devices, security incidents, and security events in your WithSecure Elements environment.

## Installation

```bash
pip install withsecure-elements-api
```

## Features

- Interact with WithSecure Elements API
    - Organization management
    - Device management and operations
        - Device isolation and release
        - Ask for malware scanning or diagnostic file collection
        - Query missing update on device
        - Assign profile
        - Change subscription key
    - Security incident monitoring
        - Get details
        - Retrieve detections linked to incident
        - Update status and resolution
        - Add comments
    - Security event tracking
- Full support for pagination
- Handle raw JSON or Python objects
- Comprehensive error handling

## Not implemented

- Invitations

## Quick Start

### Authentication

```python
from withsecure import Client

# Initialize the client with your credentials
client = Client(
    client_id="your_client_id",
    secret_id="your_secret_id"
)

# Authenticate (read-only access)
client.authenticate()

# For read-write access
client.authenticate(read_write=True)
```

### Working with Organizations

```python
# Get all organizations
organizations = client.get_organizations()

# Get a specific organization by ID
org = client.get_organizations(organization_id="your_org_id")

# Get devices for a specific organization
devices = organizations[0].get_devices()
```

### Managing Devices

```python
# Get all devices
devices = client.get_devices()

# Get devices count
devices_count = client.devices_count()

# Get devices with filters
devices = client.get_devices(
    organization_id="your_org_id",
    device_type='computer',
    online=True,
    protection_status_overview='allOk',
    limit=100
)

# Trigger operations on devices
device = devices[0]

# Network isolation
device.isolate(message="Security maintenance")
device.release()

# Security operations
device.scan_for_malware()
device.collect_diagnostic_file(consent_message="Please approve diagnostic collection")

# Profile and subscription management
device.assign_profile(profile_id="your_profile_id")
device.change_subscription_key(subscription_key="new_key")

# Software updates
updates = device.get_missing_updates(severity="critical", limit=100)

# Device state management
device.set_blocked()
device.set_inactive()
device.update_state(state="active")
```

### Monitoring Security Incidents

```python
# Get recent incidents
incidents = client.get_incident_list(
    organization_id="your_org_id",
    status=['new', 'inProgress'],
    risk_level=["high", "severe"],
    limit=50
)

# Incident management
incident = incidents[0]

# Get incident details and detections
detections = incident.get_detections(limit=100)

# Update incident status
incident.update_status(
    status="inProgress",
)

# Add comments
incident.add_comment("Investigation in progress")

# Get incident details with all statuses
incident = client.get_incident_by_id("incident_uuid")
```

### Tracking Security Events

```python
# Get security events
events = client.get_security_events(
    organization_id="your_org_id",
    start_time=datetime.now() - timedelta(days=300),
    engine_group="edr",
    severity="high",
    limit=200
)

# Get security events count
events_count = client.security_events_count(
    organization_id="your_org_id",
    start_time=datetime.now() - timedelta(days=300),
    engine='all',
    group_by='engine',

)
```

### Working with Raw JSON

```python
# Initialize client with JSON output
client = Client(
    client_id="your_client_id",
    secret_id="your_secret_id",
    json_output=True
)

# Get raw JSON responses
devices_json = client.get_devices()
incidents_json = client.get_incident_list()
```

## Advanced Usage

### Using Organization Objects

```python
# Get an organization
orgs, errors = client.get_organizations()
org = orgs[0]

# Access organization properties
print(f"Organization: {org.name} (ID: {org.id})")

# Get devices for this organization
devices = org.get_devices()

# Get incidents for this organization
incidents = org.get_incidents()

# Get security events for this organization
events = org.get_security_events(start_time=datetime.now() - timedelta(days=300), engine='all')
```

### Working with Incidents

```python
# Get incidents and work with incident objects
incidents = client.get_incident_list()

for incident in incidents:
    print(f"Incident: {incident.name}")
    print(f"  - Status: {incident.status}")
    print(f"  - Severity: {incident.severity}")
    print(f"  - Created: {incident.created_timestamp}")
    print(f"  - Categories: {incident.categories}")
```

## Error Handling

The client uses Python's exception system for error handling. All exceptions inherit from `WithSecureError`. Here's how to handle errors:

```python
from withsecure import Client
from withsecure.exceptions import WithSecureError, AuthenticationError, ResourceNotFound, InvalidParameters

try:
    client = Client(client_id="your_client_id", secret_id="your_secret_id")
    client.authenticate()
    
    # Get devices
    devices = client.get_devices()
    
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except ResourceNotFound as e:
    print(f"Resource not found: {e}")
except InvalidParameters as e:
    print(f"Invalid parameters: {e}")
except WithSecureError as e:
    print(f"An error occurred: {e}")
```

Available exceptions:

- `WithSecureError`: Base exception for all WithSecure Elements API errors
- `AuthenticationError`: Raised when authentication fails
- `APIError`: Base exception for API-related errors
  - `ResourceNotFound`: When a requested resource is not found
  - `RateLimitExceeded`: When API rate limits are exceeded
  - `ServerError`: When the API server returns an error
  - `ClientError`: When there's an error on the client side
- `InvalidParameters`: When invalid parameters are provided (e.g., invalid timeout values, missing required parameters)

Each API error includes:
- `status_code`: HTTP status code (if applicable)
- `response`: The full response object (if applicable)
- `message`: Detailed error message

Example with detailed error handling:

```python
from withsecure import Client
from withsecure.exceptions import WithSecureError, APIError

try:
    client = Client(client_id="your_client_id", secret_id="your_secret_id")
    client.authenticate()
    
    devices = client.get_devices()
    
except APIError as e:
    print(f"API Error: {e}")
    print(f"Status Code: {e.status_code}")
    if e.response:
        print(f"Response: {e.response.text}")
except WithSecureError as e:
    print(f"WithSecure Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.
