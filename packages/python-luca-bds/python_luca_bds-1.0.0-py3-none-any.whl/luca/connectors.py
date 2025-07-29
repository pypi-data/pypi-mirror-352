from keycloak.keycloak_openid import KeycloakOpenID
from keycloak.exceptions import KeycloakAuthenticationError
import pandas as pd
import time, requests

class KeycloakConnector:
    def __init__(self, server_url, realm_name='luca-bds', client_id='luca-bds-web', client_secret_key='', verify_ssl=True):
        """
        Initializes the Keycloak connection.
        Args:
            server_url (str): Base URL for the Keycloak server.
            realm_name (str): Realm name in Keycloak.
            client_id (str): Client ID in Keycloak.
            client_secret_key (str): Secret key for the client.
            verify_ssl (bool): Whether to verify SSL certificates.
        """
        self.server_url = server_url
        self.server_url = self.server_url[:-1] if self.server_url.endswith('/') else self.server_url
        self.realm_name = realm_name
        self.client_id = client_id
        self.client_secret_key = client_secret_key
        self.verify_ssl = verify_ssl
        self.keycloak_openid = KeycloakOpenID(
            server_url=self.server_url + '/',
            client_id=self.client_id,
            realm_name=self.realm_name,
            client_secret_key=self.client_secret_key,
            verify=self.verify_ssl
        )
        self.token = None
        self.token_timestamp = 0

    def create_token(self, username, password):
        """
        Creates a new Keycloak token.
        Args:
            username (str): The username.
            password (str): The password.
        """
        try:
            self.token = self.keycloak_openid.token(username=username, password=password)
            self.token_timestamp = time.time()
        except KeycloakAuthenticationError as e:
            raise Exception(f"Authentication failed: {e}")

    def refresh_token(self):
        """
        Refreshes the current Keycloak token.
        """
        try:
            self.token = self.keycloak_openid.refresh_token(self.token['refresh_token'])
            self.token_timestamp = time.time()
        except KeycloakAuthenticationError as e:
            raise Exception(f"Token refresh failed: {e}")

    def get_token(self, username, password):
        """
        Retrieves a valid access token, creating or refreshing if necessary.
        Args:
            username (str): The username.
            password (str): The password.
        Returns:
            str: A valid access token.
        """
        if not self.token or (time.time() - self.token_timestamp) >= (self.token['expires_in'] - 60):
            self.create_token(username, password)
        return self.token['access_token']


class LucaConnector:
    def __init__(self, server_url, username, password, keycloak_connection=None):
        """
        Initializes a connection to the Luca server.
        Args:
            server_url (str): Base URL for the Luca server.
            keycloak_connection (KeycloakConnection): An existing Keycloak connection.
            username (str): The username.
            password (str): The password.
        """
        self.server_url = server_url
        self.server_url = self.server_url[:-1] if self.server_url.endswith('/') else self.server_url
        self.server_url = self.server_url[:-3] if self.server_url.endswith('/v1') else self.server_url
        self.keycloak_connection = keycloak_connection if keycloak_connection else KeycloakConnector(server_url.replace('luca-api', 'auth'))
        self.username = username
        self.password = password

    def headers(self):
        """
        Returns the headers required for the request.
        Returns:
            dict: Authorization header with the current access token.
        """
        return {"Authorization": f"Bearer {self.keycloak_connection.get_token(self.username, self.password)}"}

    def info(self, return_pd=True):
        """
        Retrieves information from the Luca server.
        Args:
            return_pd (bool): If True, returns a pandas Series; otherwise, a dict.
        Returns:
            dict or pandas.Series: Server information.
        """
        response = requests.get(self.server_url + "/v1/info", headers=self.headers())
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code}, {response.text}")
        data = response.json()
        if return_pd:
            data = pd.Series(data)
        return data