import requests
import pandas as pd
import json

def get_systems(conn, type=None, datasourceType=None, user=None, enabled=True, page=1, size=25, return_pd=True):
    """
    Retrieves datasources from the server based on provided filtration parameters.
    Args:
        conn (object): Connection object with server URL and headers.
        type (str, optional): Filter by type.
        datasourceType (str, optional): Filter by system datasource type (bd, soap, rest, log).
        user (int, optional): Filter by user ID.
        enabled (bool, optional): Filter by enabled status.
        page (int, optional): Page number for pagination.
        size (int, optional): Page size for pagination.
        return_pd (bool, optional): Return data as pandas structure if True.
    Returns:
        list | DataFrame | Series: Datasources information, including IDs and metadata.
    """
    params = {"type": type, "system": datasourceType, "user": user, "enabled": json.dumps(enabled), "page": page, "size": size}
    params = {key: value for key, value in params.items() if value is not None}
    response = requests.get(conn.server_url + "/v1/systems", headers={**conn.headers(), 'accept': '*/*'}, params=params)
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}, {response.text}")
    data = [{
        'id': item['id'],
        'name': item['name'],
        'description': item['description'] if 'description' in item else '',
        'type': item['type'],
        'joinSystem': item['joinSystem'],
        'enabled': item['enabled'],
        'datasourcesNumber': item['datasourcesNumber']
        } for item in response.json()['items']]
    if return_pd and len(data) > 0:
        data = pd.DataFrame(data) if len(data) > 1 else pd.Series(data[0])
    return data

def get_system(conn, id, return_pd=True):
    """
    Retrieves a specific system by its ID and returns its detailed data.
    Args:
        conn (object): Connection object with server URL and headers.
        id (int): Unique identifier of the system.
        return_pd (bool, optional): Return data as pandas structure if True.
    Returns:
        dict | Series: System details, like name or description.
    """
    response = requests.get(conn.server_url + f"/v1/systems/{id}", headers=conn.headers())
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}, {response.text}")
    item = response.json()
    data = {
        'id': item['id'],
        'name': item['name'],
        'type': item['type'],
        'joinSystem': item['joinSystem'],
        'enabled': item['enabled'],
        'datasourcesNumber': item['datasourcesNumber'],
        'environments': item['environments'],
        'datasources': item['datasources']
        }
    data['environments'] = [(inp['id'], inp['name']) for inp in data['environments']]
    data['datasources'] = [(inp['id'], inp['name'], inp['operationType']) for inp in data['datasources']]
    if return_pd:
        data = pd.Series(data)
    return data