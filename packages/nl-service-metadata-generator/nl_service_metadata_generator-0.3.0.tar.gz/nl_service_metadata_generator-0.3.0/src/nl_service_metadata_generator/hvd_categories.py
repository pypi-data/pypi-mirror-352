import os
import urllib

from datetime import datetime, timedelta
from lxml import etree

from nl_service_metadata_generator.constants import HVD_CATEGORIES_XML_LOCAL, HVD_CATEGORIES_XML_REMOTE
from nl_service_metadata_generator.util import resolve_resource_path


def get_full_nsmap(root):
    nsmap = root.nsmap.copy()
    required_namespaces = {
        "gmd": "http://www.isotc211.org/2005/gmd",
        "gco": "http://www.isotc211.org/2005/gco",
        "gmx": "http://www.isotc211.org/2005/gmx",
        "xlink": "http://www.w3.org/1999/xlink",
        "skos": "http://www.w3.org/2004/02/skos/core#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "euvoc": "http://publications.europa.eu/ontology/euvoc#",
        "dcmi": "http://purl.org/dc/elements/1.1/",
    }
    nsmap.update({prefix: uri for prefix, uri in required_namespaces.items() if prefix not in nsmap})
    return nsmap

hvd_rdf_path = resolve_resource_path(HVD_CATEGORIES_XML_LOCAL)
hvd_downloaded_path = os.path.join(os.path.dirname(hvd_rdf_path), os.path.basename(hvd_rdf_path).split('.')[0] + "_downloaded.rdf")

def download_rdf():

    with urllib.request.urlopen(HVD_CATEGORIES_XML_REMOTE) as response:
        xml_content = response.read().decode('utf-8')

    with open(hvd_downloaded_path, "w", encoding="utf-8") as file:
        file.write(xml_content)

    return etree.XML(xml_content.encode("utf-8"))

def open_rdf(rdf_path):
    with open(rdf_path, "r", encoding="utf-8") as file:
        return etree.XML(file.read().encode("utf-8"))

def get_rdf():
    if os.path.exists(hvd_downloaded_path):
        file_time = datetime.fromtimestamp(os.path.getmtime(hvd_downloaded_path))
        if datetime.now() - file_time < timedelta(days=3):
            print("Use cached version of high-value-dataset-category.rdf")
            return open_rdf(hvd_downloaded_path)

    print("Try downloading high-value-dataset-category.rdf")
    try:
        return download_rdf()
    except urllib.error.URLError:
        print("Failed to download RDF from: "+HVD_CATEGORIES_XML_REMOTE)

    print("Revert to local copy!")
    return open_rdf(hvd_rdf_path)

def init_hvd_category_list():

    root = get_rdf()
    nsmap = get_full_nsmap(root)
    categories = [
        {
            "uri": description.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"),
            "label": pref_label.text.strip(),
            "lang": pref_label.attrib.get("{http://www.w3.org/XML/1998/namespace}lang", "").lower(),
            "order": description.find("euvoc:order", namespaces=nsmap).text,
            "id": description.find("dcmi:identifier", namespaces=nsmap).text
        }
        for description in root.findall(".//rdf:Description", namespaces=nsmap)
        for pref_label in description.findall(".//skos:prefLabel", namespaces=nsmap)
        if pref_label.text and pref_label.attrib.get("{http://www.w3.org/XML/1998/namespace}lang", "").lower() == "nl"
    ]
    return categories


class HVDCategory:

    def __init__(self):
        self.categories = init_hvd_category_list()
        self.categories.sort(key=lambda x: x['order'])

    def get_hvd_category_by_id(self, hvd_id: str):
        for category in self.categories:
            if category["id"] == hvd_id:
                return category
        return None

    def get_hvd_category_by_order(self, order: str):
        for category in self.categories:
            if category["order"] == order:
                return category
        return None

    def get_hvd_category_by_id_list(self, hvd_ids: [str]):
        hvd_categories = []
        seen_ids = set()

        for hvd_id in hvd_ids:
            for category in self.get_hvd_with_parents(hvd_id):
                if category['id'] not in seen_ids:
                    hvd_categories.append(category)
                    seen_ids.add(category['id'])
        hvd_categories.sort(key=lambda x: x['order'])

        return hvd_categories

    def get_hvd_with_parents(self, hvd_id):
        """
        Recursively fetch an HVD category and its parents up to three levels.

        :param hvd_id: The ID of the HVD category to start from.
        :return: List of dictionaries representing the HVD category and its parents.
        """

        def get_parents(order):
            if len(order) == 2:  # Top level, no parent
                return []
            parent_order = order[:-2]
            parent_category = self.get_hvd_category_by_order(parent_order)
            if parent_category:
                return [parent_category] + get_parents(parent_order)
            return []

        target_category = self.get_hvd_category_by_id(hvd_id)
        if target_category:
            parents = get_parents(target_category['order'])
            # Return the list with the target category at the end to maintain hierarchy
            return parents + [target_category]
        else:
            return []
