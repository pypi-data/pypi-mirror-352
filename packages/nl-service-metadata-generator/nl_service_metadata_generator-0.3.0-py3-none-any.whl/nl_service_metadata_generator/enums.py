import enum


class NgrEnv(str, enum.Enum):
    PROD = "prod"
    ACC = "acc"


class SchemaType(str, enum.Enum):
    SERVICE = "service"
    CONSTANTS = "constants"


class ServiceType(str, enum.Enum):
    CSW = "csw"
    WMS = "wms"
    WMTS = "wmts"
    WFS = "wfs"
    WCS = "wcs"
    SOS = "sos"
    ATOM = "atom"
    TMS = "tms"
    OAF = "oaf"
    OAT = "oat"
    OAS = "oas"


class InspireType(str, enum.Enum):
    NETWORK = "network"
    OTHER = "other"
    NONE = "none"


class SdsType(str, enum.Enum):
    INVOCABLE = "invocable"
    INTEROPERABLE = "interoperable"
    # TODO: add support for sds harmonized services
    # HARMONISED = "harmonised"
