import PySimpleGUI as sg
import subprocess

def run_script(script_path):
    try:
        result = subprocess.run(['python3', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode('utf-8'), result.stderr.decode('utf-8')
    except Exception as e:
        return '', str(e)

# Définir le layout de la fenêtre
layout = [
    [sg.Text("Conversion du XML", size=(30, 1), justification="center", font=("Arial", 16, "bold"))],
    [sg.Text("Préparation du XML :")],
    [sg.Button("Executer la conversion"), sg.Button("Validation"), sg.Button("Fermer")],
    [sg.Output(size=(50, 20))],
    [sg.Text("", size=(50, 1), key="-VALIDATION-RESULT-", text_color="black")]  # Ajout d'un élément Text pour les résultats de validation
]

# Créer la fenêtre
window = sg.Window("Accrochage caisse des dépots", layout)

# Boucle d'événements pour traiter les events et obtenir les values
while True:
    event, values = window.read()
    
    if event == "Executer la conversion":
        stdout, stderr = run_script('Accrochage.py')
        print(stdout)
        if stderr:
            print("Erreur:", stderr)
    elif event == "Validation":
        stdout, stderr = run_script('validation.py')
        if not stderr:
            window["-VALIDATION-RESULT-"].update("Fichier valide", text_color="lime")
        else:
            window["-VALIDATION-RESULT-"].update("Erreur de validation,consulter le l'affichage...", text_color="red")
        print(stdout if stdout else stderr)
    elif event == sg.WIN_CLOSED or event == "Fermer":
        break

window.close()
