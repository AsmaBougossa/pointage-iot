import base64
import json
import os
from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models import Employe, Departement
from app.services.face_service import encoder_visage_depuis_image

employees_bp = Blueprint("employees", __name__)


@employees_bp.get("")
def lister_employes():
    departement = request.args.get("departement")
    recherche = request.args.get("q")
    query = Employe.query.filter_by(actif=True)
    if departement:
        query = query.join(Departement).filter(Departement.nom == departement)
    if recherche:
        like = f"%{recherche}%"
        query = query.filter(
            db.or_(Employe.nom.ilike(like), Employe.prenom.ilike(like), Employe.matricule.ilike(like))
        )
    employes = query.order_by(Employe.nom).all()
    return jsonify([e.to_dict() for e in employes])


@employees_bp.get("/<int:id_employe>")
def obtenir_employe(id_employe):
    employe = Employe.query.get_or_404(id_employe)
    return jsonify(employe.to_dict())


@employees_bp.post("")
def creer_employe():
    data = request.get_json(force=True)
    dernier = Employe.query.order_by(Employe.id_employe.desc()).first()
    prochain_num = (dernier.id_employe + 1) if dernier else 1

    employe = Employe(
        matricule=data.get("matricule") or f"EMP-{prochain_num:03d}",
        nom=data["nom"],
        prenom=data["prenom"],
        email=data.get("email"),
        telephone=data.get("telephone"),
        id_departement=data.get("id_departement"),
        poste=data.get("poste"),
        heure_entree_prevue=data.get("heure_entree_prevue", "08:30:00"),
        heure_sortie_prevue=data.get("heure_sortie_prevue", "17:30:00"),
        date_embauche=data.get("date_embauche"),
    )

    # Photo d'inscription faciale envoyée en base64 (data URL)
    photo_base64 = data.get("photo_base64")
    if photo_base64:
        encodage, chemin_photo = encoder_visage_depuis_image(
            photo_base64, employe.matricule, current_app.config
        )
        employe.encodage_facial = json.dumps(encodage) if encodage else None
        employe.photo_path = chemin_photo

    db.session.add(employe)
    db.session.commit()
    return jsonify(employe.to_dict()), 201


@employees_bp.put("/<int:id_employe>")
def modifier_employe(id_employe):
    employe = Employe.query.get_or_404(id_employe)
    data = request.get_json(force=True)

    for champ in ["nom", "prenom", "email", "telephone", "poste", "id_departement",
                  "heure_entree_prevue", "heure_sortie_prevue", "date_embauche"]:
        if champ in data:
            setattr(employe, champ, data[champ])

    photo_base64 = data.get("photo_base64")
    if photo_base64:
        encodage, chemin_photo = encoder_visage_depuis_image(
            photo_base64, employe.matricule, current_app.config
        )
        employe.encodage_facial = json.dumps(encodage) if encodage else None
        employe.photo_path = chemin_photo

    db.session.commit()
    return jsonify(employe.to_dict())


@employees_bp.delete("/<int:id_employe>")
def desactiver_employe(id_employe):
    employe = Employe.query.get_or_404(id_employe)
    employe.actif = False
    db.session.commit()
    return jsonify({"message": "Employé désactivé"})
