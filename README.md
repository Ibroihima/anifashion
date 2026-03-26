# 🌸 Anifashion – Application Flask

Boutique en ligne de mode femme & fille avec système de comptes client et tableau de bord admin.

---

## 🚀 Installation rapide

### 1. Pré-requis
- Python 3.8+
- pip

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Lancer l'application

```bash
python app.py
```

L'application sera disponible sur **http://127.0.0.1:5000**

---

## 🔑 Comptes par défaut

| Rôle | Email | Mot de passe |
|------|-------|-------------|
| Admin | admin@anifashion.com | admin123 |

*Les comptes clients se créent via la page d'inscription.*

---

## 📁 Structure du projet

```
anifashion/
├── app.py                    # Application Flask principale
├── requirements.txt          # Dépendances Python
├── instance/
│   └── anifashion.db        # Base de données SQLite (auto-créée)
├── static/
│   ├── css/
│   │   ├── style.css        # Styles boutique
│   │   └── dashboard.css    # Styles dashboards
│   ├── js/
│   │   └── main.js          # JavaScript
│   └── uploads/             # Images des produits
└── templates/
    ├── base.html             # Template de base (boutique)
    ├── index.html            # Page d'accueil
    ├── produits.html         # Catalogue produits
    ├── auth/
    │   ├── login.html        # Connexion
    │   └── inscription.html  # Inscription
    ├── client/
    │   ├── base_client.html  # Layout dashboard client
    │   ├── dashboard.html    # Tableau de bord client
    │   ├── profil.html       # Profil client
    │   ├── commandes.html    # Liste commandes client
    │   └── commande_detail.html
    └── admin/
        ├── base_admin.html   # Layout dashboard admin
        ├── dashboard.html    # Tableau de bord admin
        ├── produits.html     # Gestion produits
        ├── produit_form.html # Formulaire ajout/modif produit
        ├── commandes.html    # Gestion commandes
        ├── commande_detail.html
        ├── clients.html      # Liste clients
        └── categories.html   # Gestion catégories
```

---

## ✨ Fonctionnalités

### 🛍️ Boutique
- Page d'accueil avec hero, produits, catégories
- Catalogue avec filtre par catégorie
- Design responsive

### 👤 Espace Client
- Inscription / Connexion sécurisée
- Tableau de bord avec résumé commandes
- Gestion du profil (infos, adresse, mot de passe)
- Suivi des commandes

### 🔧 Espace Admin
- Dashboard avec KPIs (CA, commandes, produits, clients)
- Gestion des produits (ajout, modification, désactivation)
- Upload d'images produits
- Gestion des commandes avec changement de statut
- Liste des clients
- Gestion des catégories

---

## 🛠️ Personnalisation

### Ajouter un admin
Dans `app.py`, après la création de la DB, vous pouvez créer un compte admin :
```python
from werkzeug.security import generate_password_hash
admin = User(nom='Votre', prenom='Nom', email='votre@email.com',
             password=generate_password_hash('motdepasse'), role='admin')
db.session.add(admin)
db.session.commit()
```

### Changer la clé secrète
Dans `app.py`, modifiez :
```python
app.config['SECRET_KEY'] = 'votre-cle-secrete-unique'
```
