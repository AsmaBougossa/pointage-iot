"""
Blueprint "Tests auto." : permet de déclencher la suite pytest depuis
l'interface web et d'en consulter l'historique — répond au point du cahier
des charges "stratégie de test automatisée".
"""
import subprocess
import sys
import time
from pathlib import Path

from flask import Blueprint, jsonify
from app.extensions import db
from app.models import ResultatTest

tests_bp = Blueprint("tests_runner", __name__)

BACKEND_DIR = Path(__file__).resolve().parents[3]
RAPPORTS_DIR = BACKEND_DIR / "tests" / "rapports"


@tests_bp.post("/executer")
def executer_tests():
    RAPPORTS_DIR.mkdir(parents=True, exist_ok=True)
    horodatage = int(time.time())
    rapport_path = RAPPORTS_DIR / f"rapport_{horodatage}.html"

    debut = time.time()
    processus = subprocess.run(
        [
            sys.executable, "-m", "pytest", str(BACKEND_DIR / "tests"),
            f"--html={rapport_path}", "--self-contained-html", "-q",
        ],
        cwd=str(BACKEND_DIR), capture_output=True, text=True,
    )
    duree = round(time.time() - debut, 2)

    sortie = processus.stdout + processus.stderr
    nb_reussis = sortie.count(" passed") and _extraire_nombre(sortie, "passed") or 0
    nb_echoues = _extraire_nombre(sortie, "failed")
    nb_total = nb_reussis + nb_echoues

    resultat = ResultatTest(
        nom_suite="suite_complete",
        nb_total=nb_total,
        nb_reussis=nb_reussis,
        nb_echoues=nb_echoues,
        duree_secondes=duree,
        rapport_html_path=str(rapport_path.name),
    )
    db.session.add(resultat)
    db.session.commit()

    return jsonify({"resultat": resultat.to_dict(), "sortie_brute": sortie[-2000:]})


def _extraire_nombre(sortie, mot_cle):
    import re
    match = re.search(rf"(\d+) {mot_cle}", sortie)
    return int(match.group(1)) if match else 0


@tests_bp.get("/historique")
def historique_tests():
    resultats = ResultatTest.query.order_by(ResultatTest.date_execution.desc()).limit(20).all()
    return jsonify([r.to_dict() for r in resultats])
