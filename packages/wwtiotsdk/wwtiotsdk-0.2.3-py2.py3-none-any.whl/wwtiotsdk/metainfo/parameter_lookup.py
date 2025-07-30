from enum import Enum
from dataclasses import dataclass


@dataclass
class ParInfo:
    long_name: str
    unit: str


class AutoStringEnum(str, Enum):
    """
    A base Enum class that automatically casts its members to strings.
    Inherits from both `str` and `Enum`.
    """

    def __new__(cls, value, *args, **kwargs):
        obj = str.__new__(cls, value)
        obj._value_ = value
        return obj

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class ParameterLookup(AutoStringEnum):
    VOLTAGE = "powerVoltage"
    TEMPERATURE = "temperature"
    TURBIDITY = "turbidity"
    TRYP_TEMP_CORR = "trypTempCorr"
    CDOM_TEMP_CORR = "cdomTempCorr"
    ELECTRIC_CONDUCTIVITY = "electricConductivity"
    TOTAL_COLI = "totalColi"
    FAECAL_COLI = "faecalColi"
    E_COLI = "eColi"
    BATTERY_LEVEL = "batteryLevel"
    OXYGEN_SAT = "oxygenSat"
    OXYGEN_CON = "oxygenCon"
    DEPTH = "depth"
    CHLA_CON = "chlorophyllConcentration"
    CHLA_FLOUR = "chlorophyllFluorescence"
    PHYCO_CON = "phycocyaninConcentration"
    PHYCO_FLOUR = "phycocyaninFluorescence"
    ENTRO = "entro"
    CONDUCTIVITY = "conductivity"
    SALINITY = "salinity"
    TDS_KCL = "TDS-KCl"

    def __str__(self):
        return self.value

    @classmethod
    def has(cls, value: str) -> bool:
        """
        Check if the given value exists in the enum.
        :param value: The value to check.
        :return: True if the value exists, False otherwise.
        """
        return value in cls._value2member_map_


# Metadata for parameters
PARAMETER_METADATA = {
    ParameterLookup.VOLTAGE: ParInfo("Voltage", "V"),
    ParameterLookup.TEMPERATURE: ParInfo("Temperature", "°C"),
    ParameterLookup.TURBIDITY: ParInfo("Turbidity", "NTU"),
    ParameterLookup.TRYP_TEMP_CORR: ParInfo("Tryptophan Temp. Corrected", "ppb"),
    ParameterLookup.CDOM_TEMP_CORR: ParInfo("CDOM Temp. Corrected", "µg/L"),
    ParameterLookup.ELECTRIC_CONDUCTIVITY: ParInfo("Electric Conductivity", "µS/cm"),
    ParameterLookup.TOTAL_COLI: ParInfo("Total Coli", "CFU/100mL"),
    ParameterLookup.FAECAL_COLI: ParInfo("Faecal Coli", "CFU/100mL"),
    ParameterLookup.E_COLI: ParInfo("E Coli", "CFU/100mL"),
    ParameterLookup.BATTERY_LEVEL: ParInfo("Battery Level", "%"),
    ParameterLookup.OXYGEN_SAT: ParInfo("Oxygen Saturation", "%"),
    ParameterLookup.OXYGEN_CON: ParInfo("Oxygen Concentration", "mg/L"),
    ParameterLookup.DEPTH: ParInfo("Depth", "m"),
    ParameterLookup.CHLA_CON: ParInfo("Chlorophyll Concentration", "µg/L"),
    ParameterLookup.CHLA_FLOUR: ParInfo("Chlorophyll Fluorescence", "RFU"),
    ParameterLookup.PHYCO_CON: ParInfo("Phycocyanin Concentration", "µg/L"),
    ParameterLookup.PHYCO_FLOUR: ParInfo("Phycocyanin Fluorescence", "RFU"),
    ParameterLookup.ENTRO: ParInfo("Entrococci", "CFU/100mL"),
    ParameterLookup.CONDUCTIVITY: ParInfo("Conductivity", "µS/cm"),
    ParameterLookup.SALINITY: ParInfo("Salinity", "ppt"),
    ParameterLookup.TDS_KCL: ParInfo("TDS-KCl", "ppm"),
}
