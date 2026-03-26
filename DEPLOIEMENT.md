# 🚀 Déploiement Anifashion sur PythonAnywhere

## Étape 1 — Créer un compte
→ https://www.pythonanywhere.com (compte gratuit suffisant)
→ Notez votre **nom d'utilisateur** (ex: `monsite`)

---

## Étape 2 — Uploader les fichiers

1. Onglet **Files** → créez le dossier `anifashion`
2. Uploadez `anifashion.zip` dans `/home/VOTRE_USERNAME/`
3. Ouvrez une **Bash console** et tapez :
```bash
cd ~
unzip anifashion.zip
```

---

## Étape 3 — Installer les dépendances

Dans la **Bash console** :
```bash
cd ~/anifashion
pip3.10 install -r requirements.txt --user
```

---

## Étape 4 — Modifier wsgi.py

Ouvrez le fichier `wsgi.py` et remplacez :
```python
USERNAME = 'VOTRE_USERNAME'
```
par votre vrai nom d'utilisateur, puis changez la clé secrète.

---

## Étape 5 — Créer l'application Web

1. Onglet **Web** → **Add a new web app**
2. Choisissez **Manual configuration** → **Python 3.10**
3. Dans **Code** :
   - Source code : `/home/VOTRE_USERNAME/anifashion`
   - Working directory : `/home/VOTRE_USERNAME/anifashion`
4. Cliquez sur le lien **WSGI configuration file**
   → Supprimez tout, collez le contenu de `wsgi.py`, sauvegardez

---

## Étape 6 — Fichiers statiques

Onglet **Web** → section **Static files** → ajoutez :

| URL       | Directory                                        |
|-----------|--------------------------------------------------|
| /static/  | /home/VOTRE_USERNAME/anifashion/static/          |

---

## Étape 7 — Lancer !

Onglet **Web** → bouton vert **Reload**
Votre site est sur : `https://VOTRE_USERNAME.pythonanywhere.com`

Admin : `admin@anifashion.com` / `admin123`

---

## ❗ Erreurs fréquentes

| Problème | Solution |
|----------|----------|
| Erreur 500 | Vérifiez **Error log** dans l'onglet Web |
| Images manquantes | Vérifiez la config Static files |
| Module not found | `pip3.10 install flask flask-sqlalchemy --user` |
| DB vide | Dans Bash : `python3.10 -c "from app import init_db; init_db()"` |
