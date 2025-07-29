import yaml
from typing import Optional
import numpy as np
from pydantic import BaseModel, Field, field_validator, model_validator
import pandas as pd
from enum import Enum

from .type import ValueWithDOI, Reference
from .type import init_df_state


class EmissionsMethod(Enum):
    '''
    0: Uses values provided in the meteorological forcing file (SSss_YYYY_data_tt.txt) to calculate QF. If you do not want to include QF to the calculation of surface energy balance, you should set values in the meteorological forcing file to zero to prevent calculation of QF. UMEP provides two methods to calculate QF LQF which is simpler GQF which is more complete but requires more data inputs

    1: Not recommended in this version. QF calculated according to Loridan et al. [2011] using coefficients specified. Modelled values will be used even if QF is provided in the meteorological forcing file. CO2 emission is not calculated

    2: Recommended in this version. QF calculated according to Järvi et al. [2011] using coefficients specified and diurnal patterns specified. Modelled values will be used even if QF is provided in the meteorological forcing file. CO2 emission is not calculated
    
    3: Updated Loridan et al. [2011] method using daily (not instantaneous) air temperature (HDD(id-1,3)) using coefficients specified. CO2 emission is not calculated

    4: Järvi et al. [2019] method, in addition to anthropogenic heat due to building energy use calculated by Järvi et al. [2011], that due to metabolism and traffic is also calculated using coefficients specified and diurnal patterns specified. Modelled values will be used even if QF is provided in the meteorological forcing file. CO2 emission is not calculated

    5: QF calculated using EmissionMethod = 4. Fc (both biogenic and anthropogenic) components calculated following Järvi et al. [2019]. Emissions from traffic and human metabolism calculated as a bottom up approach using coefficients specified and diurnal patterns specified. Building emissions are calculated with the aid of heating and cooling degree days. Biogenic emissions and sinks are calculated using coefficients specified
    '''
    # just a demo to show how to use Enum for emissionsmethod
    NO_EMISSIONS = 0
    L11 = 1
    J11 = 2
    L11_UPDATED = 3
    J19 = 4
    J19_UPDATED = 4
  

    def __int__(self):
        """Representation showing just the value"""
        return self.value

    def __repr__(self):
        """Representation showing the name and value"""
        return str(self.value)


class NetRadiationMethod(Enum):
    '''
    0: Uses observed values of Q* supplied in meteorological forcing file
    1: Q* modelled with L↓ observations supplied in meteorological forcing file. Zenith angle not accounted for in albedo calculation
    2: Q* modelled with L↓ modelled using cloud cover fraction supplied in meteorological forcing file [Loridan et al., 2011]. Zenith angle not accounted for in albedo calculation
    3: Q* modelled with L↓ modelled using air temperature and relative humidity supplied in meteorological forcing file [Loridan et al., 2011]. Zenith angle not accounted for in albedo calculation
    11: Same as 1 but with L↑ modelled using surface temperature Not recommended in this version
    12: Same as 2 but with L↑ modelled using surface temperature Not recommended in this version
    13: Same as 3 but with L↑ modelled using surface temperature Not recommended in this version
    100: Q* modelled with L↓ observations supplied in meteorological forcing file. Zenith angle accounted for in albedo calculation. SSss_YYYY_NARPOut.txt file produced. Not recommended in this version
    200: Q* modelled with L↓ modelled using cloud cover fraction supplied in meteorological forcing file [Loridan et al., 2011]. Zenith angle accounted for in albedo calculation. SSss_YYYY_NARPOut.txt file produced. Not recommended in this version
    300: Q* modelled with L↓ modelled using air temperature and relative humidity supplied in meteorological forcing file [Loridan et al., 2011]. Zenith angle accounted for in albedo calculation. SSss_YYYY_NARPOut.txt file produced. Not recommended in this version
    1001: Q* modelled with SPARTACUS-Surface (SS) but with L↓ modelled as in 1. Experimental in this version
    1002: Q* modelled with SPARTACUS-Surface (SS) but with L↓ modelled as in 2. Experimental in this version
    1003: Q* modelled with SPARTACUS-Surface (SS) but with L↓ modelled as in 3. Experimental in this version
    '''
    OBSERVED = 0
    LDOWN_OBSERVED = 1
    LDOWN_CLOUD = 2
    LDOWN_AIR = 3
    LDOWN_SURFACE = 11
    LDOWN_CLOUD_SURFACE = 12
    LDOWN_AIR_SURFACE = 13
    LDOWN_ZENITH = 100
    LDOWN_CLOUD_ZENITH = 200
    LDOWN_AIR_ZENITH = 300
    LDOWN_SS_OBSERVED = 1001
    LDOWN_SS_CLOUD = 1002
    LDOWN_SS_AIR = 1003

    def __int__(self):
        return self.value

    def __repr__(self):
        return str(self.value)


class StorageHeatMethod(Enum):
    '''
    0: Uses observed values of ΔQS supplied in meteorological forcing file
    1: ΔQS modelled using the objective hysteresis model (OHM) [Grimmond et al., 1991] using parameters specified for each surface type
    3: ΔQS modelled using AnOHM [Sun et al., 2017]. Not recommended in this version
    4: ΔQS modelled using the Element Surface Temperature Method (ESTM) [Offerle et al., 2005]. Not recommended in this version
    '''
    OBSERVED = 0
    OHM_WITHOUT_QF = 1
    ANOHM = 3
    ESTM = 4
    FIVE = 5
    OHM_YL = 6

    def __int__(self):
        return self.value

    def __repr__(self):
        return str(self.value)


class OhmIncQf(Enum):
    '''
    0: ΔQS modelled Q* only
    1: ΔQS modelled using Q*+QF
    '''
    EXCLUDE = 0
    INCLUDE = 1

    def __int__(self):
        return self.value

    def __repr__(self):
        return str(self.value)


class RoughnessMethod(Enum):
    '''
    TODO:
    '''
    FIXED = 1  # Fixed roughness length
    VARIABLE = 2  # Variable roughness length based on vegetation state
    THREE = 3  # Not documented
    FIVE = 5  # Not documented

    def __int__(self):
        return self.value

    def __repr__(self):
        return str(self.value)


class StabilityMethod(Enum):
    '''
    0: Not used
    1: Not used
    2: 
    Momentum:
        unstable: Dyer [1974] modified by Högström [1988]
        stable: Van Ulden and Holtslag [1985]
    Heat: Dyer [1974] modified by Högström [1988]
    Not recommended in this version.
    
    3:
    Momentum: Campbell and Norman [1998] (Eq 7.27, Pg97)
    Heat
        unstable: Campbell and Norman [1998]
        stable: Campbell and Norman [1998]
    Recommended in this version.
    
    4:
    Momentum: Businger et al. [1971] modified by Högström [1988]
    Heat: Businger et al. [1971] modified by Högström [1988]
    Not recommended in this version.
    '''
    NOT_USED = 0
    NOT_USED2 = 1
    HOEGSTROM = 2
    CAMPBELL_NORMAN = 3
    BUSINGER_HOEGSTROM = 4

    def __int__(self):
        return self.value

    def __repr__(self):
        return str(self.value)


class SMDMethod(Enum):
    '''
    0: SMD modelled using parameters specified
    1: Observed SM provided in the meteorological forcing file is used. Data are provided as volumetric soil moisture content. Metadata must be provided
    2: Observed SM provided in the meteorological forcing file is used. Data are provided as gravimetric soil moisture content. Metadata must be provided
    '''
    MODELLED = 0
    OBSERVED_VOLUMETRIC = 1
    OBSERVED_GRAVIMETRIC = 2

    def __int__(self):
        return self.value

    def __repr__(self):
        return str(self.value)


class WaterUseMethod(Enum):
    '''
    0: External water use modelled using parameters specified
    1: Observations of external water use provided in the meteorological forcing file are used.
    '''
    MODELLED = 0
    OBSERVED = 1

    def __int__(self):
        return self.value

    def __repr__(self):
        return str(self.value)


class DiagMethod(Enum):
    '''
    0: Use MOST to calculate near surface diagnostics
    1: Use RST to calculate near surface diagnostics
    2: Use a set of criteria based on plan area index, frontal area index and heights of roughness elements to determine if RSL or MOST should be used.
    '''
    MOST = 0
    RST = 1
    VARIABLE = 2

    def __int__(self):
        return self.value

    def __repr__(self):
        return str(self.value)


class FAIMethod(Enum):
    '''
    TODO: Add more detailed description for each method
    '''
    ZERO = 0 # Not documented
    FIXED = 1  # Fixed frontal area index
    VARIABLE = 2  # Variable frontal area index based on vegetation state

    def __int__(self):
        return self.value

    def __repr__(self):
        return str(self.value)


class LocalClimateMethod(Enum):
    '''
    TODO: Add more detailed description for each method
    '''
    NONE = 0
    BASIC = 1
    DETAILED = 2

    def __int__(self):
        return self.value

    def __repr__(self):
        return str(self.value)


class StebbsMethod(Enum):
    '''
    NONE = 0  # No STEBBS calculations
    BASIC = 1  # STEBBS used with default stebbs parameters
    DETAILED = 2  # STEBBS used with provided stebbs parameters from user
    '''
    NONE = 0
    DEFAULT = 1
    PROVIDED = 2

    def __int__(self):
        return self.value

    def __repr__(self):
        return str(self.value)

class SnowUse(Enum):
    '''
    DISABLED = 0  # Snow calculations are performed
    ENABLED = 1  # Snow calculations are not performed
    '''
    DISABLED = 0 
    ENABLED = 1

    def __int__(self):
        return self.value

    def __repr__(self):
        return str(self.value)


def yaml_equivalent_of_default(dumper, data):
    """Convert enum values to YAML scalar integers.

    This function is used as a YAML representer for enum classes. It converts the enum value
    to a string and represents it as a YAML integer scalar.

    Args:
        dumper: The YAML dumper instance
        data: The enum value to be converted

    Returns:
        A YAML scalar node containing the integer value of the enum
    """
    return dumper.represent_scalar("tag:yaml.org,2002:int", str(data.value))

# Register YAML representers for all enums
for enum_class in [
    NetRadiationMethod,
    EmissionsMethod,
    StorageHeatMethod,
    RoughnessMethod,
    StabilityMethod,
    SMDMethod,
    WaterUseMethod,
    DiagMethod,
    FAIMethod,
    LocalClimateMethod,
    StebbsMethod,
    SnowUse,
    OhmIncQf,
]:
    yaml.add_representer(enum_class, yaml_equivalent_of_default)


class ModelPhysics(BaseModel):
    netradiationmethod: ValueWithDOI[NetRadiationMethod] = Field(
        default=ValueWithDOI(NetRadiationMethod.LDOWN_AIR),
        description="Method used to calculate net radiation",
    )
    emissionsmethod: ValueWithDOI[EmissionsMethod] = Field(
        default=ValueWithDOI(EmissionsMethod.J11),
        description="Method used to calculate anthropogenic emissions",
    )
    storageheatmethod: ValueWithDOI[StorageHeatMethod] = Field(
        default=ValueWithDOI(StorageHeatMethod.OHM_WITHOUT_QF),
        description="Method used to calculate storage heat flux",
    )
    ohmincqf: ValueWithDOI[OhmIncQf] = Field(
        default=ValueWithDOI(OhmIncQf.EXCLUDE),
        description="Include anthropogenic heat in OHM calculations (1) or not (0)",
    )
    roughlenmommethod: ValueWithDOI[RoughnessMethod] = Field(
        default=ValueWithDOI(RoughnessMethod.VARIABLE),
        description="Method used to calculate momentum roughness length",
    )
    roughlenheatmethod: ValueWithDOI[RoughnessMethod] = Field(
        default=ValueWithDOI(RoughnessMethod.VARIABLE),
        description="Method used to calculate heat roughness length",
    )
    stabilitymethod: ValueWithDOI[StabilityMethod] = Field(
        default=ValueWithDOI(StabilityMethod.CAMPBELL_NORMAN),
        description="Method used for atmospheric stability calculation",
    )
    smdmethod: ValueWithDOI[SMDMethod] = Field(
        default=ValueWithDOI(SMDMethod.MODELLED),
        description="Method used to calculate soil moisture deficit",
    )
    waterusemethod: ValueWithDOI[WaterUseMethod] = Field(
        default=ValueWithDOI(WaterUseMethod.MODELLED),
        description="Method used to calculate water use",
    )
    diagmethod: ValueWithDOI[DiagMethod] = Field(
        default=ValueWithDOI(DiagMethod.VARIABLE),
        description="Method used for model diagnostics",
    )
    faimethod: ValueWithDOI[FAIMethod] = Field(
        default=ValueWithDOI(FAIMethod.FIXED),
        description="Method used to calculate frontal area index",
    )
    localclimatemethod: ValueWithDOI[LocalClimateMethod] = Field(
        default=ValueWithDOI(LocalClimateMethod.NONE),
        description="Method used for local climate zone calculations",
    )
    snowuse: ValueWithDOI[SnowUse] = Field(
        default=ValueWithDOI(SnowUse.DISABLED),
        description="Include snow calculations (1) or not (0)",
    )
    stebbsmethod: ValueWithDOI[StebbsMethod] = Field(
        default=ValueWithDOI(StebbsMethod.NONE),
        description="Method used for stebbs calculations",
    )

    ref: Optional[Reference] = None

    @model_validator(mode="after")
    def check_all(self) -> "ModelPhysics":
        """
        Collect and aggregate all validation checks for ModelPhysics,
        so multiple errors (if any) can be raised together
        """
        errors = []
        # storageheatmethod check
        if self.storageheatmethod == 1 and self.ohmincqf != 0:
            errors.append(
                f"\nStorageHeatMethod is set to {self.storageheatmethod} and OhmIncQf is set to {self.ohmincqf}.\n"
                f"You should switch to OhmIncQf=0.\n"
            )
        elif self.storageheatmethod == 2 and self.ohmincqf != 1:
            errors.append(
                f"\nStorageHeatMethod is set to {self.storageheatmethod} and OhmIncQf is set to {self.ohmincqf}.\n"
                f"You should switch to OhmIncQf=1.\n"
            )

        # snowusemethod check
        if self.snowuse == 1:
            errors.append(
                f"\nSnowUse is set to {self.snowuse}.\n"
                f"There are no checks implemented for this case (snow calculations included in the run).\n"
                f"You should switch to SnowUse=0.\n"
            )

        # emissionsmethod check
        # if self.emissionsmethod == 45:
        #     errors.append(
        #         f"\nEmissionsMethod is set to {self.emissionsmethod}.\n"
        #         f"There are no checks implemented for this case (CO2 calculations included in the run).\n"
        #         f"You should switch to EmissionsMethod=0, 1, 2, 3, or 4.\n"
        #     )

        if errors:
            raise ValueError("\n".join(errors))

        return self

    # We then need to set to 0 (or None) all the CO2-related parameters or rules
    # in the code and return them accordingly in the yml file.

    def to_df_state(self, grid_id: int) -> pd.DataFrame:
        """Convert model physics properties to DataFrame state format."""
        df_state = init_df_state(grid_id)

        # Helper function to set values in DataFrame
        def set_df_value(col_name: str, value: float):
            idx_str = "0"
            if (col_name, idx_str) not in df_state.columns:
                # df_state[(col_name, idx_str)] = np.nan
                df_state[(col_name, idx_str)] = None
            df_state.at[grid_id, (col_name, idx_str)] = int(value.value)

        list_attr = [
            "netradiationmethod",
            "emissionsmethod",
            "storageheatmethod",
            "ohmincqf",
            "roughlenmommethod",
            "roughlenheatmethod",
            "stabilitymethod",
            "smdmethod",
            "waterusemethod",
            "diagmethod",
            "faimethod",
            "localclimatemethod",
            "snowuse",
            "stebbsmethod",
        ]
        for attr in list_attr:
            set_df_value(attr, getattr(self, attr))
        return df_state

    @classmethod
    def from_df_state(cls, df: pd.DataFrame, grid_id: int) -> "ModelPhysics":
        """
        Reconstruct ModelPhysics from a DataFrame state format.

        Args:
            df: DataFrame containing model physics properties
            grid_id: Grid ID for the DataFrame index

        Returns:
            ModelPhysics: Instance of ModelPhysics
        """

        properties = {}

        list_attr = [
            "netradiationmethod",
            "emissionsmethod",
            "storageheatmethod",
            "ohmincqf",
            "roughlenmommethod",
            "roughlenheatmethod",
            "stabilitymethod",
            "smdmethod",
            "waterusemethod",
            "diagmethod",
            "faimethod",
            "localclimatemethod",
            "snowuse",
            "stebbsmethod",
        ]

        for attr in list_attr:
            try:
                properties[attr] = ValueWithDOI(int(df.loc[grid_id, (attr, "0")]))
            except KeyError:
                raise ValueError(f"Missing attribute '{attr}' in the DataFrame")

        return cls(**properties)


class ModelControl(BaseModel):
    tstep: int = Field(
        default=300, description="Time step in seconds for model calculations"
    )
    forcing_file: ValueWithDOI[str] = Field(
        default=ValueWithDOI("forcing.txt"),
        description="Path to meteorological forcing data file",
    )
    kdownzen: Optional[ValueWithDOI[int]] = Field(
        default=None,
        description="Use zenithal correction for downward shortwave radiation",
    )
    output_file: str = Field(
        default="output.txt", description="Path to model output file"
    )
    # daylightsaving_method: int
    diagnose: int = Field(
        default=0,
        description="Level of diagnostic output (0=none, 1=basic, 2=detailed)",
    )

    ref: Optional[Reference] = None

    @field_validator("tstep", "diagnose", mode="after")
    def validate_int_float(cls, v):
        if isinstance(v, (np.float64, np.float32)):
            return float(v)
        elif isinstance(v, (np.int64, np.int32)):
            return int(v)
        return v

    def to_df_state(self, grid_id: int) -> pd.DataFrame:
        """Convert model control properties to DataFrame state format."""
        df_state = init_df_state(grid_id)

        # Helper function to set values in DataFrame
        def set_df_value(col_name: str, value: float):
            idx_str = "0"
            if (col_name, idx_str) not in df_state.columns:
                # df_state[(col_name, idx_str)] = np.nan
                df_state[(col_name, idx_str)] = None
            df_state.at[grid_id, (col_name, idx_str)] = value

        list_attr = ["tstep", "diagnose"]
        for attr in list_attr:
            set_df_value(attr, getattr(self, attr))
        return df_state

    @classmethod
    def from_df_state(cls, df: pd.DataFrame, grid_id: int) -> "ModelControl":
        """Reconstruct model control properties from DataFrame state format."""
        instance = cls()
        for attr in ["tstep", "diagnose"]:
            value = df.loc[grid_id, (attr, "0")]
            setattr(
                instance,
                attr,
                int(value) if isinstance(value, (np.int64, np.int32)) else value,
            )
        return instance


class Model(BaseModel):
    control: ModelControl = Field(
        default_factory=ModelControl,
        description="Model control parameters including timestep, output options, etc.",
    )
    physics: ModelPhysics = Field(
        default_factory=ModelPhysics,
        description="Model physics parameters including surface properties, coefficients, etc.",
    )

    @model_validator(mode="after")
    def validate_radiation_method(self) -> "Model":
        if (
            self.physics.netradiationmethod.value == 1
            and self.control.forcing_file.value == "forcing.txt"
        ):
            raise ValueError(
                "NetRadiationMethod is set to 1 (using observed Ldown). "
                "The sample forcing file lacks observed Ldown. Use netradiation = 3 for sample forcing. "
                "If not using sample forcing, ensure that the forcing file contains Ldown and rename from forcing.txt."
                # TODO: This is a temporary solution. We need to provide a better way to catch this.
            )
        return self

    def to_df_state(self, grid_id: int) -> pd.DataFrame:
        """Convert model to DataFrame state format"""
        df_state = init_df_state(grid_id)
        df_control = self.control.to_df_state(grid_id)
        df_physics = self.physics.to_df_state(grid_id)
        df_state = pd.concat([df_state, df_control, df_physics], axis=1)
        return df_state

    @classmethod
    def from_df_state(cls, df: pd.DataFrame, grid_id: int) -> "Model":
        """Reconstruct Model from DataFrame state format."""
        # Extract control and physics parameters
        control = ModelControl.from_df_state(df, grid_id)
        physics = ModelPhysics.from_df_state(df, grid_id)

        # Create an instance using the extracted parameters
        return cls(control=control, physics=physics)
