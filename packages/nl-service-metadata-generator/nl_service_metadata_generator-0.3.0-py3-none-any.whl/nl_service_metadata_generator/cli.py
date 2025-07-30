#!/usr/bin/env python3
import json
import logging
import os
import sys
from pathlib import Path

import click

from nl_service_metadata_generator.constants import DEFAULT_CSW_ENDPOINT
from nl_service_metadata_generator.enums import InspireType, SchemaType, SdsType, ServiceType
from nl_service_metadata_generator.hvd_categories import HVDCategory, download_rdf
from nl_service_metadata_generator.metadata_generator import generate_service_metadata
from nl_service_metadata_generator.util import get_schema, validate_service_metadata

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@cli.command(name="show-schema")
@click.argument("schema-type", type=click.Choice(SchemaType, case_sensitive=True))
def inspect_schema_command(schema_type):
    """
    Show JSON schema for input config files
    """
    schema = get_schema(schema_type)
    print(json.dumps(schema, indent=4))


@cli.command(name="generate")
@click.argument("service-type", type=click.Choice(ServiceType, case_sensitive=True))
@click.argument("inspire-type", type=click.Choice(InspireType, case_sensitive=True))
@click.argument("constants-config-file", type=click.Path(exists=True))
@click.argument("service-config-file", type=click.Path(exists=True))
@click.argument("output-file", type=click.Path(exists=False))
@click.option(
    "--csw-endpoint",
    type=str,
    default=DEFAULT_CSW_ENDPOINT,
    help=f"References to dataset metadata records will use this CSW endpoint (default val: {DEFAULT_CSW_ENDPOINT})",
)
@click.option(
    "--sds-type",
    type=click.Choice(SdsType, case_sensitive=True),
    default=SdsType.INVOCABLE,
    help="only applies when inspire-type='other'",
)
def generate_command(
    service_type: ServiceType,
    inspire_type: InspireType,
    constants_config_file,
    service_config_file,
    output_file,
    csw_endpoint,
    sds_type: SdsType,
):
    """Generate service metadata record based on **Nederlands profiel op ISO 19119 voor services versie 2.1.0**.

    CONSTANTS_CONFIG_FILE: JSON file that contains values for constant fields
    SERVICE_CONFIG_FILE: JSON file that contains values for fields that are unique for each service

    See `show-schema` command for help on config files.
    """
    try:
        md_record = generate_service_metadata(
            constants_config_file,
            service_config_file,
            service_type,
            inspire_type,
            sds_type,
            csw_endpoint,
        )
    except ValueError as e:
        log.error(f"ERROR: {e}")
        sys.exit(1)
    validation_result = validate_service_metadata(md_record)

    if validation_result:
        log.error(
            f"metadata-generator error: generated metadata is invalid, validation message: {validation_result}"
        )
        sys.exit(1)
    if output_file != "-":
        output_dir = os.path.dirname(output_file)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        if validation_result:
            output_file = f"{output_file}.invalid"
        with open(output_file, "w") as output:
            output.write(md_record)
        if validation_result:
            exit(1)
    else:
        if validation_result:
            exit(1)
        print(md_record)


@cli.command(name="show-hvd")
def inspect_schema_command():
    """
    Show Options for hvdCategories field
    """

    hvd = HVDCategory()
    for h in hvd.categories:
        print(f"{h['id']} - {h['order']:<6} {h['label']}")


@cli.command(name="download-hvd")
def inspect_schema_command():
    """
    Refresh the cache containing the high-value-dataset-category.rdf
    """

    download_rdf()


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    cli()
