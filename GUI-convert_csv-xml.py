import csv
import os
import subprocess
import PySimpleGUI as sg

csv_file = 'Dico2.csv'

# Vérifiez le système d'exploitation pour déterminer la commande appropriée pour effacer l'écran
if os.name == 'posix':  # Linux ou macOS
    subprocess.run(['clear'], text=True, encoding='utf-8', check=False)
elif os.name == 'nt':   # Windows
    subprocess.run(['cls'], text=True, encoding='utf-8', check=False)

# Créez une liste vide pour stocker les lignes du CSV
csv_data = []

# Ouverture du fichier CSV en mode lecture
with open(csv_file, 'r', encoding='utf-8') as csvfile:
    # Créer un objet reader
    csvreader = csv.reader(csvfile)
    
    # Parcourir les lignes du fichier CSV et les ajouter à la liste csv_data
    for row in csvreader:
        csv_data.append(row)

# Créer une interface utilisateur simple pour afficher les données
layout = [
    [sg.Text('Balises :'), sg.Text('', size=(30, 1), key='balises')],
    [sg.Text('Nombre d\'éléments :'), sg.Text('', size=(30, 1), key='nb_elements')],
    [sg.Button('Afficher la deuxième ligne'), sg.Button('Afficher la cinquième ligne'), sg.Exit()]
]

window = sg.Window('Affichage de données CSV', layout)

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break
    elif event == 'Afficher la deuxième ligne':
        if len(csv_data) >= 2:
            window['balises'].update(', '.join(csv_data[1]))
            window['nb_elements'].update(len(csv_data[1]))
        else:
            sg.popup_error("Le fichier CSV ne contient pas assez de lignes pour accéder à l'indice 1.")
    elif event == 'Afficher la cinquième ligne':
        if len(csv_data) >= 5:
            window['balises'].update(', '.join(csv_data[4]))
            window['nb_elements'].update(len(csv_data[4]))
        else:
            sg.popup_error("Le fichier CSV ne contient pas assez de lignes pour accéder à l'indice 4.")

window.close()
