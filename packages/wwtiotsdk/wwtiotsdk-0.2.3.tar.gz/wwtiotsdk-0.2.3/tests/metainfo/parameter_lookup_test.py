from wwtiotsdk.metainfo.parameter_lookup import ParameterLookup, PARAMETER_METADATA


def test_has():
    # Test that the has method correctly identifies existing and non-existing enum members
    assert ParameterLookup.has("powerVoltage") is True
    assert ParameterLookup.has("nonExistent") is False


def test_str():
    # Test that the string representation of enum members is correct
    assert str(ParameterLookup.VOLTAGE) == "powerVoltage"
    assert str(ParameterLookup.TEMPERATURE) == "temperature"


def test_repr():
    # Test that the repr representation of enum members is correct
    assert repr(ParameterLookup.VOLTAGE) == "powerVoltage"
    assert repr(ParameterLookup.TEMPERATURE) == "temperature"


def test_parameter_metadata():
    # Test that the parameter metadata is correctly defined
    assert PARAMETER_METADATA["powerVoltage"].long_name == "Voltage"
    assert PARAMETER_METADATA["powerVoltage"].unit == "V"
    assert PARAMETER_METADATA["temperature"].long_name == "Temperature"
    assert PARAMETER_METADATA["temperature"].unit == "°C"
    assert PARAMETER_METADATA["turbidity"].long_name == "Turbidity"
    assert PARAMETER_METADATA["turbidity"].unit == "NTU"
    assert PARAMETER_METADATA["trypTempCorr"].long_name == "Tryptophan Temp. Corrected"
    assert PARAMETER_METADATA["trypTempCorr"].unit == "ppb"
    assert PARAMETER_METADATA["cdomTempCorr"].long_name == "CDOM Temp. Corrected"
    assert PARAMETER_METADATA["cdomTempCorr"].unit == "µg/L"
    assert (
        PARAMETER_METADATA["electricConductivity"].long_name == "Electric Conductivity"
    )
    assert PARAMETER_METADATA["electricConductivity"].unit == "µS/cm"
    assert PARAMETER_METADATA["totalColi"].long_name == "Total Coli"
    assert PARAMETER_METADATA["totalColi"].unit == "CFU/100mL"
    assert PARAMETER_METADATA["faecalColi"].long_name == "Faecal Coli"
    assert PARAMETER_METADATA["faecalColi"].unit == "CFU/100mL"
    assert PARAMETER_METADATA["eColi"].long_name == "E Coli"
    assert PARAMETER_METADATA["eColi"].unit == "CFU/100mL"
    assert PARAMETER_METADATA["batteryLevel"].long_name == "Battery Level"
    assert PARAMETER_METADATA["batteryLevel"].unit == "%"
    assert PARAMETER_METADATA["oxygenSat"].long_name == "Oxygen Saturation"
    assert PARAMETER_METADATA["oxygenSat"].unit == "%"
    assert PARAMETER_METADATA["oxygenCon"].long_name == "Oxygen Concentration"
    assert PARAMETER_METADATA["oxygenCon"].unit == "mg/L"
    assert PARAMETER_METADATA["depth"].long_name == "Depth"
    assert PARAMETER_METADATA["depth"].unit == "m"
    assert (
        PARAMETER_METADATA["chlorophyllConcentration"].long_name
        == "Chlorophyll Concentration"
    )
    assert PARAMETER_METADATA["chlorophyllConcentration"].unit == "µg/L"
    assert (
        PARAMETER_METADATA["phycocyaninConcentration"].long_name
        == "Phycocyanin Concentration"
    )
    assert PARAMETER_METADATA["phycocyaninConcentration"].unit == "µg/L"
    assert (
        PARAMETER_METADATA["chlorophyllFluorescence"].long_name
        == "Chlorophyll Fluorescence"
    )
    assert PARAMETER_METADATA["chlorophyllFluorescence"].unit == "RFU"
    assert (
        PARAMETER_METADATA["phycocyaninFluorescence"].long_name
        == "Phycocyanin Fluorescence"
    )
    assert PARAMETER_METADATA["phycocyaninFluorescence"].unit == "RFU"
    assert PARAMETER_METADATA["entro"].long_name == "Entrococci"
    assert PARAMETER_METADATA["entro"].unit == "CFU/100mL"
    assert PARAMETER_METADATA["conductivity"].long_name == "Conductivity"
    assert PARAMETER_METADATA["conductivity"].unit == "µS/cm"
    assert PARAMETER_METADATA["salinity"].long_name == "Salinity"
    assert PARAMETER_METADATA["salinity"].unit == "ppt"
    assert PARAMETER_METADATA["TDS-KCl"].long_name == "TDS-KCl"
    assert PARAMETER_METADATA["TDS-KCl"].unit == "ppm"
