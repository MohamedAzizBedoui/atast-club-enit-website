import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here' # TODO: Change this in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///atast.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Models ---
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Member(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    motivation = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')

# --- Helper to init DB ---
def init_db():
    with app.app_context():
        db.create_all()
        # Check if admin exists, if not create one
        if not User.query.filter_by(email='admin@atast.tn').first():
            hashed_pw = generate_password_hash('admin123', method='pbkdf2:sha256')
            admin = User(email='admin@atast.tn', password=hashed_pw, is_admin=True)
            db.session.add(admin)
            db.session.commit()
            print("Admin user created.")

# --- Routes ---

@app.route('/')
def index():
    return render_template('acceuil.html')

@app.route('/acceuil.html')
def acceuil():
    return redirect(url_for('index'))

@app.route('/a_propos.html')
def a_propos():
    return render_template('a_propos.html')

@app.route('/board_members.html')
def board_members():
    return render_template('board_members.html')

@app.route('/projets.html')
def projets():
    return render_template('projets.html')

@app.route('/event.html')
def event():
    return render_template('event.html')

@app.route('/rejoindre.html', methods=['GET', 'POST'])
def join():
    if request.method == 'POST':
        nom = request.form.get('nom')
        email = request.form.get('email')
        motivation = request.form.get('motivation')

        if not nom or not email:
            flash('Veuillez remplir tous les champs obligatoires.', 'error')
            return redirect(url_for('join'))

        existing_member = Member.query.filter_by(email=email).first()
        if existing_member:
            flash('Cet email est déjà enregistré.', 'warning')
            return redirect(url_for('join'))

        new_member = Member(nom=nom, email=email, motivation=motivation)
        db.session.add(new_member)
        db.session.commit()
        flash('Votre demande a été envoyée avec succès !', 'success')
        return redirect(url_for('join'))

    return render_template('rejoindre.html')

@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            # In a real app, we would use flask_login to manage sessions
            flash('Connexion réussie !', 'success')
            return redirect(url_for('index'))
        else:
            flash('Email ou mot de passe incorrect.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    # Placeholder for logout logic
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists('atast.db'):
        init_db()
    app.run(debug=True)
