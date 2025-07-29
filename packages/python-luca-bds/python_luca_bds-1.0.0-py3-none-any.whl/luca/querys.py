import requests
import pandas as pd

def get_queries(conn, name=None, description=None, user=None, page=1, size=25, return_pd=True):
    """
    Retrieves custom queries from the server based on provided filtration parameters.
    Args:
        conn (object): Connection object with server URL and headers.
        name (str, optional): Filter by query name.
        description (str, optional): Filter by query description.
        user (int, optional): Filter by user ID.
        page (int, optional): Page number for pagination.
        size (int, optional): Page size for pagination.
        return_pd (bool, optional): Return data as pandas structure if True.
    Returns:
        list | DataFrame | Series: Queries information, including IDs and metadata.
    """
    params = {"name": name, "description": description, "user": user, "page": page, "size": size}
    params = {key: value for key, value in params.items() if value is not None}
    response = requests.get(conn.server_url + "/v1/customQueries", headers={**conn.headers(), 'accept': '*/*'}, params=params)
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

def get_query(conn, id, return_pd=True):
    """
    Retrieves a specific query by its ID and returns its detailed data.
    Args:
        conn (object): Connection object with server URL and headers.
        id (int): Unique identifier of the query.
        return_pd (bool, optional): Return data as pandas structure if True.
    Returns:
        dict | Series: Query details, like name or description.
    """
    response = requests.get(conn.server_url + f"/v1/customQueries/{id}", headers=conn.headers())
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
        'query': item['query'],
        'type': item['type'],
        'inputVariables': item['inputVariables'],
        'environments': item['environments']
        }
    data['inputVariables'] = [(inp['id'], inp['key'], inp['description'], inp['type']) for inp in data['inputVariables']]
    data['environments'] = [(env['id'], env['name']) for env in data['environments']]
    if return_pd:
        data = pd.Series(data)
    return data

def execute_query(conn, id, environment_id, input_variables=[], page=1, size=25, commit=True, return_pd=True):
    """
    Executes a query on a specified environment with optional input variables.
    Args:
        conn (object): Connection object with server URL and headers.
        id (int): Unique identifier of the query.
        environment_id (str): Environment in which to execute the query.
        input_variables (list, optional): Variables to be passed as input.
        page (int, optional): Page number for pagination.
        size (int, optional): Page size for pagination.
        commit (bool, optional): Whether to commit the query transaction.
        return_pd (bool, optional): Return data as pandas structure if True.
    Returns:
        tuple (list | dict | DataFrame | Series): The query result (DataFrame or Series), pagination info, and query state.
    """
    body = {"environmentId": environment_id, "inputVariables": input_variables, "pageNumber": page, "pageSize": size, "commit": commit}
    response = requests.post(conn.server_url + f"/v1/customQueries/{id}", headers=conn.headers(), json=body)
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}, {response.text}")
    item = response.json()
    data = item.get('data', {}).get('rows', [])
    pagination = item.get('data', {}).get('pagination', {})
    state = item.get('state', {})
    if return_pd:
        if data:
            data = pd.DataFrame(data) if len(data) > 1 else pd.Series(data[0])
        else:
            data = pd.Series(data)
        pagination = pd.Series(pagination)
        state = pd.Series(state)
    return (data, pagination, state)

def query(conn, environment, name=None, id=None, input_variables={}, page=1, size=25, commit=True, return_pd=True):
    """
    Executes a query by either its name or ID for a specific environment, using optional input variables.
    Args:
        conn (object): Connection object with server URL and headers.
        environment (str): Name of the environment to run the query in.
        name (str, optional): Name of the query to look up.
        id (int, optional): ID of the query to look up.
        input_variables (dict, optional): Key-value pairs for query input variables.
        page (int, optional): Page number for pagination.
        size (int, optional): Page size for pagination.
        commit (bool, optional): Whether to commit the query transaction.
        return_pd (bool, optional): Return data as pandas structure if True.
    Returns:
        tuple (list | dict | DataFrame | Series): The query result (DataFrame or Series), pagination info, and query state.
    """
    if name is None and id is None:
        raise Exception("Error: name or id must be provided")
    if name is not None and id is not None:
        raise Exception("Error: name and id cannot be provided at the same time")
    if name is not None:
        queries = get_queries(conn=conn, name=name)
        if len(queries) == 0:
            raise Exception(f"Error: Query with name {name} not found")
        if isinstance(queries, pd.DataFrame):
            raise Exception(f"Error: Multiple queries with the same name, choose on of the following optios and use id instead of name:\n{queries[['id', 'name', 'description']]}")
        id = queries.loc['id']
    query = get_query(conn=conn, id=id)
    environment_id = [env[0] for env in query['environments'] if env[1] == environment][0]
    if input_variables:
        try:
            input_variables = [{'id': filter[0], 'key': filter[1], 'type': filter[3], 'value': '\n'.join(input_variables[filter[2]]) if isinstance(input_variables[filter[2]], list) else input_variables[filter[2]]} for filter in query['inputVariables'] if filter[2] in input_variables]
        except Exception as e:
            raise Exception(f"Error: {e}. Check the filters keys")
    else:
        input_variables = []
    return execute_query(conn=conn, id=id, environment_id=environment_id, input_variables=input_variables, page=page, size=size, commit=commit, return_pd=return_pd)