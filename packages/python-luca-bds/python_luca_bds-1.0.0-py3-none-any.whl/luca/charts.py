import requests
import pandas as pd

def get_charts(conn, name=None, description=None, user=None, query=None, page=1, size=25, return_pd=True):
    """
    Retrieves charts from the server based on provided filtration parameters.
    Args:
        conn (object): Connection object with server URL and headers.
        name (str, optional): Filter by query name.
        description (str, optional): Filter by query description.
        user (str, optional): Filter by user.
        query (int, optional): Filter by query ID.
        page (int, optional): Page number for pagination.
        size (int, optional): Page size for pagination.
        return_pd (bool, optional): Return data as pandas structure if True.
    Returns:
        list | DataFrame | Series: Charts information, including IDs and metadata.
    """
    params = {"name": name, "description": description, "user": user, "query": query, "page": page, "size": size}
    params = {key: value for key, value in params.items() if value is not None}
    response = requests.get(conn.server_url + "/v1/charts", headers={**conn.headers(), 'accept': '*/*'}, params=params)
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}, {response.text}")
    data = [{
        'id': item['id'],
        'name': item['name'],
        'description': item['description'] if 'description' in item else '',
        'state': item['state'],
        'visibility': item['visibility'],
        'creationDate': item['creationDate'],
        'modificationDate': item['modificationDate']
        } for item in response.json()['items']]
    if return_pd and len(data) > 0:
        data = pd.DataFrame(data) if len(data) > 1 else pd.Series(data[0])
    return data

def get_chart(conn, id, return_pd=True):
    """
    Retrieves a specific chart by its ID and returns its detailed data.
    Args:
        conn (object): Connection object with server URL and headers.
        id (int): Unique identifier of the chart.
        return_pd (bool, optional): Return data as pandas structure if True.
    Returns:
        dict | Series: Chart details, like name or description.
    """
    response = requests.get(conn.server_url + f"/v1/charts/{id}", headers=conn.headers())
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}, {response.text}")
    item = response.json()
    data = {
        'id': item['id'],
        'name': item['name'],
        'description': item['description'] if 'description' in item else '',
        'state': item['state'],
        'visibility': item['visibility'],
        'creationDate': item['creationDate'],
        'modificationDate': item['modificationDate'],
        'type': item['type'],
        'query': item['query']['id'],
        'inputVariables': item['query']['inputVariables'],
        'filters': item['chartFilters']
        }
    data['inputVariables'] = [(inp['id'], inp['key'], inp['description'], inp['type']) for inp in data['inputVariables']]
    data['filters'] = [(inp['id'], inp['name'], inp['defaultFilter']) for inp in data['filters']]
    if return_pd:
        data = pd.Series(data)
    return data