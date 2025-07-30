from wwtiotsdk.influxdb.dataframe_records_3d_time_depth import (
    DataframeRecords3DTimeDepth,
)
from datetime import datetime, timezone
import pytest


def test_validate():
    # Test valid input
    obj = DataframeRecords3DTimeDepth("source", "device", "measurement")

    # Test invalid input
    with pytest.raises(ValueError):
        obj = DataframeRecords3DTimeDepth("", "device", "measurement")

    with pytest.raises(TypeError):
        obj = DataframeRecords3DTimeDepth(123, "device", "measurement")

    with pytest.raises(ValueError):
        obj = DataframeRecords3DTimeDepth("source", "", "measurement")

    with pytest.raises(ValueError):
        obj = DataframeRecords3DTimeDepth("source", "device", None)


def test_add_datapoint():
    obj = DataframeRecords3DTimeDepth("source", "device", "measurement")

    # Test valid datapoint
    obj.add_datapoint(
        datetime(2023, 10, 1, 12, 0, tzinfo=timezone.utc), "temperature", 10, 25.5
    )
    assert len(obj.datapoints) == 1
    assert obj.datapoints[0]["time"] == 1696161600000
    assert obj.datapoints[0]["parameter"] == "temperature"
    assert obj.datapoints[0]["depth"] == 10.0
    assert obj.datapoints[0]["value"] == 25.5

    obj.add_datapoint(
        datetime(2023, 10, 1, 12, 0, tzinfo=timezone.utc), "batteryLevel", -1.5, 100
    )
    assert obj.datapoints[1]["time"] == 1696161600000
    assert obj.datapoints[1]["parameter"] == "batteryLevel"
    assert obj.datapoints[1]["depth"] == -1.5
    assert obj.datapoints[1]["value"] == 100.0

    # Test invalid parameter
    with pytest.raises(ValueError):
        obj.add_datapoint(
            datetime(2023, 10, 1, 12, 0, tzinfo=timezone.utc), "invalid_param", 10, 25.5
        )

    # Test invalid value type
    with pytest.raises(TypeError):
        obj.add_datapoint(
            datetime(2023, 10, 1, 12, 0, tzinfo=timezone.utc),
            "temperature",
            10,
            "invalid_value",
        )

    # Test invalid depth type
    with pytest.raises(TypeError):
        obj.add_datapoint(
            datetime(2023, 10, 1, 12, 0, tzinfo=timezone.utc),
            "temperature",
            "invalid_depth",
            25.5,
        )

    # Depth is None
    with pytest.raises(TypeError):
        obj.add_datapoint(
            datetime(2023, 10, 1, 12, 0, tzinfo=timezone.utc),
            "temperature",
            None,
            25.5,
        )


def test_add_datapoint_null_values():
    obj = DataframeRecords3DTimeDepth("source", "device", "measurement")

    # Test valid datapoint
    obj.add_datapoint(
        datetime(2023, 10, 1, 12, 0, tzinfo=timezone.utc), "temperature", 10, None
    )
    assert len(obj.datapoints) == 1
    assert obj.datapoints[0]["time"] == 1696161600000
    assert obj.datapoints[0]["parameter"] == "temperature"
    assert obj.datapoints[0]["depth"] == 10.0
    assert obj.datapoints[0]["value"] == None


def test_add_datapoint_invalid_time():
    obj = DataframeRecords3DTimeDepth("source", "device", "measurement")
    # Test invalid timezone
    with pytest.raises(ValueError):
        obj.add_datapoint(datetime(2023, 10, 1, 12, 0), "temperature", 10, 25.5)


def test_get_influx_records():
    obj = DataframeRecords3DTimeDepth("source", "device", "measurement")
    obj.add_datapoint(
        datetime(2023, 10, 1, 12, 0, tzinfo=timezone.utc), "temperature", 10, 25.5
    )
    obj.add_datapoint(
        datetime(2023, 10, 1, 12, 1, tzinfo=timezone.utc), "turbidity", 12, 60.0
    )

    records = obj.get_influx_records(valid=True)
    assert len(records) == 2
    r0 = records[0]
    assert r0["time"] == 1696161600000
    assert r0["fields"]["valid"] == True
    assert r0["fields"]["value"] == 25.5
    assert r0["fields"]["depth"] == 10.0
    assert r0["tags"]["source"] == "source"
    assert r0["tags"]["device"] == "device"
    assert r0["tags"]["parameter"] == "temperature"
    assert r0["measurement"] == "measurement"

    r1 = records[1]
    assert r1["time"] == 1696161660000
    assert r1["fields"]["valid"] == True
    assert r1["fields"]["value"] == 60.0
    assert r1["fields"]["depth"] == 12.0
    assert r1["tags"]["source"] == "source"
    assert r1["tags"]["device"] == "device"
    assert r1["tags"]["parameter"] == "turbidity"
    assert r1["measurement"] == "measurement"


def test_get_precision():
    obj = DataframeRecords3DTimeDepth("source", "device", "measurement")
    precision = obj.get_precision()
    assert precision == "ms"
