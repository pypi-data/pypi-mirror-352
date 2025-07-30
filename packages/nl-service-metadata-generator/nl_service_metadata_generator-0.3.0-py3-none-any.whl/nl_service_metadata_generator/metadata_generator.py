import json
from datetime import datetime

from .codelist_lookup import (
    get_coordinate_reference_systems,
    get_inspire_fields_by_ogc_service_type,
    get_inspire_theme_label,
    get_sds_categories,
    get_service_protocol_values,
    get_spatial_dataservice_categories,
)
from nl_service_metadata_generator.constants import QUALITY_SERVICE_CONFORMANCE, SERVICE_TEMPLATE
from nl_service_metadata_generator.enums import InspireType, SchemaType, SdsType
from nl_service_metadata_generator.util import (
    camel_to_snake,
    format_xml,
    get_service_md_identifier,
    replace_servicetype_var,
    get_service_url,
    render_template,
    replace_keys,
    validate_input_json,
)

from .hvd_categories import HVDCategory


def add_dynamic_fields(data_json, ogc_service_type, is_sds_interoperable):
    md_date_stamp = datetime.today().strftime("%Y-%m-%d")

    data_json["md_date_stamp"] = md_date_stamp

    if (
        not "service_revision_date" in data_json
        or not data_json["service_revision_date"]
    ):
        data_json["service_revision_date"] = md_date_stamp
    data_json["service_type"] = ogc_service_type
    protocol_fields = get_service_protocol_values(ogc_service_type)
    data_json.update(protocol_fields)
    # trim leading and trailing whitespace from keywords.
    data_json["keywords"] = [x.strip() for x in data_json["keywords"]]

    if is_sds_interoperable:
        if not "coordinate_reference_system" in data_json:
            raise ValueError(
                "coordinateReferenceSystem field required in metadata config file when generating SDS Interoperable service metadata record"
            )
        ref_systems = get_coordinate_reference_systems()
        ref_system = ref_systems[data_json["coordinate_reference_system"]]

        data_json["ref_system_name"] = ref_system["name"]
        data_json["ref_system_uri"] = ref_system["uri"]

    if "protocol_version" in data_json:
        data_json[
            "service_protocol_full_name"
        ] = f'{data_json["service_protocol_name"]} - {data_json["protocol_version"]}'
    else:
        data_json["service_protocol_full_name"] = data_json["service_protocol_name"]

    service_access_point = get_service_url(data_json, ogc_service_type)
    data_json["service_access_point"] = service_access_point

    service_title = replace_servicetype_var(data_json, ogc_service_type, "service_title")
    data_json["service_title"] = service_title

    service_abstract = replace_servicetype_var(data_json, ogc_service_type, "service_abstract")
    data_json["service_abstract"] = service_abstract

    service_md_identifier = get_service_md_identifier(data_json, ogc_service_type)
    data_json["md_identifier"] = service_md_identifier

    # remove keywords that are equal to spatial_dataservice_category_label (
    # these kw are already taken care of by get_inspire_fields_by_ogc_service_type
    categories = get_spatial_dataservice_categories()
    kw_to_delete = [kw for kw in data_json["keywords"] if kw in categories]
    for kw in kw_to_delete:
        data_json["keywords"].remove(kw)
    # trim leading and trailing whitespace from keywords.
    data_json["keywords"] = [kw.strip() for kw in data_json["keywords"]]


    # some inspire related fields are also mandatory in the "vanilla" NL profiel
    inspire_fields = get_inspire_fields_by_ogc_service_type(ogc_service_type)
    data_json.update(inspire_fields)

    if 'hvd_categories' in data_json and len(data_json['hvd_categories']) > 0:
        data_json['hvd_categories'] = HVDCategory().get_hvd_category_by_id_list(data_json["hvd_categories"])

    if data_json["inspire_type"] == "other":
        data_json["inspire_servicetype"] = "other"
        sds_values = get_sds_categories(
            data_json["sds_category"]
        )  # by default all other services are invokable services, see discussion here: https://github.com/INSPIRE-MIF/helpdesk/issues/25
        data_json["sds_category_uri"] = sds_values["uri"]
        data_json["sds_category"] = str(data_json["sds_category"].value)

    if "inspire_theme_uris" in data_json:
        inspire_themes = [{"uri": uri, "label": get_inspire_theme_label(uri)} for uri in data_json["inspire_theme_uris"]]
        data_json["inspire_themes"] = inspire_themes
    return data_json


def generate_service_metadata(
    constants_config_file,
    metadata_config_file,
    service_type,
    inspire_type,
    sds_type,
    csw_endpoint,
):
    with (open(metadata_config_file, "r") as md_config_file,
          open(constants_config_file, "r") as constants_config_file):
        md_config = json.loads(md_config_file.read())
        constants_config = json.loads(constants_config_file.read())

        base_config = QUALITY_SERVICE_CONFORMANCE
        validate_input_json(constants_config, SchemaType.CONSTANTS)
        validate_input_json(md_config, SchemaType.SERVICE)
        base_config.update(constants_config)

        base_config_snake = replace_keys(base_config, camel_to_snake)
        md_config_snake = replace_keys(md_config, camel_to_snake)
        md_config_snake.update(base_config_snake)

        # add variables supplied by args
        md_config_snake["inspire_type"] = inspire_type
        md_config_snake["sds_category"] = sds_type
        md_config_snake["csw_endpoint"] = csw_endpoint

        # add dynamic fields from lookup table
        is_sds_interoperable = (
            inspire_type == InspireType.OTHER and sds_type == SdsType.INTEROPERABLE
        )
        md_config_snake = add_dynamic_fields(
            md_config_snake, service_type, is_sds_interoperable
        )
        md_record = render_template(SERVICE_TEMPLATE, md_config_snake)
        return format_xml(md_record)
