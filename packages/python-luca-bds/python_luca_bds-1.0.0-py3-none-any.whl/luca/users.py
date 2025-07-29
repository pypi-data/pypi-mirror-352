import requests
import pandas as pd
import json

def get_users(conn, username=None, email=None, enabled=True, page=1, size=25, return_pd=True):
    """
    Retrieves users from the server based on provided filtration parameters.
    Args:
        conn (object): Connection object with server URL and headers.
        username (str, optional): Filter by username.
        email (str, optional): Filter by email.
        enabled (bool, optional): Filter by enabled status.
        page (int, optional): Page number for pagination.
        size (int, optional): Page size for pagination.
        return_pd (bool, optional): Return data as pandas structure if True.
    Returns:
        list | DataFrame | Series: Users information, including IDs and metadata.
    """
    params = {"username": username, "email": email, "enabled": json.dumps(enabled), "page": page, "size": size}
    params = {key: value for key, value in params.items() if value is not None}
    response = requests.get(conn.server_url + "/v1/users", headers={**conn.headers(), 'accept': '*/*'}, params=params)
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}, {response.text}")
    data = [{
        'id': item['id'],
        'name': item['name'],
        'surname': item['surname'] if 'surname' in item else '',
        'username': item['username'],
        'email': item['email'],
        'enabled': item['enabled']
        } for item in response.json()['items']]
    if return_pd and len(data) > 0:
        data = pd.DataFrame(data) if len(data) > 1 else pd.Series(data[0])
    return data

def get_user(conn, id, return_pd=True):
    """
    Retrieves a specific user by its ID and returns its detailed data.
    Args:
        conn (object): Connection object with server URL and headers.
        id (int): Unique identifier of the system.
        return_pd (bool, optional): Return data as pandas structure if True.
    Returns:
        dict | Series: User details, like name or description.
    """
    response = requests.get(conn.server_url + f"/v1/users/{id}", headers=conn.headers())
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}, {response.text}")
    item = response.json()
    data = {
        'id': item['id'],
        'name': item['name'],
        'surname': item['surname'] if 'surname' in item else '',
        'username': item['username'],
        'email': item['email'],
        'enabled': item['enabled'],
        'permissions': item['permissions']
        }
    if return_pd:
        data = pd.Series(data)
    return data