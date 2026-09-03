def test_healthcheck(client):
    reponse = client.get("/api/health")
    assert reponse.status_code == 200
    assert reponse.get_json()["status"] == "ok"


def test_statistiques_dashboard(client):
    reponse = client.get("/api/dashboard/statistiques")
    assert reponse.status_code == 200
    data = reponse.get_json()
    assert "total_employes" in data
    assert data["total_employes"] == 1


def test_presence_hebdomadaire_renvoie_7_jours(client):
    reponse = client.get("/api/dashboard/presence-hebdomadaire")
    assert reponse.status_code == 200
    assert len(reponse.get_json()) == 7
