# Accrochage
Accrochage à la caisse des dépôts. Ce script génére un fichier xml pour la caisse des dépôt à partir d'un fichier csv.

# Prérequis
* Les fichiers "Data.csv" doit être dans le meme dossier que "Accrochage.py"
* Environnement Python installé : sudo apt install python3
* Outil pip3 doit être installé : sudo apt install python3-pip python3-tk
* Le module pytz doit être installé : pip3 install pytz lxml 

### Cas de l'utilisation de Pycharm (Education) :

**Ouvrez les Paramètres de PyCharm.**
Allez dans Project: [nom_du_projet] > Python Interpreter.
Vérifiez que l'interpréteur Python sélectionné est celui où vous avez installé pytz (généralement /usr/bin/python3 si vous n'utilisez pas un environnement virtuel).

**Installer pytz directement via PyCharm :**
Dans PyCharm, allez dans File > Settings > Project: [nom_du_projet] > Python Interpreter.
Cliquez sur le bouton + (en haut à droite) pour ajouter un paquet.
Recherchez pytz et installez-le directement depuis PyCharm.


# Description 
Ce fichier doit contenir les certifications des étudiants aux format : 

## 5 Premières lignes du CSV :

BLOC 1,,BLOC 2,BLOC 3,,BLOC 4,,BLOC 5,,,,,,,,,BLOC 7,BLOC 8,,,,,,,

<cpf:flux>,,<cpf:emetteur>,<cpf:certificateur>,,<cpf:certification>,,<cpf:passageCertification>,,,,,,,,,<cpf:modalitesInscription>,<cpf:titulaire>,,,,,,,

1.1,1.2,2.1,3.1,3.2,4.1,4.2,5.1,5.4,5.5,5.10,5.11,5.12,5.14,5.15,5.16,7.1,8.1,8.2,8.3,8.6,8.7,8.8,8.9,8.11

Identifiant du flux,Horodatage,N° de la fiche client de l'emetteur,N° de la fiche client Certificateur,Numéro de contrat spécifique Certificateur,Type de certification,Code,ID Technique du passage de la certification,Obtention de la certification par admission ou scoring,Donnée certifiée,Date de début de validité et de délivrance de la certification,Date de fin de validité de la certification,Présence du niveau de langue européen,Présence du niveau numérique européen,Scoring ou base de notation,Mention(s) validée(s),Modalité d'accès à la certification,Nom de naissance du titulaire,Nom d'usage ou marital,Prénom 1,Année de naissance,Mois de naissance,Jour de naissance,Sexe,Code postal de la commune de naissance du titulaire

idFlux,horodatage,idClient,idClient,idContrat,type,code,idTechnique,obtentionCertification,donneeCertifiee,dateDebutValidite,dateFinValidite,presenceNiveauLangueEuro,presenceNiveauNumeriqueEuro,scoring,mentionValidee,modaliteAcces,nomNaissance,nomUsage,prenom1,anneeNaissance,moisNaissance,jourNaissance,sexe,codePostal

## A partir de la 6ème lignes :

* Les enregistrements des étudiants, avec les infos dans chaque colonne.

# Execution :
Lancement du script de converison en XML
`python3 Accrochage.py`

# Resultat :
Le script génére à partir du fichier "Data.csv" un fichier "file.xml" dans le dossier courant.
