from datetime import datetime, timezone
from wwtiotsdk.influxdb.dataframe_base import DataframeBase
from wwtiotsdk.metainfo.parameter_lookup import ParameterLookup


class DataframeRecords3DTimeDepth(DataframeBase):
    """
    Class to transform data into a 3D time record based format, that can be ingested into InfluxDB.
    """

    def __init__(self, source: str, device: str, measurement: str):
        """
        Initialize the DataframeRecords2DTime object.

        args:
            source (str): The source of the data.
            device (str): The device name.
            measurement (str): The measurement name.
        """
        self.source = source
        self.device = device
        self.measurement = measurement
        self.datapoints: list[dict] = []
        self._validate()

    def _validate(self) -> None:
        """
        Validate the source, device, and measurement attributes.
        """
        if not self.source or not self.device or not self.measurement:
            raise ValueError("Source, device, and measurement must be provided.")
        if (
            not isinstance(self.source, str)
            or not isinstance(self.device, str)
            or not isinstance(self.measurement, str)
        ):
            raise TypeError("Source, device, and measurement must be strings.")
        if len(self.source) == 0 or len(self.device) == 0 or len(self.measurement) == 0:
            raise ValueError("Source, device, and measurement cannot be empty strings.")

    def add_datapoint(
        self, time: datetime, parameter: str, depth: float, value: float | int | None
    ) -> None:
        """
        Add a datapoint to the 2D time record.

        args:
            time (datetime): The time of the record.
            parameter (str): The parameter name.
            depth (float): The depth of the record. (positive for depth, negative for height)
            value (float|int): The value of the parameter.
        """

        if time.tzinfo != timezone.utc:
            raise ValueError("The 'time' parameter must have a UTC timezone.")

        unix_ms = int(time.timestamp() * 1000)

        if not ParameterLookup.has(parameter):
            raise ValueError(f"Parameter '{parameter}' is not valid.")

        if not isinstance(depth, (int, float)):
            raise TypeError(
                f"Depth for parameter '{parameter}' must be an int or float."
            )
        if not isinstance(value, (int, float)) and value is not None:
            raise TypeError(
                f"Value for parameter '{parameter}' must be an int, float or None."
            )

        value = None if value is None else float(value)
        depth = float(depth)

        self.datapoints.append(
            {"time": unix_ms, "parameter": parameter, "depth": depth, "value": value}
        )

    def get_influx_records(self, valid: bool = True) -> list[dict]:
        """
        Get the InfluxDB records from the 2D time record.

        returns:
            list[dict]: The InfluxDB records.
        """
        return [
            {
                "measurement": self.measurement,
                "tags": {
                    "source": self.source,
                    "device": self.device,
                    "parameter": datapoint["parameter"],
                },
                "time": datapoint["time"],
                "fields": {
                    "depth": datapoint["depth"],
                    "value": datapoint["value"],
                    "valid": valid,
                },
            }
            for datapoint in self.datapoints
        ]

    def get_precision(self) -> str:
        """
        Get the precision of the records."
        """
        return "ms"
