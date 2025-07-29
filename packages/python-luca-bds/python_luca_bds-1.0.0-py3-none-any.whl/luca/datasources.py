import requests
import pandas as pd

def get_datasources(conn, type=None, system=None, page=1, size=25, return_pd=True):
    """
    Retrieves datasources from the server based on provided filtration parameters.
    Args:
        conn (object): Connection object with server URL and headers.
        type (str, optional): Filter by type.
        system (int, optional): Filter by system ID.
        page (int, optional): Page number for pagination.
        size (int, optional): Page size for pagination.
        return_pd (bool, optional): Return data as pandas structure if True.
    Returns:
        list | DataFrame | Series: Datasources information, including IDs and metadata.
    """
    params = {"type": type, "system": system, "page": page, "size": size}
    params = {key: value for key, value in params.items() if value is not None}
    response = requests.get(conn.server_url + "/v1/datasources", headers={**conn.headers(), 'accept': '*/*'}, params=params)
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}, {response.text}")
    data = [{
        'id': item['id'],
        'name': item['name'],
        'description': item['description'] if 'description' in item else '',
        'systemType': item['systemType'],
        'operationType': item['operationType'],
        'environment': item['environment']['name'],
        'system': item['system']['id'] if 'system' in item else ''
        } for item in response.json()['items']]
    if return_pd and len(data) > 0:
        data = pd.DataFrame(data) if len(data) > 1 else pd.Series(data[0])
    return data

def get_datasource(conn, id, return_pd=True):
    """
    Retrieves a specific chart by its ID and returns its detailed data.
    Args:
        conn (object): Connection object with server URL and headers.
        id (int): Unique identifier of the datasource.
        return_pd (bool, optional): Return data as pandas structure if True.
    Returns:
        dict | Series: Datasource details, like name or description.
    """
    response = requests.get(conn.server_url + f"/v1/datasources/{id}", headers=conn.headers())
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}, {response.text}")
    item = response.json()
    data = {
        'id': item['id'],
        'name': item['name'],
        'description': item['description'] if 'description' in item else '',
        'systemType': item['systemType'],
        'operationType': item['operationType'],
        'environment': item['environment']['name'],
        'system': item['system']['id'] if 'system' in item else '',
        'type': item['resource']['type'],
        'urlDomain': item['resource']['urlDomain'],
        'baseUrl': item['resource']['baseUrl'],
        'protocol': item['resource']['protocol'],
        'securityType': item['resource']['securityType'],
        'users': item['users']
        }
    data['users'] = [(inp['id'], inp['username'], inp['email'], inp['enabled']) for inp in data['users']]
    if return_pd:
        data = pd.Series(data)
    return data