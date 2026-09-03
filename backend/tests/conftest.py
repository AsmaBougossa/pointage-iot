import pytest
from app import create_app
from app.extensions import db
from app.models import Departement, Employe, Camera


@pytest.fixture()
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        _peupler_donnees_test()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def _peupler_donnees_test():
    dep = Departement(nom="Informatique", couleur="#5b9dff")
    db.session.add(dep)
    db.session.flush()

    employe = Employe(
        matricule="EMP-TEST-1", nom="Test", prenom="Utilisateur",
        email="test@societe.tn", id_departement=dep.id_departement,
        heure_entree_prevue="08:30:00", heure_sortie_prevue="17:30:00",
    )
    camera = Camera(code="CAM-TEST", nom="Caméra test", statut="en_ligne", flux_url="0")
    db.session.add_all([employe, camera])
    db.session.commit()
