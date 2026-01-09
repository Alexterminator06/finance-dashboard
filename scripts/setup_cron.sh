#!/bin/bash

# 1. Définir le dossier où se trouve votre projet sur la VM Linux
# Exemple : /home/etudiant/finance-dashboard
PROJECT_DIR="/home/votre_nom_utilisateur/finance-dashboard"

# 2. Se déplacer dans ce dossier
cd "$PROJECT_DIR" || exit

# 3. Activer l'environnement virtuel (Indispensable pour avoir pandas, yfinance, etc.)
# Assurez-vous que votre dossier venv s'appelle bien "venv"
source venv/bin/activate

# 4. Lancer le script Python
# On ajoute une date dans les logs pour savoir quand ça a tourné
echo "--- Début du rapport : $(date) ---" >> logs/cron_log.txt

# On lance le script et on redirige les erreurs (2>&1) vers le fichier de log
python3 app/daily_report.py >> logs/cron_log.txt 2>&1

# 5. Désactiver l'environnement (optionnel mais propre)
deactivate