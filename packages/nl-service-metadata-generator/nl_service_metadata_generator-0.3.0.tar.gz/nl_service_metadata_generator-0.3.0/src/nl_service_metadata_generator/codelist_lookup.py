import json

import pkg_resources

from nl_service_metadata_generator.constants import CODELIST_JSON_FILE


def get_inspire_theme_label(inspire_theme_uri):
    json_path = pkg_resources.resource_filename(__name__, CODELIST_JSON_FILE)
    with open(json_path, "r") as json_file:
        codelists_json = json.loads(json_file.read())
        inspire_themes_codelist = codelists_json["inspire_themes"]

        if inspire_theme_uri not in inspire_themes_codelist:
            raise Exception(
                f"inspire theme uri {inspire_theme_uri} unknown. See https://www.eionet.europa.eu/gemet/nl/inspire-themes/ for supported values."
            )
        return inspire_themes_codelist[inspire_theme_uri]



def get_inspire_fields_by_ogc_service_type(ogc_service_type):
    # "inspire_service_type": "view",
    json_path = pkg_resources.resource_filename(__name__, CODELIST_JSON_FILE)
    with open(json_path, "r") as json_file:
        codelists_json = json.loads(json_file.read())
        inspire_servicetypes_codelist = codelists_json["codelist_inspire_service_types"]
        for item in inspire_servicetypes_codelist:
            if ogc_service_type in item["ogc_service_types"]:
                return item


def get_service_protocol_values(service_type):
    # "service_protocol_name": "OGC:WMS",
    # "service_protocol_url": "http://www.opengeospatial.org/standards/wms"
    json_path = pkg_resources.resource_filename(__name__, CODELIST_JSON_FILE)
    with open(json_path, "r") as json_file:
        codelists_json = json.loads(json_file.read())
        inspire_servicetypes_codelist = codelists_json["codelist_protocol"]
        return inspire_servicetypes_codelist[service_type]


def get_spatial_dataservice_categories():
    json_path = pkg_resources.resource_filename(__name__, CODELIST_JSON_FILE)
    with open(json_path, "r") as json_file:
        codelists_json = json.loads(json_file.read())
        inspire_servicetypes_codelist = codelists_json["codelist_protocol"]
        categories = [
            inspire_servicetypes_codelist[key]["spatial_dataservice_category"]
            for key in inspire_servicetypes_codelist.keys()
            if "spatial_dataservice_category" in inspire_servicetypes_codelist[key]
        ]
        return categories


def get_coordinate_reference_systems():
    json_path = pkg_resources.resource_filename(__name__, CODELIST_JSON_FILE)
    with open(json_path, "r") as json_file:
        codelists_json = json.loads(json_file.read())
        return codelists_json["reference_systems"]


def get_sds_categories(sds_category):
    json_path = pkg_resources.resource_filename(__name__, CODELIST_JSON_FILE)
    with open(json_path, "r") as json_file:
        codelists_json = json.loads(json_file.read())
        sds_categories = codelists_json["codelist_sds_service_category"]
        return sds_categories[sds_category]
