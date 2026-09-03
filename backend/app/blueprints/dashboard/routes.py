from datetime import datetime, timedelta
from flask import Blueprint, jsonify
from sqlalchemy import func
from app.extensions import db
from app.models import Employe, Pointage, Camera, Departement, Alerte

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/statistiques")
def statistiques():
    aujourdhui = datetime.utcnow().date()

    total_employes = Employe.query.filter_by(actif=True).count()

    presents_ids = {
        p.id_employe
        for p in Pointage.query.filter(
            func.date(Pointage.horodatage) == aujourdhui,
            Pointage.type_evenement == "entree",
        ).all()
    }
    presents = len(presents_ids)
    absents = max(total_employes - presents, 0)

    cameras_total = Camera.query.count()
    cameras_en_ligne = Camera.query.filter_by(statut="en_ligne").count()

    return jsonify(
        {
            "total_employes": total_employes,
            "presents_aujourdhui": presents,
            "taux_presence": round((presents / total_employes * 100) if total_employes else 0, 1),
            "absents_aujourdhui": absents,
            "cameras_en_ligne": cameras_en_ligne,
            "cameras_total": cameras_total,
        }
    )


@dashboard_bp.get("/activite-recente")
def activite_recente():
    pointages = (
        Pointage.query.order_by(Pointage.horodatage.desc()).limit(8).all()
    )
    return jsonify([p.to_dict() for p in pointages])


@dashboard_bp.get("/presence-hebdomadaire")
def presence_hebdomadaire():
    aujourdhui = datetime.utcnow().date()
    resultats = []
    jours_labels = ["L", "M", "M", "J", "V", "S", "D"]

    for i in range(6, -1, -1):
        jour = aujourdhui - timedelta(days=i)
        total_employes = Employe.query.filter_by(actif=True).count()
        presents = (
            db.session.query(func.count(func.distinct(Pointage.id_employe)))
            .filter(
                func.date(Pointage.horodatage) == jour,
                Pointage.type_evenement == "entree",
            )
            .scalar()
        )
        absents = max(total_employes - presents, 0)
        resultats.append(
            {
                "date": jour.isoformat(),
                "label": jours_labels[jour.weekday()],
                "presents": presents,
                "absents": absents,
                "pourcentage_presence": round(
                    (presents / total_employes * 100) if total_employes else 0
                ),
            }
        )
    return jsonify(resultats)


@dashboard_bp.get("/presence-departements")
def presence_departements():
    departements = Departement.query.all()
    return jsonify([d.to_dict(with_stats=True) for d in departements])


@dashboard_bp.get("/alertes")
def alertes_recentes():
    alertes = Alerte.query.order_by(Alerte.date_creation.desc()).limit(10).all()
    return jsonify([a.to_dict() for a in alertes])
