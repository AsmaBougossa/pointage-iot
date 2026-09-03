def test_liste_employes(client):
    reponse = client.get("/api/employes")
    assert reponse.status_code == 200
    employes = reponse.get_json()
    assert len(employes) == 1
    assert employes[0]["matricule"] == "EMP-TEST-1"


def test_creation_employe(client):
    payload = {
        "nom": "Nouveau", "prenom": "Employe",
        "email": "nouveau@societe.tn", "poste": "Testeur QA",
    }
    reponse = client.post("/api/employes", json=payload)
    assert reponse.status_code == 201
    assert reponse.get_json()["nom"] == "Nouveau"


def test_desactivation_employe(client):
    liste = client.get("/api/employes").get_json()
    id_employe = liste[0]["id"]
    reponse = client.delete(f"/api/employes/{id_employe}")
    assert reponse.status_code == 200

    liste_apres = client.get("/api/employes").get_json()
    assert len(liste_apres) == 0
