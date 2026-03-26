# ============================================================
#  FICHIER WSGI – PythonAnywhere
#  Remplacez VOTRE_USERNAME par votre nom PythonAnywhere
# ============================================================
import sys
import os

USERNAME = 'VOTRE_USERNAME'   # <-- À CHANGER

project_home = f'/home/{USERNAME}/anifashion'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['SECRET_KEY'] = 'changez-cette-cle-secrete-unique-2025!'

from app import app, init_db
init_db()

application = app
