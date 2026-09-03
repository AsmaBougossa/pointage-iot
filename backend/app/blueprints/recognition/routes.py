from flask import Blueprint, request, jsonify, current_app, Response
from app.extensions import db
from app.models import Employe, Camera, Pointage, Alerte
from app.services.face_service import (
    charger_encodages_connus,
    reconnaitre_visages_sur_frame,
    _decoder_image_base64,
)
from app.services.camera_service import GestionnaireCamera

recognition_bp = Blueprint("recognition", __name__)


def _enregistrer_pointage(id_employe, id_camera, score, source="reconnaissance_auto"):
    from datetime import datetime, time as dtime

    employe = Employe.query.get(id_employe)
    if not employe:
        return None

    aujourdhui = datetime.utcnow().date()
    dernier = (
        Pointage.query.filter_by(id_employe=id_employe)
        .filter(db.func.date(Pointage.horodatage) == aujourdhui)
        .order_by(Pointage.horodatage.desc())
        .first()
    )
    type_evenement = "sortie" if (dernier and dernier.type_evenement == "entree") else "entree"

    statut = "a_lheure"
    maintenant = datetime.utcnow().time()
    if type_evenement == "entree" and employe.heure_entree_prevue:
        if maintenant > employe.heure_entree_prevue:
            statut = "retard"

    pointage = Pointage(
        id_employe=id_employe,
        id_camera=id_camera,
        type_evenement=type_evenement,
        score_confiance=score,
        statut=statut,
        source=source,
    )
    db.session.add(pointage)

    if statut == "retard":
        db.session.add(
            Alerte(
                type_alerte="retard_repete",
                gravite="warning",
                id_employe=id_employe,
                message=f"Retard détecté pour {employe.prenom} {employe.nom}",
            )
        )

    db.session.commit()
    return pointage


@recognition_bp.post("/analyser-image")
def analyser_image():
    """Reçoit une image (base64) issue de la caméra IoT / webcam et tente
    une reconnaissance faciale, puis enregistre le pointage si un employé
    est identifié avec un score suffisant."""
    data = request.get_json(force=True)
    image = _decoder_image_base64(data["photo_base64"])
    id_camera = data.get("id_camera")

    employes = Employe.query.filter(Employe.actif.is_(True), Employe.encodage_facial.isnot(None)).all()
    encodages_connus, ids_employes = charger_encodages_connus(employes)

    import cv2
    frame_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    tolerance = current_app.config["FACE_RECOGNITION_TOLERANCE"]
    resultats = reconnaitre_visages_sur_frame(frame_bgr, encodages_connus, ids_employes, tolerance)

    reponses = []
    for r in resultats:
        if r["id_employe"]:
            pointage = _enregistrer_pointage(r["id_employe"], id_camera, r["score_confiance"])
            reponses.append(pointage.to_dict() if pointage else None)
        else:
            reponses.append({"reconnu": False, "score_confiance": r["score_confiance"]})

    return jsonify({"visages_detectes": len(resultats), "resultats": reponses})


@recognition_bp.post("/simuler")
def simuler_reconnaissance():
    """Bouton "Simuler reconnaissance" du dashboard : choisit un employé
    aléatoirement pour démontrer le pipeline sans caméra physique branchée."""
    import random

    data = request.get_json(silent=True) or {}
    employes = Employe.query.filter_by(actif=True).all()
    if not employes:
        return jsonify({"erreur": "Aucun employé enregistré"}), 400

    employe = random.choice(employes)
    camera = Camera.query.filter_by(statut="en_ligne").first()
    score = round(random.uniform(85, 98), 1)

    pointage = _enregistrer_pointage(
        employe.id_employe,
        camera.id_camera if camera else None,
        score,
        source="simulation",
    )
    return jsonify(pointage.to_dict()), 201


@recognition_bp.get("/flux/<int:id_camera>")
def flux_video(id_camera):
    """Flux MJPEG en direct avec overlay de reconnaissance — à consommer
    depuis React via <img src="/api/reconnaissance/flux/1" />."""
    camera = Camera.query.get_or_404(id_camera)
    employes = Employe.query.filter(Employe.encodage_facial.isnot(None)).all()

    gestionnaire = GestionnaireCamera(camera.flux_url or "0")
    tolerance = current_app.config["FACE_RECOGNITION_TOLERANCE"]

    def on_reconnaissance(id_employe, score):
        _enregistrer_pointage(id_employe, id_camera, score)

    return Response(
        gestionnaire.generer_flux_mjpeg(employes, tolerance, on_reconnaissance),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )
