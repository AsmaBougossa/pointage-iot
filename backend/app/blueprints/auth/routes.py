from datetime import datetime
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Utilisateur

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/connexion")
def connexion():
    data = request.get_json(force=True)
    email = data.get("email", "").strip().lower()
    mot_de_passe = data.get("mot_de_passe", "")

    utilisateur = Utilisateur.query.filter_by(email=email, actif=True).first()
    if not utilisateur or not check_password_hash(utilisateur.mot_de_passe_hash, mot_de_passe):
        return jsonify({"erreur": "Identifiants invalides"}), 401

    utilisateur.derniere_connexion = datetime.utcnow()
    db.session.commit()

    token = create_access_token(identity=str(utilisateur.id_utilisateur))
    return jsonify({"access_token": token, "utilisateur": utilisateur.to_dict()})


@auth_bp.post("/inscription")
def inscription():
    """Réservé à la création du premier compte admin (à sécuriser en prod)."""
    data = request.get_json(force=True)
    if Utilisateur.query.filter_by(email=data["email"]).first():
        return jsonify({"erreur": "Cet email est déjà utilisé"}), 409

    utilisateur = Utilisateur(
        nom_utilisateur=data["nom_utilisateur"],
        email=data["email"].strip().lower(),
        mot_de_passe_hash=generate_password_hash(data["mot_de_passe"]),
        role=data.get("role", "rh"),
    )
    db.session.add(utilisateur)
    db.session.commit()
    return jsonify(utilisateur.to_dict()), 201


@auth_bp.get("/moi")
@jwt_required()
def profil_courant():
    utilisateur = Utilisateur.query.get_or_404(get_jwt_identity())
    return jsonify(utilisateur.to_dict())
