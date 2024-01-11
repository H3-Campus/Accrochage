import xml.etree.ElementTree as ET
import csv
import random
import logging
import datetime
import subprocess
import pytz
import os 

# Emplacement du fichier CSV et XML
csv_file = "Dico2.csv"
xml_file = "file.xml"
tz_paris = pytz.timezone('Europe/Paris')

#Efface la console
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')
clear_console()

# Configuration du logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def indent(elem, level=0):
    """ Ajoute des indentations aux éléments pour une meilleure lisibilité du fichier XML. """
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


# Fonction pour lire les données CSV et générer le fichier XML
def create_xml_from_csv(csv_filepath, xml_filepath):
    logging.info("Ouverture du CSV...")
    # Ouvrir le fichier CSV pour la lecture
    with open(csv_filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        Allrows = list(reader)
    
    # Vérification de la présence des données nécessaires
        if len(Allrows) < 5:
            logging.error("Les données CSV requises sont manquantes.")
            exit()
                        
        headers = Allrows[4][2:]  # Sauter les deux premiers en-têtes
        logging.info("Création de l'arborescence du fichier XML...")
    
        # Créer l'élément racine avec l'espace de noms 'cpf'
        root = ET.Element("cpf:flux")
        root.set("xmlns:cpf", "urn:cdc:cpf:pc5:schema:1.0.0")
        root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        
        #Reglage du fuseau horaire    
        now = datetime.datetime.now(tz_paris)
        value = now.strftime("%Y-%m-%dT%H:%M:%S+01:00")

        ET.SubElement(root, "cpf:idFlux").text = headers[0]
        #str(random.randint(1000000000, 99999999999))
        ET.SubElement(root, "cpf:horodatage").text = value
        
        # Création et ajout de l'élément emetteur
        emetteur = ET.SubElement(root, "cpf:emetteur")
        logging.info("Emmetteur du fchier ...")
        
        # Création de la structure des certificateurs       
        idClient = str(random.randint(10000000, 99999999)) if Allrows[5][2] == '' else Allrows[5][2]
        ET.SubElement(emetteur, "cpf:idClient").text = idClient
        certificateurs = ET.SubElement(emetteur, "cpf:certificateurs")   
        certificateur = ET.SubElement(certificateurs, "cpf:certificateur")
        logging.info(f"Certificateur {idClient}...")
        
        # Traitement pour NumClient pour le certificateur
        idClient2 = str(random.randint(10000000, 99999999)) if Allrows[5][3] == '' else Allrows[5][3]
        ET.SubElement(certificateur, "cpf:idClient").text = idClient2

        # Traitement pour NumContrat pour le certificateur
        idContrat = str(random.randint(10000000, 99999999)) if Allrows[5][4] == '' else Allrows[5][4]
        ET.SubElement(certificateur, "cpf:idContrat").text = idContrat
        
        # Création de la structure des certifications
        certifications = ET.SubElement(certificateur, "cpf:certifications")
        certification = ET.SubElement(certifications, "cpf:certification")
        
        ET.SubElement(certification, "cpf:type").text = headers[5]
        ET.SubElement(certification, "cpf:code").text = headers[6]
        
        # Ajout d'un seul passage de certification
        passage_certifications = ET.SubElement(certification, "cpf:passageCertifications")

        # Itérer sur chaque ligne du fichier CSV
        for row in Allrows[5:]: 
            # Sauter les lignes vides
            if not row[0].strip():
                continue

            #Ajout des certifications
            logging.info(f"Ajout des certifications : {row[7]}")
            passage_certification = ET.SubElement(passage_certifications, "cpf:passageCertification")
            ET.SubElement(passage_certification, "cpf:idTechnique").text = row[7]
            ET.SubElement(passage_certification, "cpf:obtentionCertification").text = row[8]
            ET.SubElement(passage_certification, "cpf:donneeCertifiee").text = row[9]
            ET.SubElement(passage_certification, "cpf:dateDebutValidite").text = row[10]
             # Vérification si la date de fin de validité est 'nil;'
            if row[11].strip().lower() == 'nil':
                ET.SubElement(passage_certification, "cpf:dateFinValidite", {"xsi:nil": "true"})
            else:
                ET.SubElement(passage_certification, "cpf:dateFinValidite").text = row[11]
            ET.SubElement(passage_certification, "cpf:presenceNiveauLangueEuro").text = row[12]
            ET.SubElement(passage_certification, "cpf:presenceNiveauNumeriqueEuro").text = row[13]
            if row[14].strip().lower() == 'nil':
                ET.SubElement(passage_certification, "cpf:scoring", {"xsi:nil": "true"})
            else:
                ET.SubElement(passage_certification, "cpf:scoring").text = row[14]
            if row[15].strip().lower() == 'nil':
                ET.SubElement(passage_certification, "cpf:mentionValidee", {"xsi:nil": "true"})
            else:
                ET.SubElement(passage_certification, "cpf:mentionValidee").text = row[15]
            
            # Modalite inscription
            modalites_inscription = ET.SubElement(passage_certification, "cpf:modalitesInscription")
            ET.SubElement(modalites_inscription, "cpf:modaliteAcces").text = row[16]
            
            #Identification Titulaire
            identification_titulaire = ET.SubElement(passage_certification, "cpf:identificationTitulaire")
            titulaire = ET.SubElement(identification_titulaire, "cpf:titulaire")
            
            logging.info(f"Titulaire : {row[18]} {row[19]}")
            ET.SubElement(titulaire, "cpf:nomNaissance").text = row[17]
            ET.SubElement(titulaire, "cpf:nomUsage").text = row[18]
            ET.SubElement(titulaire, "cpf:prenom1").text = row[19]
            ET.SubElement(titulaire, "cpf:anneeNaissance").text = row[20]
            ET.SubElement(titulaire, "cpf:moisNaissance").text = row[21]
            ET.SubElement(titulaire, "cpf:jourNaissance").text = row[22]
            ET.SubElement(titulaire, "cpf:sexe").text = row[23]
            code_commune_naissance = ET.SubElement(titulaire, "cpf:codeCommuneNaissance")
            code_postal_naissance = ET.SubElement(code_commune_naissance, "cpf:codePostalNaissance")
            ET.SubElement(code_postal_naissance, "cpf:codePostal").text = row[24]


        # Appliquer l'indentation
        indent(root)

        # Enregistrement du fichier XML
        logging.info(f"Ecriture du XML...")
        tree = ET.ElementTree(root)
        with open(xml_filepath, "wb") as file:
            tree.write(file, encoding="utf-8", xml_declaration=True)

# Appel de la fonction pour créer le fichier XML
create_xml_from_csv(csv_file, xml_file)
logging.info("Fichier XML créé avec succès.")

