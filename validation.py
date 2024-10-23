#Prérequis : Install

from lxml import etree
import sys

# Emplacement du fichier CSV et XML
xsdfile = "validation.xsd"
xmlfile = "file.xml"


def valider_xml(xml_path, xsd_path):
    try:
        # Charger le schéma XSD
        with open(xsd_path, 'rb') as schema_file:
            schema_root = etree.XML(schema_file.read())
        schema = etree.XMLSchema(schema_root)

        # Parser avec prise en compte des namespaces
        parser = etree.XMLParser(ns_clean=True)

        # Charger le fichier XML en mode binaire avec le parser
        with open(xml_path, 'rb') as xml_file:
            xml_doc = etree.parse(xml_file, parser)

        # Valider le fichier XML
        schema.assertValid(xml_doc)
        print("Le fichier XML est valide.")

    except etree.XMLSchemaError as e:
        print("Erreur de schéma XSD:", e)
    except etree.DocumentInvalid as e:
        print("Le fichier XML est invalide:", e)
    except Exception as e:
        print("Erreur lors de la validation du fichier XML:", e)

valider_xml(xmlfile, xsdfile)
