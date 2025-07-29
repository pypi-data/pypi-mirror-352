from dataclasses import dataclass

import requests
from requests.auth import HTTPBasicAuth
import json


@dataclass
class AirflowClient:
    username: str
    password: str
    host: str

    def request(self, url, method="GET", data=None):
        full_url = f"{self.host}{url}"
        auth = HTTPBasicAuth(self.username, self.password)
        headers = {"Content-Type": "application/json"}

        if method == "GET":
            return requests.get(full_url, auth=auth)
        elif method == "POST":
            return requests.post(full_url, auth=auth, headers=headers, data=json.dumps(data))
        elif method == "DELETE":
            return requests.delete(full_url, auth=auth)
        else:
            raise ValueError(f"Unsupported method: {method}")

    def create_connection(self, conn_id, conn_type, host=None, login=None, password=None, schema=None, port=None,
                          extra=None):
        """
        Create a new Airflow connection.
        """
        data = {
            "connection_id": conn_id,
            "conn_type": conn_type,
            "host": host,
            "login": login,
            "password": password,
            "schema": schema,
            "port": port,
            "extra": extra
        }

        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        response = self.request("/api/v1/connections", method="POST", data=data).json()
        return response

    def get_connection(self, conn_id):
        """
        Get an existing Airflow connection.
        """
        return self.request(f"/api/v1/connections/{conn_id}", method="GET").json()

    def get_connections(self):
        """
        Get all Airflow connections.
        """
        return self.request(f"/api/v1/connections", method="GET").json()

    def delete_connection(self, conn_id):
        """
        Delete an Airflow connection.
        """
        return self.request(f"/api/v1/connections/{conn_id}", method="DELETE").json()


