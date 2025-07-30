from wwtiotsdk.influxdb.connector import InfluxDBConnector
import pytest


def test_raise_exception(mocker):

    with pytest.raises(Exception) as excinfo:

        client_mock = mocker.Mock()
        client_mock.write = mocker.Mock(side_effect=Exception("Write error"))

        with InfluxDBConnector("", "", "") as client:
            client.client = client_mock
            client.write(mocker.Mock())

    assert str(excinfo.value) == "Write error"
