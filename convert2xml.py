"""
Générateur XML pour certifications CPF - Version Optimisée
Génère un fichier XML conforme au schéma urn:cdc:cpf:pc5:schema:1.0.0
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import csv
import logging
import datetime
import pytz
import os
from pathlib import Path
from typing import Optional, List, Dict
import sys

# Configuration
CSV_FILE = "Data.csv"
XML_FILE = "file.xml"
XSD_FILE = "validation.xsd"
TZ_PARIS = pytz.timezone('Europe/Paris')

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('xml_generation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class XMLValidator:
    """Classe pour valider le XML généré contre le XSD"""
    
    @staticmethod
    def validate_xml(xml_file: str, xsd_file: str) -> bool:
        """Valide un fichier XML contre un schéma XSD"""
        try:
            from lxml import etree
            
            # Charger le schéma XSD
            with open(xsd_file, 'rb') as f:
                schema_root = etree.XML(f.read())
            schema = etree.XMLSchema(schema_root)
            
            # Charger le fichier XML
            with open(xml_file, 'rb') as f:
                xml_doc = etree.parse(f)
            
            # Valider
            is_valid = schema.validate(xml_doc)
            
            if not is_valid:
                logger.error("Erreurs de validation XSD:")
                for error in schema.error_log:
                    logger.error(f"  Ligne {error.line}: {error.message}")
                return False
            
            logger.info("✓ Le fichier XML est valide selon le schéma XSD")
            return True
            
        except ImportError:
            logger.warning("Module lxml non disponible. Installation recommandée: pip install lxml")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la validation: {e}")
            return False


class CPFXMLGenerator:
    """Générateur de fichiers XML pour les certifications CPF"""
    
    def __init__(self, csv_filepath: str, xml_filepath: str):
        self.csv_filepath = Path(csv_filepath)
        self.xml_filepath = Path(xml_filepath)
        self.namespace = "urn:cdc:cpf:pc5:schema:1.0.0"
        self.xsi_namespace = "http://www.w3.org/2001/XMLSchema-instance"
        
    def validate_csv_structure(self, rows: List[List[str]]) -> bool:
        """Valide la structure du fichier CSV"""
        if len(rows) < 6:
            logger.error("Le fichier CSV doit contenir au moins 6 lignes")
            return False
        
        # Vérifier que la ligne d'en-tête existe
        if not rows[5] or len(rows[5]) < 25:
            logger.error("La ligne d'en-tête (ligne 6) est incomplète")
            return False
        
        return True
    
    def clean_string(self, value: str, max_length: Optional[int] = None) -> str:
        """Nettoie et tronque une chaîne si nécessaire"""
        cleaned = value.strip()
        if max_length and len(cleaned) > max_length:
            logger.warning(f"Valeur tronquée: '{cleaned}' -> '{cleaned[:max_length]}'")
            cleaned = cleaned[:max_length]
        return cleaned
    
    def format_date(self, date_str: str) -> str:
        """
        Convertit une date du format DD/MM/YYYY vers YYYY-MM-DD
        Gère aussi les dates déjà au bon format
        """
        date_str = date_str.strip()
        
        # Si déjà au format ISO (YYYY-MM-DD)
        if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
            return date_str
        
        # Format DD/MM/YYYY
        if '/' in date_str:
            parts = date_str.split('/')
            if len(parts) == 3 and len(parts[2]) == 4:
                return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
        
        logger.warning(f"Format de date non reconnu: {date_str}")
        return date_str
    
    def get_current_timestamp(self) -> str:
        """Génère un horodatage au format requis par le XSD"""
        now = datetime.datetime.now(TZ_PARIS)
        return now.strftime("%Y-%m-%dT%H:%M:%S+01:00")
    
    def create_element(self, parent: ET.Element, tag: str, text: Optional[str] = None, 
                      attrib: Optional[Dict] = None) -> ET.Element:
        """Crée un élément XML avec le namespace cpf"""
        full_tag = f"{{{self.namespace}}}{tag}"
        elem = ET.SubElement(parent, full_tag, attrib or {})
        if text is not None:
            elem.text = str(text)
        return elem
    
    def add_titulaire(self, parent: ET.Element, row: List[str]) -> None:
        """Ajoute les informations du titulaire"""
        titulaire = self.create_element(parent, "titulaire")
        
        # Données obligatoires
        self.create_element(titulaire, "nomNaissance", self.clean_string(row[17], 60))
        
        # nomUsage (nillable)
        if row[18].strip() and row[18].strip().lower() != 'nil':
            self.create_element(titulaire, "nomUsage", self.clean_string(row[18], 60))
        else:
            self.create_element(titulaire, "nomUsage", attrib={f"{{{self.xsi_namespace}}}nil": "true"})
        
        self.create_element(titulaire, "prenom1", self.clean_string(row[19], 60))
        self.create_element(titulaire, "anneeNaissance", self.clean_string(row[20]))
        
        # moisNaissance (nillable)
        if row[21].strip() and row[21].strip().lower() != 'nil':
            self.create_element(titulaire, "moisNaissance", self.clean_string(row[21]))
        else:
            self.create_element(titulaire, "moisNaissance", attrib={f"{{{self.xsi_namespace}}}nil": "true"})
        
        # jourNaissance (nillable)
        if row[22].strip() and row[22].strip().lower() != 'nil':
            self.create_element(titulaire, "jourNaissance", self.clean_string(row[22]))
        else:
            self.create_element(titulaire, "jourNaissance", attrib={f"{{{self.xsi_namespace}}}nil": "true"})
        
        self.create_element(titulaire, "sexe", self.clean_string(row[23]))
        
        # Code commune naissance
        code_commune = self.create_element(titulaire, "codeCommuneNaissance")
        code_postal_elem = self.create_element(code_commune, "codePostalNaissance")
        
        if row[24].strip() and row[24].strip().lower() != 'nil':
            self.create_element(code_postal_elem, "codePostal", self.clean_string(row[24], 9))
        else:
            self.create_element(code_postal_elem, "codePostal", attrib={f"{{{self.xsi_namespace}}}nil": "true"})
    
    def add_passage_certification(self, parent: ET.Element, row: List[str]) -> None:
        """Ajoute un passage de certification"""
        passage = self.create_element(parent, "passageCertification")
        
        # Données obligatoires
        self.create_element(passage, "idTechnique", self.clean_string(row[7], 255))
        self.create_element(passage, "obtentionCertification", row[8].upper())
        self.create_element(passage, "donneeCertifiee", row[9].lower())
        
        # Dates
        self.create_element(passage, "dateDebutValidite", self.format_date(row[10]))
        
        # dateFinValidite (nillable)
        if row[11].strip().lower() == 'nil':
            self.create_element(passage, "dateFinValidite", attrib={f"{{{self.xsi_namespace}}}nil": "true"})
        else:
            self.create_element(passage, "dateFinValidite", self.format_date(row[11]))
        
        # Niveaux européens
        self.create_element(passage, "presenceNiveauLangueEuro", row[12].lower())
        self.create_element(passage, "presenceNiveauNumeriqueEuro", row[13].lower())
        
        # Scoring (nillable)
        if row[14].strip().lower() == 'nil':
            self.create_element(passage, "scoring", attrib={f"{{{self.xsi_namespace}}}nil": "true"})
        else:
            self.create_element(passage, "scoring", self.clean_string(row[14], 255))
        
        # Mention validée (nillable)
        if row[15].strip().lower() == 'nil':
            self.create_element(passage, "mentionValidee", attrib={f"{{{self.xsi_namespace}}}nil": "true"})
        else:
            self.create_element(passage, "mentionValidee", row[15].upper())
        
        # Modalités inscription
        modalites = self.create_element(passage, "modalitesInscription")
        self.create_element(modalites, "modaliteAcces", row[16].upper())
        
        # Identification titulaire
        identification = self.create_element(passage, "identificationTitulaire")
        self.add_titulaire(identification, row)
    
    def generate_xml(self) -> bool:
        """Génère le fichier XML à partir du CSV"""
        try:
            logger.info(f"Lecture du fichier CSV: {self.csv_filepath}")
            
            # Vérifier l'existence du fichier
            if not self.csv_filepath.exists():
                logger.error(f"Fichier CSV introuvable: {self.csv_filepath}")
                return False
            
            # Lire le CSV
            with open(self.csv_filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            # Valider la structure
            if not self.validate_csv_structure(rows):
                return False
            
            logger.info("Création de la structure XML...")
            
            # Créer l'élément racine
            ET.register_namespace('cpf', self.namespace)
            ET.register_namespace('xsi', self.xsi_namespace)
            
            root = ET.Element(
                f"{{{self.namespace}}}flux",
                attrib={
                    f"{{{self.xsi_namespace}}}schemaLocation": 
                        f"{self.namespace} validation.xsd"
                }
            )
            
            # En-tête
            headers = rows[5]
            self.create_element(root, "idFlux", self.clean_string(headers[2], 50))
            self.create_element(root, "horodatage", self.get_current_timestamp())
            
            # Émetteur
            emetteur = self.create_element(root, "emetteur")
            self.create_element(emetteur, "idClient", self.clean_string(headers[3], 8))
            
            # Certificateurs
            certificateurs = self.create_element(emetteur, "certificateurs")
            certificateur = self.create_element(certificateurs, "certificateur")
            
            self.create_element(certificateur, "idClient", self.clean_string(headers[4], 8))
            self.create_element(certificateur, "idContrat", self.clean_string(headers[5], 20))
            
            # Certifications
            certifications = self.create_element(certificateur, "certifications")
            certification = self.create_element(certifications, "certification")
            
            self.create_element(certification, "type", self.clean_string(headers[6], 255))
            self.create_element(certification, "code", self.clean_string(headers[7], 100))
            
            # Passages de certification
            passages = self.create_element(certification, "passageCertifications")
            
            # Traiter chaque ligne de données
            data_rows = [row for row in rows[6:] if row and row[0].strip()]
            logger.info(f"Traitement de {len(data_rows)} certifications...")
            
            for idx, row in enumerate(data_rows, start=1):
                try:
                    logger.info(f"  [{idx}/{len(data_rows)}] Ajout: {row[19]} {row[17]}")
                    self.add_passage_certification(passages, row)
                except Exception as e:
                    logger.error(f"Erreur ligne {idx + 6}: {e}")
                    continue
            
            # Formater et sauvegarder
            logger.info(f"Écriture du fichier XML: {self.xml_filepath}")
            xml_str = ET.tostring(root, encoding='utf-8')
            
            # Indentation avec minidom
            dom = minidom.parseString(xml_str)
            pretty_xml = dom.toprettyxml(indent="  ", encoding='utf-8')
            
            # Supprimer les lignes vides
            lines = [line for line in pretty_xml.decode('utf-8').split('\n') if line.strip()]
            
            with open(self.xml_filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            logger.info("✓ Fichier XML créé avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération XML: {e}", exc_info=True)
            return False


def main():
    """Fonction principale"""
    # Effacer la console
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("=" * 70)
    print("GÉNÉRATEUR XML CPF - Version Professionnelle")
    print("=" * 70)
    print()
    
    # Générer le XML
    generator = CPFXMLGenerator(CSV_FILE, XML_FILE)
    
    if not generator.generate_xml():
        logger.error("❌ Échec de la génération du fichier XML")
        sys.exit(1)
    
    print()
    print("-" * 70)
    print("VALIDATION DU FICHIER XML")
    print("-" * 70)
    
    # Valider le XML
    validator = XMLValidator()
    
    if Path(XSD_FILE).exists():
        validation_result = validator.validate_xml(XML_FILE, XSD_FILE)
        
        if validation_result is True:
            print()
            print("✓" * 35)
            print("SUCCESS: Le fichier XML est conforme au schéma XSD")
            print("✓" * 35)
        elif validation_result is False:
            print()
            print("⚠" * 35)
            print("ATTENTION: Le fichier XML contient des erreurs de validation")
            print("Consultez les logs ci-dessus pour plus de détails")
            print("⚠" * 35)
        else:
            print()
            print("ℹ" * 35)
            print("INFO: Validation XSD non effectuée (module lxml non installé)")
            print("Installez lxml pour activer la validation: pip install lxml")
            print("ℹ" * 35)
    else:
        logger.warning(f"Fichier XSD non trouvé: {XSD_FILE}")
        print()
        print("⚠" * 35)
        print("ATTENTION: Fichier XSD non trouvé - validation impossible")
        print("⚠" * 35)
    
    print()
    print(f"Fichier généré: {XML_FILE}")
    print(f"Logs disponibles: xml_generation.log")


if __name__ == "__main__":
    main()
