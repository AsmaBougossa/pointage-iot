"""
Service de reconnaissance faciale.
Utilise `face_recognition` (dlib) pour l'encodage 128D et OpenCV pour
la capture/traitement des flux caméra IoT.
"""
import base64
import json
import os
import uuid
from io import BytesIO

import numpy as np
from PIL import Image

try:
    import face_recognition
    FACE_RECOGNITION_DISPONIBLE = True
except ImportError:
    # Permet de démarrer l'API même si dlib/face_recognition n'est pas
    # encore compilé sur la machine de dev (Windows notamment).
    FACE_RECOGNITION_DISPONIBLE = False


def _decoder_image_base64(photo_base64: str) -> np.ndarray:
    if "," in photo_base64:
        photo_base64 = photo_base64.split(",", 1)[1]
    donnees = base64.b64decode(photo_base64)
    image = Image.open(BytesIO(donnees)).convert("RGB")
    return np.array(image)


def encoder_visage_depuis_image(photo_base64: str, matricule: str, app_config: dict):
    """Encode le visage d'une photo d'inscription et sauvegarde le fichier.

    Retourne (encodage_128d: list|None, chemin_relatif_photo: str)
    """
    image = _decoder_image_base64(photo_base64)

    nom_fichier = f"{matricule}_{uuid.uuid4().hex[:8]}.jpg"
    chemin_absolu = os.path.join(app_config["UPLOAD_FOLDER"], nom_fichier)
    Image.fromarray(image).save(chemin_absolu, quality=90)
    chemin_relatif = f"uploads/{nom_fichier}"

    if not FACE_RECOGNITION_DISPONIBLE:
        return None, chemin_relatif

    emplacements = face_recognition.face_locations(image, model="hog")
    if not emplacements:
        return None, chemin_relatif

    encodages = face_recognition.face_encodings(image, known_face_locations=emplacements)
    if not encodages:
        return None, chemin_relatif

    return encodages[0].tolist(), chemin_relatif


def charger_encodages_connus(employes):
    """Construit les tableaux (encodages, ids) à partir des employés en base."""
    encodages_connus, ids_employes = [], []
    for employe in employes:
        if not employe.encodage_facial:
            continue
        try:
            vecteur = json.loads(employe.encodage_facial)
            encodages_connus.append(np.array(vecteur))
            ids_employes.append(employe.id_employe)
        except (json.JSONDecodeError, TypeError):
            continue
    return encodages_connus, ids_employes


def reconnaitre_visages_sur_frame(frame_bgr, encodages_connus, ids_employes, tolerance=0.5):
    """Détecte et reconnaît les visages présents dans une frame OpenCV (BGR).

    Retourne une liste de résultats : [{id_employe, score_confiance, boite}]
    """
    if not FACE_RECOGNITION_DISPONIBLE:
        return []

    frame_rgb = frame_bgr[:, :, ::-1]
    emplacements = face_recognition.face_locations(frame_rgb, model="hog")
    encodages_frame = face_recognition.face_encodings(frame_rgb, known_face_locations=emplacements)

    resultats = []
    for encodage, boite in zip(encodages_frame, emplacements):
        if not encodages_connus:
            resultats.append({"id_employe": None, "score_confiance": 0.0, "boite": boite})
            continue

        distances = face_recognition.face_distance(encodages_connus, encodage)
        meilleur_index = int(np.argmin(distances))
        distance_min = distances[meilleur_index]

        if distance_min <= tolerance:
            score = round((1 - distance_min) * 100, 1)
            resultats.append(
                {
                    "id_employe": ids_employes[meilleur_index],
                    "score_confiance": score,
                    "boite": boite,
                }
            )
        else:
            resultats.append({"id_employe": None, "score_confiance": 0.0, "boite": boite})

    return resultats
