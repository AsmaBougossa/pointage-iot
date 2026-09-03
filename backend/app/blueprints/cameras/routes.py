from datetime import datetime
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Camera

cameras_bp = Blueprint("cameras", __name__)


@cameras_bp.get("")
def lister_cameras():
    cameras = Camera.query.order_by(Camera.code).all()
    return jsonify([c.to_dict() for c in cameras])


@cameras_bp.post("")
def ajouter_camera():
    data = request.get_json(force=True)
    camera = Camera(
        code=data["code"],
        nom=data["nom"],
        emplacement=data.get("emplacement"),
        adresse_ip=data.get("adresse_ip"),
        flux_url=data.get("flux_url", "0"),
        statut=data.get("statut", "hors_ligne"),
    )
    db.session.add(camera)
    db.session.commit()
    return jsonify(camera.to_dict()), 201


@cameras_bp.put("/<int:id_camera>/statut")
def changer_statut(id_camera):
    camera = Camera.query.get_or_404(id_camera)
    data = request.get_json(force=True)
    camera.statut = data["statut"]
    if data["statut"] == "en_ligne":
        camera.derniere_activite = datetime.utcnow()
    db.session.commit()
    return jsonify(camera.to_dict())


@cameras_bp.delete("/<int:id_camera>")
def supprimer_camera(id_camera):
    camera = Camera.query.get_or_404(id_camera)
    db.session.delete(camera)
    db.session.commit()
    return jsonify({"message": "Caméra supprimée"})
