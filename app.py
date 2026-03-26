from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime
import os

app = Flask(__name__)

# ── CONFIGURATION ──
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'anifashion-secret-2025-changeme')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'anifashion.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'instance'), exist_ok=True)

db = SQLAlchemy(app)

# ─────────────────────────────────────────
# MODÈLES
# ─────────────────────────────────────────

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='client')  # 'client' ou 'admin'
    telephone = db.Column(db.String(20))
    adresse = db.Column(db.String(255))
    ville = db.Column(db.String(100))
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    commandes = db.relationship('Commande', backref='client', lazy=True)

class Categorie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    emoji = db.Column(db.String(10), default='👗')
    produits = db.relationship('Produit', backref='categorie', lazy=True)

class Produit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    prix = db.Column(db.Float, nullable=False)
    prix_ancien = db.Column(db.Float)
    stock = db.Column(db.Integer, default=0)
    image = db.Column(db.String(255), default='default.jpg')
    categorie_id = db.Column(db.Integer, db.ForeignKey('categorie.id'))
    badge = db.Column(db.String(50))  # 'Nouveau', 'Solde', etc.
    actif = db.Column(db.Boolean, default=True)
    date_ajout = db.Column(db.DateTime, default=datetime.utcnow)
    lignes_commande = db.relationship('LigneCommande', backref='produit', lazy=True)

class Commande(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_commande = db.Column(db.DateTime, default=datetime.utcnow)
    statut = db.Column(db.String(50), default='En attente')  # En attente, Confirmée, Expédiée, Livrée, Annulée
    total = db.Column(db.Float, default=0.0)
    adresse_livraison = db.Column(db.String(255))
    ville_livraison = db.Column(db.String(100))
    lignes = db.relationship('LigneCommande', backref='commande', lazy=True)

class LigneCommande(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commande_id = db.Column(db.Integer, db.ForeignKey('commande.id'), nullable=False)
    produit_id = db.Column(db.Integer, db.ForeignKey('produit.id'), nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    prix_unitaire = db.Column(db.Float, nullable=False)

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Veuillez vous connecter.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Accès réservé aux administrateurs.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ─────────────────────────────────────────
# ROUTES PUBLIQUES
# ─────────────────────────────────────────

@app.route('/')
def index():
    produits = Produit.query.filter_by(actif=True).order_by(Produit.date_ajout.desc()).limit(8).all()
    categories = Categorie.query.all()
    return render_template('index.html', produits=produits, categories=categories)

@app.route('/produits')
def produits():
    cat_id = request.args.get('categorie')
    if cat_id:
        produits = Produit.query.filter_by(actif=True, categorie_id=cat_id).all()
    else:
        produits = Produit.query.filter_by(actif=True).all()
    categories = Categorie.query.all()
    return render_template('produits.html', produits=produits, categories=categories, cat_id=cat_id)

# ─────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────

@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']
        if password != confirm:
            flash('Les mots de passe ne correspondent pas.', 'danger')
            return redirect(url_for('inscription'))
        if User.query.filter_by(email=email).first():
            flash('Cet email est déjà utilisé.', 'danger')
            return redirect(url_for('inscription'))
        user = User(
            nom=nom, prenom=prenom, email=email,
            password=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        flash('Compte créé avec succès ! Connectez-vous.', 'success')
        return redirect(url_for('login'))
    return render_template('auth/inscription.html')

@app.route('/connexion', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_nom'] = user.prenom
            session['role'] = user.role
            flash(f'Bienvenue, {user.prenom} !', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('client_dashboard'))
        flash('Email ou mot de passe incorrect.', 'danger')
    return render_template('auth/login.html')

@app.route('/deconnexion')
def logout():
    session.clear()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('index'))

# ─────────────────────────────────────────
# DASHBOARD CLIENT
# ─────────────────────────────────────────

@app.route('/mon-compte')
@login_required
def client_dashboard():
    user = User.query.get(session['user_id'])
    commandes = Commande.query.filter_by(user_id=user.id).order_by(Commande.date_commande.desc()).all()
    return render_template('client/dashboard.html', user=user, commandes=commandes)

@app.route('/mon-compte/profil', methods=['GET', 'POST'])
@login_required
def client_profil():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.nom = request.form['nom']
        user.prenom = request.form['prenom']
        user.telephone = request.form['telephone']
        user.adresse = request.form['adresse']
        user.ville = request.form['ville']
        if request.form['nouveau_mdp']:
            if check_password_hash(user.password, request.form['ancien_mdp']):
                user.password = generate_password_hash(request.form['nouveau_mdp'])
            else:
                flash('Ancien mot de passe incorrect.', 'danger')
                return redirect(url_for('client_profil'))
        db.session.commit()
        flash('Profil mis à jour.', 'success')
    return render_template('client/profil.html', user=user)

@app.route('/mon-compte/commandes')
@login_required
def client_commandes():
    user = User.query.get(session['user_id'])
    commandes = Commande.query.filter_by(user_id=user.id).order_by(Commande.date_commande.desc()).all()
    return render_template('client/commandes.html', user=user, commandes=commandes)

@app.route('/mon-compte/commande/<int:id>')
@login_required
def client_commande_detail(id):
    commande = Commande.query.get_or_404(id)
    if commande.user_id != session['user_id']:
        flash('Accès refusé.', 'danger')
        return redirect(url_for('client_dashboard'))
    user = User.query.get(session['user_id'])
    return render_template('client/commande_detail.html', commande=commande, user=user)

# ─────────────────────────────────────────
# DASHBOARD ADMIN
# ─────────────────────────────────────────

@app.route('/admin')
@admin_required
def admin_dashboard():
    total_users = User.query.filter_by(role='client').count()
    total_commandes = Commande.query.count()
    total_produits = Produit.query.filter_by(actif=True).count()
    chiffre_affaires = db.session.query(db.func.sum(Commande.total)).scalar() or 0
    commandes_recentes = Commande.query.order_by(Commande.date_commande.desc()).limit(5).all()
    # Stats par statut
    stats_statuts = db.session.query(Commande.statut, db.func.count(Commande.id)).group_by(Commande.statut).all()
    return render_template('admin/dashboard.html',
        total_users=total_users,
        total_commandes=total_commandes,
        total_produits=total_produits,
        chiffre_affaires=chiffre_affaires,
        commandes_recentes=commandes_recentes,
        stats_statuts=stats_statuts
    )

# Admin – Produits
@app.route('/admin/produits')
@admin_required
def admin_produits():
    produits = Produit.query.order_by(Produit.date_ajout.desc()).all()
    return render_template('admin/produits.html', produits=produits)

@app.route('/admin/produits/ajouter', methods=['GET', 'POST'])
@admin_required
def admin_produit_ajouter():
    categories = Categorie.query.all()
    if request.method == 'POST':
        image_filename = 'default.jpg'
        if 'image' in request.files:
            f = request.files['image']
            if f and allowed_file(f.filename):
                filename = secure_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
        produit = Produit(
            nom=request.form['nom'],
            description=request.form['description'],
            prix=float(request.form['prix']),
            prix_ancien=float(request.form['prix_ancien']) if request.form['prix_ancien'] else None,
            stock=int(request.form['stock']),
            categorie_id=int(request.form['categorie_id']),
            badge=request.form['badge'],
            image=image_filename
        )
        db.session.add(produit)
        db.session.commit()
        flash('Produit ajouté avec succès.', 'success')
        return redirect(url_for('admin_produits'))
    return render_template('admin/produit_form.html', categories=categories, produit=None)

@app.route('/admin/produits/modifier/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_produit_modifier(id):
    produit = Produit.query.get_or_404(id)
    categories = Categorie.query.all()
    if request.method == 'POST':
        produit.nom = request.form['nom']
        produit.description = request.form['description']
        produit.prix = float(request.form['prix'])
        produit.prix_ancien = float(request.form['prix_ancien']) if request.form['prix_ancien'] else None
        produit.stock = int(request.form['stock'])
        produit.categorie_id = int(request.form['categorie_id'])
        produit.badge = request.form['badge']
        produit.actif = 'actif' in request.form
        if 'image' in request.files:
            f = request.files['image']
            if f and allowed_file(f.filename):
                filename = secure_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                produit.image = filename
        db.session.commit()
        flash('Produit mis à jour.', 'success')
        return redirect(url_for('admin_produits'))
    return render_template('admin/produit_form.html', categories=categories, produit=produit)

@app.route('/admin/produits/supprimer/<int:id>')
@admin_required
def admin_produit_supprimer(id):
    produit = Produit.query.get_or_404(id)
    produit.actif = False
    db.session.commit()
    flash('Produit désactivé.', 'info')
    return redirect(url_for('admin_produits'))

# Admin – Commandes
@app.route('/admin/commandes')
@admin_required
def admin_commandes():
    commandes = Commande.query.order_by(Commande.date_commande.desc()).all()
    return render_template('admin/commandes.html', commandes=commandes)

@app.route('/admin/commandes/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_commande_detail(id):
    commande = Commande.query.get_or_404(id)
    if request.method == 'POST':
        commande.statut = request.form['statut']
        db.session.commit()
        flash('Statut mis à jour.', 'success')
    return render_template('admin/commande_detail.html', commande=commande)

# Admin – Clients
@app.route('/admin/clients')
@admin_required
def admin_clients():
    clients = User.query.filter_by(role='client').order_by(User.date_inscription.desc()).all()
    return render_template('admin/clients.html', clients=clients)

# Admin – Catégories
@app.route('/admin/categories', methods=['GET', 'POST'])
@admin_required
def admin_categories():
    if request.method == 'POST':
        cat = Categorie(nom=request.form['nom'], emoji=request.form['emoji'])
        db.session.add(cat)
        db.session.commit()
        flash('Catégorie ajoutée.', 'success')
    categories = Categorie.query.all()
    return render_template('admin/categories.html', categories=categories)

# ─────────────────────────────────────────
# PANIER (stocké en session)
# ─────────────────────────────────────────

def get_panier():
    """Retourne le panier depuis la session sous forme de dict {produit_id: quantite}"""
    return session.get('panier', {})

def save_panier(panier):
    session['panier'] = panier
    session.modified = True

def panier_count():
    return sum(get_panier().values())

def panier_total():
    panier = get_panier()
    total = 0
    for pid, qty in panier.items():
        p = Produit.query.get(int(pid))
        if p:
            total += p.prix * qty
    return round(total, 2)

# Injecter le nombre d'articles dans tous les templates
@app.context_processor
def inject_panier():
    return dict(panier_count=panier_count(), panier_total=panier_total())

@app.route('/panier/ajouter/<int:produit_id>', methods=['POST'])
def ajouter_panier(produit_id):
    produit = Produit.query.get_or_404(produit_id)
    quantite = int(request.form.get('quantite', 1))
    panier = get_panier()
    key = str(produit_id)
    panier[key] = panier.get(key, 0) + quantite
    # Vérifier stock
    if panier[key] > produit.stock:
        panier[key] = produit.stock
    save_panier(panier)
    flash(f'"{produit.nom}" ajouté au panier ! 🛍️', 'success')
    # Retour à la page précédente
    return redirect(request.referrer or url_for('produits'))

@app.route('/panier/supprimer/<int:produit_id>')
def supprimer_panier(produit_id):
    panier = get_panier()
    key = str(produit_id)
    if key in panier:
        del panier[key]
        save_panier(panier)
    return redirect(url_for('voir_panier'))

@app.route('/panier/modifier/<int:produit_id>', methods=['POST'])
def modifier_panier(produit_id):
    panier = get_panier()
    key = str(produit_id)
    quantite = int(request.form.get('quantite', 1))
    if quantite <= 0:
        if key in panier:
            del panier[key]
    else:
        produit = Produit.query.get_or_404(produit_id)
        panier[key] = min(quantite, produit.stock)
    save_panier(panier)
    return redirect(url_for('voir_panier'))

@app.route('/panier')
def voir_panier():
    panier = get_panier()
    items = []
    total = 0
    for pid, qty in panier.items():
        p = Produit.query.get(int(pid))
        if p:
            sous_total = p.prix * qty
            total += sous_total
            items.append({'produit': p, 'quantite': qty, 'sous_total': round(sous_total, 2)})
    return render_template('panier.html', items=items, total=round(total, 2))

@app.route('/panier/vider')
def vider_panier():
    session.pop('panier', None)
    flash('Panier vidé.', 'info')
    return redirect(url_for('voir_panier'))

@app.route('/commander', methods=['GET', 'POST'])
@login_required
def commander():
    panier = get_panier()
    if not panier:
        flash('Votre panier est vide.', 'warning')
        return redirect(url_for('voir_panier'))
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        adresse = request.form.get('adresse', user.adresse or '')
        ville = request.form.get('ville', user.ville or '')
        # Calculer total et créer commande
        total = 0
        lignes = []
        for pid, qty in panier.items():
            p = Produit.query.get(int(pid))
            if p and p.stock >= qty:
                total += p.prix * qty
                lignes.append(LigneCommande(produit_id=p.id, quantite=qty, prix_unitaire=p.prix))
                p.stock -= qty  # Déduire le stock
        commande = Commande(
            user_id=user.id,
            total=round(total, 2),
            adresse_livraison=adresse,
            ville_livraison=ville,
            statut='En attente'
        )
        db.session.add(commande)
        db.session.flush()  # Pour obtenir l'ID de la commande
        for ligne in lignes:
            ligne.commande_id = commande.id
            db.session.add(ligne)
        db.session.commit()
        session.pop('panier', None)  # Vider le panier
        flash(f'✅ Commande #{commande.id} passée avec succès !', 'success')
        return redirect(url_for('client_commande_detail', id=commande.id))
    # Charger les produits du panier pour le récapitulatif
    produits_recap = []
    for pid in panier.keys():
        p = Produit.query.get(int(pid))
        if p:
            produits_recap.append(p)
    return render_template('commander.html', user=user, total=panier_total(), produits_recap=produits_recap)

# ─────────────────────────────────────────
# INIT DB
# ─────────────────────────────────────────

def init_db():
    with app.app_context():
        db.create_all()
        # Admin par défaut
        if not User.query.filter_by(role='admin').first():
            admin = User(
                nom='Admin', prenom='Anifashion',
                email='admin@anifashion.com',
                password=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
        # Catégories par défaut
        if Categorie.query.count() == 0:
            cats = [
                Categorie(nom='Collection Femme', emoji='👗'),
                Categorie(nom='Mini Mode', emoji='🎀'),
                Categorie(nom='Tenues de Fête', emoji='🌸'),
                Categorie(nom='Accessoires', emoji='👒'),
                Categorie(nom='Look Casual', emoji='🌿'),
            ]
            db.session.add_all(cats)
        db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
