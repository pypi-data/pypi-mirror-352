import json
import re
from pathlib import Path

import pkg_resources
from jinja2 import Environment, PackageLoader, select_autoescape
from jsonschema import validate
from lxml import etree

from nl_service_metadata_generator.constants import SERVICE_METADATA_SCHEMA, TEMPLATES_DIR
from nl_service_metadata_generator.enums import SchemaType


def render_template(template_path, data_json):
    env = Environment(
        loader=PackageLoader(__name__, TEMPLATES_DIR),
        autoescape=select_autoescape(["xml"]),
    )
    template = env.get_template(template_path)
    result = template.render(data_json)
    return result


def camel_to_snake(input) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", input).lower()


def snake_to_camel(input: str) -> str:
    components = input.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def replace_keys(dictionary: dict, fun) -> dict:
    empty = {}
    # special case when it is called for element of array being NOT a dictionary
    if not dictionary or type(dictionary) == str:
        # nothing to do
        return dictionary
    for k, v in dictionary.items():
        if type(v) == dict:
            empty[fun(k)] = replace_keys(v, fun)
        elif type(v) == list:
            newvalues = [replace_keys(x, fun) for x in v]
            empty[fun(k)] = newvalues  # type: ignore
        else:
            empty[fun(k)] = v
    return empty


def get_schema(schema_type: SchemaType):
    json_schema_path = Path(f"data/json_schema/{schema_type.value}.schema.json")
    json_schema_path = resolve_resource_path(json_schema_path)
    with open(json_schema_path, "r") as f:
        parsed = json.load(f)
        return parsed


def get_pkg_string():
    module_name = "." + __name__.replace(Path(__file__).name.replace(".py", ""), "")
    return __name__.replace(module_name, "")

def resolve_resource_path(resource_path: Path):
    absolute_resource_path = pkg_resources.resource_filename(
        get_pkg_string(),
        str(resource_path),
    )
    return absolute_resource_path

def validate_input_json(contact_config, schema_type: SchemaType):
    json_schema = get_schema(schema_type)
    return validate(instance=contact_config, schema=json_schema)


def get_service_md_identifier(data_json, service_type):
    service_type_string = service_type.lower().replace(" ", "_")
    key = f"md_identifier_{service_type_string}"
    if not key in data_json:
        camel_key = snake_to_camel(key)
        raise ValueError(f"key {camel_key} missing in metadata config file")
    md_identifier = data_json[key]
    return md_identifier

def replace_servicetype_var(data_json, service_type, key):
    if not key in data_json:
        raise ValueError(f"key {key} missing in metadata config file")
    value = data_json[key]
    value = value.replace("$SERVICE_TYPE_UPPER", service_type.upper())
    value = value.replace("$SERVICE_TYPE_LOWER", service_type.lower())
    value = value.replace("$OAF", "OGC API Features")
    return value


def get_service_url(data_json, service_type):
    service_type_string = service_type.lower().replace(" ", "_")
    key = f"service_access_point_{service_type_string}"
    if not key in data_json:
        camel_key = snake_to_camel(key)
        raise ValueError(f"key {camel_key} missing in metadata config file")
    url = data_json[key]
    return url

def validate_xml_form(xml_string):
    result = ""
    try:
        parser = etree.XMLParser()
        etree.fromstring(xml_string.encode("utf-8"), parser=parser)
    except IOError:
        result = "Invalid File"
    # check for XML syntax errors
    except etree.XMLSyntaxError as err:
        result = "XML Syntax Error: {0}".format(err.msg)
    return result


def validate_service_metadata(xml_string):
    result = validate_xml_form(xml_string)
    if result:
        return result
    schema_path = resolve_resource_path(SERVICE_METADATA_SCHEMA)
    with open(schema_path, "rb") as xml_schema_file:
        schema_doc = etree.XML(xml_schema_file.read(), base_url=schema_path)
        schema = etree.XMLSchema(schema_doc)
        parser = etree.XMLParser(ns_clean=True, recover=True, encoding="utf-8")
        xml_string = etree.XML(xml_string.encode("utf-8"), parser=parser)
        if not schema.validate(xml_string):
            for error in schema.error_log:
                result += f"\n\terror: {error.message}, line: {error.line}, column {error.column}"
    return result


def format_xml(md_record):
    parser = etree.XMLParser(remove_comments=True, remove_blank_text=True)
    tree = etree.fromstring(md_record.encode("utf-8"), parser=parser)
    return etree.tostring(tree, pretty_print=True).decode("utf-8")
