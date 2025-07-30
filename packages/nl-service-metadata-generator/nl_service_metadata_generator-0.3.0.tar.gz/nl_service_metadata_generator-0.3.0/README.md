# nl-service-metadata-generator

[![PyPI version](https://badge.fury.io/py/nl-service-metadata-generator.svg)](https://pypi.org/project/nl-service-metadata-generator/)
[![GitHub
release](https://img.shields.io/github/release/PDOK/nl-service-metadata-generator.svg?include_prereleases)](https://github.com/PDOK/nl-service-metadata-generator/releases)
[![Docker Pulls](https://img.shields.io/docker/pulls/pdok/nl-service-metadata-generator)](https://hub.docker.com/repository/docker/pdok/nl-service-metadata-generator)

CLI applicatie om service metadata records te genereren die voldoen aan het [Nederlands profiel op ISO 19119 voor services versie 2.1.0](https://docs.geostandaarden.nl/md/mdprofiel-iso19119/).

CLI applicatie genereert metadata en voert schema validatie uit. Applicatie voert _geen_ schematron validatie uit (validatie op _Nederlands profiel op ISO 19119 voor services versie 2.1.0_).

Indien schema validatie faalt op de gegenereerde metadata wordt het metadata bestand weggeschreven naar `${file-destination}.invalid` (dus toevoeging van `.invalid` extensie) en zal de nl-service-metadata-generator de schema validatie foutmelding naar stdout printen en een returncode van `1` teruggeven.

## Service Types

De nl-service-metadata-generator ondersteunt de volgende service types:

- geen INSPIRE service
- INSPIRE network service
- INSPIRE other service
  - Spatial Data Service (SDS) - invocable
  - SDS - interoperable

> N.B. SDS harmonized wordt dus niet ondersteund door de nl-service-metadata-generator

## Installation

Installeer `nl-service-metadata-generator` als pip package (uitvoeren vanuit root van repository):

```pip3
pip3 install . # Add -e for development and debugging
```

Nu moet het cli command `nl-service-metadata-generator` beschikbaar zijn in `PATH`.

## Usage

```bash
Usage: nl-service-metadata-generator generate [OPTIONS] {csw|wms|wmts|wfs|wcs|
                                              sos|atom|tms|oaf|oat}
                                              {network|other|none}
                                              CONSTANTS_CONFIG_FILE
                                              SERVICE_CONFIG_FILE OUTPUT_FILE

  Generate service metadata record based on **Nederlands profiel op ISO 19119
  voor services versie 2.1.0**.

  CONSTANTS_CONFIG_FILE: JSON file that contains values for constant fields
  SERVICE_CONFIG_FILE: JSON file that contains values for fields that are
  unique for each service

  See `show-schema` command for help on config files.

Options:
  --csw-endpoint TEXT             References to dataset metadata records will
                                  use this CSW endpoint (default val: https://
                                  nationaalgeoregister.nl/geonetwork/srv/dut/c
                                  sw)
  --sds-type [invocable|interoperable]
                                  only applies when inspire-type='other'
  --help                          Show this message and exit.
```

Bijvoorbeeld (uitvoeren in root directory van dit repository):

```bash
nl-service-metadata-generator generate atom network example_json/constants.json example_json/inspire.json atom.xml
```

Merk op:
- `network` is voor INSPIRE WMS
- `other` is voor INSPIRE WFS en OGC API Feature
  - default = invocable
  - `--sds-type=INTEROPERABLE` 
- `none` is voor niet-INSPIRE services

Verschil van het generen van een service record voor inspire AS-IS of geharmoniseerde

- AS IS dataset voor INSPIRE voor de WFS en OGC API Feature een metadata inrichting krijgt met service type other en SDS invocable metadata
- geharmoniseerde dataset voor INSPIRE voor de WFS en OGC API Feature een metadata inrichting krijgt met service type other en SDS interoperable metadata

- Voor het genereren van een NGR record voor OGC API Features als other (as-is)
```bash
nl-service-metadata-generator generate OAF OTHER example_json/constants.json /data/oaf.json /data/oaf.xml
```

Voor het genereren van een NGR record voor OGC API Features als other (geharmoniseerde)
```bash
nl-service-metadata-generator generate OTHER --sds-type=INTEROPERABLE example_json/constants.json /data/oaf.json /data/oaf.xml
```


### HVD verordening
High Value Datasets (HVD) zijn datasets die door de Europese Unie zijn aangewezen als bijzonder waardevol voor sociaaleconomische doeleinden, 
met een verplichting tot kosteloze beschikbaarstelling voor hergebruik. 
Voor service metadata is het mogelijk middels het `hvdCategories` veld de HVD-categorieën te genereren en als keywords zoals omschreven in de [handrijking](https://docs.geostandaarden.nl/eu/handreiking-hvd/#409368F9) van Geonovum toe te voegen.

Zie [high-value-dataset-category.rdf](https://op.europa.eu/o/opportal-service/euvoc-download-handler?cellarURI=http%3A%2F%2Fpublications.europa.eu%2Fresource%2Fdistribution%2Fhigh-value-dataset-category%2F20241002-0%2Frdf%2Fskos_core%2Fhigh-value-dataset-category.rdf&fileName=high-value-dataset-category.rdf) voor een lijst van alle mogelijke HVD-categorieën.
De HVD is zo opgezet dat er een hiërarchie van 3 levels bestaat.
Wanneer een lagere categorie wordt gekozen worden automatisch de bovenliggende categorieën ook toegevoegd.
De RDF wordt automatisch gedownload en gecached voor 3 dagen.
Mocht je op zoek zijn naar een nieuwe recentelijke categorie verwijder dan `/src/nl_service_metadata_generator/data/xml/high-value-dataset-category_downloaded.rdf` zodat deze opnieuw wordt gedownload.
 
### Template variabelen

In de velden

- `service_title`
- `service_abstract`

Kunnen de volgende template variabelen worden opgenomen:

- `$SERVICE_TYPE_UPPER` - wordt vervangen door uppercase service type (korte variant)
- `$SERVICE_TYPE_LOWER` - wordt vervangen door lowercase service type (korte variant)
- `$OAF`                - wordt vervangen door OGC API Features

Bijvoorbeeld:

```json
{
  ...
  "serviceTitle": "Actueel Hoogtebestand Nederland $SERVICE_TYPE_UPPER"
  ...
}
```

## Development

Voor het formatteren van code installeer [`black`](https://pypi.org/project/black/) en draai vanuit de root van het repo:

```sh
black .
```

Verwijderen van ongebruikte imports met [`autoflake`](https://pypi.org/project/autoflake/):

```sh
autoflake --remove-all-unused-imports -i -r .
```

Organiseren en orderen imports met [`isort`](https://pypi.org/project/isort/):

```sh
isort  -m 3 .
```

## Docker

Container starten met: 

```sh
docker run --user root -v $(pwd)/example_json:/data pdok/nl-service-metadata-generator generate atom network /data/constants.json /data/inspire.json /data/atom.xml
```

> **n.b.** `-u root` argument, is nodig voor priviliges Docker container om bestanden weg te schrijven in folder mount. Voor productie doeleindes niet aan te raden om docker containers onder de root user te draaien. 

