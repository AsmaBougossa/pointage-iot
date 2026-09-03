from datetime import datetime
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Pointage, Employe

attendance_bp = Blueprint("attendance", __name__)


@attendance_bp.get("")
def lister_pointages():
    date_filtre = request.args.get("date")
    id_employe = request.args.get("id_employe", type=int)
    type_evenement = request.args.get("type_evenement")
    page = request.args.get("page", 1, type=int)
    par_page = request.args.get("par_page", 20, type=int)

    query = Pointage.query
    if date_filtre:
        jour = datetime.strptime(date_filtre, "%Y-%m-%d").date()
        query = query.filter(db.func.date(Pointage.horodatage) == jour)
    if id_employe:
        query = query.filter_by(id_employe=id_employe)
    if type_evenement:
        query = query.filter_by(type_evenement=type_evenement)

    pagination = query.order_by(Pointage.horodatage.desc()).paginate(
        page=page, per_page=par_page, error_out=False
    )
    return jsonify(
        {
            "pointages": [p.to_dict() for p in pagination.items],
            "total": pagination.total,
            "page": page,
            "pages": pagination.pages,
        }
    )


@attendance_bp.post("/manuel")
def pointage_manuel():
    """Permet à un RH d'enregistrer un pointage manuellement (badge oublié, etc.)."""
    data = request.get_json(force=True)
    employe = Employe.query.get_or_404(data["id_employe"])

    pointage = Pointage(
        id_employe=employe.id_employe,
        id_camera=data.get("id_camera"),
        type_evenement=data["type_evenement"],
        source="manuel",
    )
    db.session.add(pointage)
    db.session.commit()
    return jsonify(pointage.to_dict()), 201


@attendance_bp.get("/resume/<int:id_employe>")
def resume_employe(id_employe):
    Employe.query.get_or_404(id_employe)
    pointages = (
        Pointage.query.filter_by(id_employe=id_employe)
        .order_by(Pointage.horodatage.desc())
        .limit(30)
        .all()
    )
    total_retards = sum(1 for p in pointages if p.statut == "retard")
    return jsonify(
        {
            "pointages": [p.to_dict() for p in pointages],
            "total_retards_30_derniers": total_retards,
        }
    )
