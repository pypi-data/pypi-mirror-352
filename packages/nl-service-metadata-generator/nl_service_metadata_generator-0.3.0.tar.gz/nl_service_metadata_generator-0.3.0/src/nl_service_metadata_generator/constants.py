SERVICE_TEMPLATE = "iso19119_nl_profile_2.1.0.xml"
CODELIST_JSON_FILE = "data/json/codelists.json"
SERVICE_METADATA_SCHEMA = (
    "data/schema/schemas.opengis.net/csw/2.0.2/profiles/apiso/1.0.0/apiso.xsd"
)
HVD_CATEGORIES_XML_LOCAL = "data/xml/high-value-dataset-category.rdf"
HVD_CATEGORIES_XML_REMOTE = "https://op.europa.eu/o/opportal-service/euvoc-download-handler?cellarURI=http%3A%2F%2Fpublications.europa.eu%2Fresource%2Fdistribution%2Fhigh-value-dataset-category%2F20241002-0%2Frdf%2Fskos_core%2Fhigh-value-dataset-category.rdf&fileName=high-value-dataset-category.rdf"
TEMPLATES_DIR = "data/templates"
DEFAULT_CSW_ENDPOINT = "https://nationaalgeoregister.nl/geonetwork/srv/dut/csw"
QUALITY_SERVICE_CONFORMANCE = {
    "qosPerformance": 1,
    "qosAvailability": 99,
    "qosCapacity": 10,
}
