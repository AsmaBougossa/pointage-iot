"""
Service de capture vidéo IoT — encapsule OpenCV VideoCapture pour un flux
webcam local (index) ou distant (RTSP/HTTP), avec dessin des boîtes de
reconnaissance en direct pour le flux MJPEG consommé par le frontend React.
"""
import time
import cv2

from app.services.face_service import (
    charger_encodages_connus,
    reconnaitre_visages_sur_frame,
)


class GestionnaireCamera:
    """Gère l'ouverture/fermeture d'un flux OpenCV pour une caméra donnée."""

    def __init__(self, source):
        # `source` peut être un index webcam ("0") ou une URL RTSP/HTTP
        self.source = int(source) if str(source).isdigit() else source
        self.capture = None

    def ouvrir(self):
        self.capture = cv2.VideoCapture(self.source)
        return self.capture.isOpened()

    def fermer(self):
        if self.capture is not None:
            self.capture.release()

    def generer_flux_mjpeg(self, employes, tolerance=0.5, on_reconnaissance=None):
        """Générateur MJPEG (multipart/x-mixed-replace) avec overlay de
        reconnaissance faciale — consommé directement par une balise <img>
        côté React (page "Flux en direct")."""
        if self.capture is None:
            self.ouvrir()

        encodages_connus, ids_employes = charger_encodages_connus(employes)
        derniere_reconnaissance = {}

        while True:
            ok, frame = self.capture.read()
            if not ok:
                time.sleep(0.5)
                continue

            resultats = reconnaitre_visages_sur_frame(
                frame, encodages_connus, ids_employes, tolerance
            )

            for r in resultats:
                haut, droite, bas, gauche = r["boite"]
                couleur = (34, 197, 94) if r["id_employe"] else (239, 68, 68)
                cv2.rectangle(frame, (gauche, haut), (droite, bas), couleur, 2)
                etiquette = f"{r['score_confiance']}%" if r["id_employe"] else "Inconnu"
                cv2.putText(
                    frame, etiquette, (gauche, bas + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, couleur, 2,
                )

                if r["id_employe"] and on_reconnaissance:
                    cle = r["id_employe"]
                    maintenant = time.time()
                    # Anti-doublon : 1 seul événement toutes les 30s / employé
                    if maintenant - derniere_reconnaissance.get(cle, 0) > 30:
                        derniere_reconnaissance[cle] = maintenant
                        on_reconnaissance(r["id_employe"], r["score_confiance"])

            ok, buffer = cv2.imencode(".jpg", frame)
            if not ok:
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
            )
