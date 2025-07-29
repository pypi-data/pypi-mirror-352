# GRID Python SDK
Python SDK to simplify integration with GRID services: https://gridgs.com

**It's in beta state now. Please expect changes (we'll try to keep them backward-compatible).**

# Main parts
GridAuthClient (gridgs.sdk.auth.Client) - Used to authorize on GRID SSO server.

GridApiClient (gridgs.sdk.api.Client) - Client for GRID RespAPI that can work with main Grid entities.

GridEventSubscriber (gridgs.sdk.event.Subscriber) - subscriber to receive real-time events about changes in sessions (creation, deletion, starting and so on).

GridMQTTClient (gridgs.sdk.mqtt.Client) - Client for GRID MQTT API. It useful for realtime connection (receive downlink frames and send uplink frames).

# Examples how to use
## GridAuthClient
```
from keycloak import KeycloakOpenID
from gridgs.sdk.auth import Client as GridAuthClient

keycloak_openid = KeycloakOpenID(server_url="https://login.gridgs.com", client_id="grid-api", realm_name="grid")
grid_auth_client = GridAuthClient(open_id_client=keycloak_openid, username="user@gridgs.com", password="userpass", company_id=1, logger=logging.getLogger('grid_auth_client'))
```

## GridApiClient

```
from gridgs.sdk.api import Client as GridApiClient

grid_api_client = GridApiClient(base_url="https://api.gridgs.com" auth_client=grid_auth_client, logger=logging.getLogger('grid_api_client'))
```

### Get sessions
```
from gridgs.sdk.api import SortOrder, SessionQueryParams, SessionSortField

params = SessionQueryParams(
        satellite=1,
        ground_station=13,
        status=Session.STATUS_SUCCESS,
        offset=0, limit=3, 
        sort_by=SessionSortField.END_DATE, sort_order=SortOrder.ASC)
sessions_result = grid_api_client.find_sessions(params)

print(f'Total: {sessions_result.total}')
```

### Get and Iterate ALL sessions
it iterates by chunks all sessions which can be found on api based on SessionQueryParams. Default chunk size is 500. 
```
from gridgs.sdk.api import SortOrder, SessionQueryParams, SessionSortField

params = SessionQueryParams(
        offset=0, limit=1000000,
        satellite=1,
        ground_station=13,
        status=Session.STATUS_SUCCESS,
        sort_by=SessionSortField.END_DATE, sort_order=SortOrder.ASC)
for session in grid_api_client.iterate_sessions(params):
    print(session)
```


### Get session by Id
```
session = grid_api_client.find_session(session_uuid)
```

### Predict sessions
max - 100 sessions
```
from gridgs.sdk.api import NonPaginatedSessionQueryParams

params = NonPaginatedSessionQueryParams(
    satellite=1, 
    ground_station=13,
    date_from=datetime.fromisoformat("2025-01-01 00:00:00"),
    date_to=datetime.fromisoformat("2025-01-02 00:00:00"),
    min_tca_elevation=20,
    )
sessions = grid_api_client.predict_sessions(params) 
```

### Create session
```
session = Session() # A session from get_predicted_sessions
session = grid_api_client.create_session(session)
```

### Delete session
```
grid_api_client.delete_session(session_uuid)
```

### Get frames
```
from gridgs.sdk.api import SortOrder, FrameSortField, FrameQueryParams

params = FrameQueryParams(
    satellite=2, 
    ground_station=13, 
    date_from=datetime.fromisoformat("2025-02-07 00:00:00"), 
    date_to=datetime.fromisoformat("2025-02-07 00:48:00"), 
    offset=0, limit=5, 
    sort_by=FrameSortField.CREATED_AT, sort_order=SortOrder.ASC)
    )

frames_result = grid_api_client.find_frames(params) 

print(f'Total: {frames_result.total}')
```

### Get and Iterate ALL frames
it iterates by chunks all frames which can be found on api based on FrameQueryParams. Default chunk size is 500
```
from gridgs.sdk.api import SortOrder, FrameSortField, FrameQueryParams

params = FrameQueryParams(
        offset=0, limit=1000000, 
        satellite=1,
        ground_station=13,
        date_from=datetime.fromisoformat("2025-02-07 00:00:00"), 
        date_to=datetime.fromisoformat("2025-02-07 00:48:00"), 
        sort_by=FrameSortField.CREATED_AT, sort_order=SortOrder.ASC)
for frame in grid_api_client.iterate_frames(params):
    print(frame)
```

## SSL/TLS for GridEventSubscriber and GridMQTTClient
```
from gridgs.sdk.ssl import Settings as SslSettings
ssl_settings = SslSettings(version=ssl.PROTOCOL_TLSv1_2, verify=True)
```
the arguments have defaults values.

In a case of usage ssl_settings use SSL/TLS port **8883**

## GridEventSubscriber

Receive statuses of sessions

```
from gridgs.sdk.entity import SessionEvent
from gridgs.sdk.event import Subscriber as GridEventSubscriber

grid_event_subscriber = GridEventSubscriber(host="api.gridgs.com", port=1883, auth_client=grid_auth_client, ssl_settings=None, logger=logging.getLogger('grid_event_subscriber'))

def on_event(event: SessionEvent):
    session = event.session
    type = event.type # Create, Update, Delete

grid_event_subscriber.on_event(on_event)

grid_event_subscriber.run()
```

## GridMQTTClient

```
from gridgs.sdk.entity import Frame
from gridgs.sdk.mqtt import Client as GridMQTTClient

grid_mqtt_client = GridMQTTClient(host="api.gridgs.com", port=1883, auth_client=grid_auth_client, ssl_settings=None, logger=logging.getLogger('grid_event_subscriber'))

def on_downlink_frame(frame: Frame):
    pass

grid_mqtt_client.on_downlink(on_downlink_frame)

grid_mqtt_client.connect(session)
```

### Sending a frame

```
grid_mqtt_client.send(b'Uplink frame data')
```
