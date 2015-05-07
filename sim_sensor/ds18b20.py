class DS18B20:
    """
    Simulates the temperature sensor
    """

    def __init__(self):
        pass

    def read_temp_raw(self):
        """
        raw results from the sensor
        :return:
        """
        return 21.34

    def read_temp(self):
        """
        Reads the current temperature from the sensor, retrying on errors
        :return:
        """
        return 21.34

    def get_current(self):
        """
        :return: float the last temperature reading
        """
        return 21.34
