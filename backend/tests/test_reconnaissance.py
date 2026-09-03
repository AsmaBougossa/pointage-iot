def test_simulation_reconnaissance_cree_un_pointage(client):
    reponse = client.post("/api/reconnaissance/simuler")
    assert reponse.status_code == 201
    data = reponse.get_json()
    assert data["source"] == "simulation"
    assert data["type_evenement"] in ("entree", "sortie")


def test_pointages_apparaissent_dans_activite_recente(client):
    client.post("/api/reconnaissance/simuler")
    reponse = client.get("/api/dashboard/activite-recente")
    assert reponse.status_code == 200
    assert len(reponse.get_json()) >= 1
