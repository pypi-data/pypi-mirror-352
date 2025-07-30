class DataframeBase:

    def get_influx_records():
        raise NotImplementedError("This method should be implemented in subclasses.")

    def get_precision():
        raise NotImplementedError("This method should be implemented in subclasses.")
