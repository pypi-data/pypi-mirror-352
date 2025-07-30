import boto3
import json
from influxdb_client_3 import InfluxDBClient3, flight_client_options
import certifi

from wwtiotsdk.influxdb.dataframe_base import DataframeBase


class InfluxDBConnector:

    def __init__(self, host: str, database: str, token: str):
        self.host = host
        self.database = database
        self.token = token
        self.client = None

    def connect(self):
        """Create the InfluxDB client"""

        fh = open(certifi.where(), "r")
        cert = fh.read()
        fh.close()

        self.client = InfluxDBClient3(
            host=self.host,
            token=self.token,
            database=self.database,
            flight_client_options=flight_client_options(tls_root_certs=cert),
        )

    def close(self):
        """Close the InfluxDB client"""
        if self.client:
            self.client.close()
            self.client = None

    def query(self, query: str) -> list[dict]:
        """Execute a query and return the result"""
        if not self.client:
            raise Exception("Client is not connected. Please call connect() first.")

        table = self.client.query(query, language="sql", mode="all")
        return table.to_pylist()

    def write(self, dataframe: DataframeBase) -> None:
        """Write records to InfluxDB"""
        if not self.client:
            raise Exception("Client is not connected. Please call connect() first.")

        precision = dataframe.get_precision()
        records = dataframe.get_influx_records()

        self.client.write(
            record=records,
            write_precision=precision,
        )

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, _exc_value, _traceback):
        if exc_type is not None:
            return False
        self.close()
        return True


def get_secret_from_aws(name: str) -> str:
    try:
        client = boto3.client("secretsmanager")
        res = client.get_secret_value(SecretId=name)
        return json.loads(res["SecretString"])["token"]
    except Exception as err:
        raise ValueError(
            f"Error occurred while fetching '{name}'secret from AWS Secrets Manager: {str(err)}"
        )
