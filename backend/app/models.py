from datetime import datetime
from app.extensions import db


class Departement(db.Model):
    __tablename__ = "departements"
    id_departement = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), unique=True, nullable=False)
    couleur = db.Column(db.String(20), default="#5b9dff")
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    employes = db.relationship("Employe", backref="departement", lazy=True)

    def to_dict(self, with_stats=False):
        data = {
            "id": self.id_departement,
            "nom": self.nom,
            "couleur": self.couleur,
        }
        if with_stats:
            actifs = [e for e in self.employes if e.actif]
            presents = sum(1 for e in actifs if e.est_present_aujourdhui())
            data["effectif_total"] = len(actifs)
            data["presents_aujourdhui"] = presents
            data["taux_presence"] = round(
                (presents / len(actifs) * 100) if actifs else 0, 1
            )
        return data


class Utilisateur(db.Model):
    __tablename__ = "utilisateurs"
    id_utilisateur = db.Column(db.Integer, primary_key=True)
    nom_utilisateur = db.Column(db.String(60), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mot_de_passe_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("admin", "rh", "superviseur"), default="rh")
    actif = db.Column(db.Boolean, default=True)
    derniere_connexion = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id_utilisateur,
            "nom_utilisateur": self.nom_utilisateur,
            "email": self.email,
            "role": self.role,
        }


class Employe(db.Model):
    __tablename__ = "employes"
    id_employe = db.Column(db.Integer, primary_key=True)
    matricule = db.Column(db.String(20), unique=True, nullable=False)
    nom = db.Column(db.String(60), nullable=False)
    prenom = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(120), unique=True)
    telephone = db.Column(db.String(20))
    id_departement = db.Column(db.Integer, db.ForeignKey("departements.id_departement"))
    poste = db.Column(db.String(100))
    photo_path = db.Column(db.String(255))
    encodage_facial = db.Column(db.Text)  # JSON du vecteur 128D
    heure_entree_prevue = db.Column(db.Time)
    heure_sortie_prevue = db.Column(db.Time)
    actif = db.Column(db.Boolean, default=True)
    date_embauche = db.Column(db.Date)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    pointages = db.relationship(
        "Pointage", backref="employe", lazy=True, cascade="all, delete-orphan"
    )

    def est_present_aujourdhui(self):
        aujourdhui = datetime.utcnow().date()
        return any(
            p.type_evenement == "entree" and p.horodatage.date() == aujourdhui
            for p in self.pointages
        )

    def to_dict(self):
        return {
            "id": self.id_employe,
            "matricule": self.matricule,
            "nom": self.nom,
            "prenom": self.prenom,
            "nom_complet": f"{self.prenom} {self.nom}",
            "initiales": f"{self.prenom[:1]}{self.nom[:1]}".upper(),
            "email": self.email,
            "telephone": self.telephone,
            "departement": self.departement.nom if self.departement else None,
            "id_departement": self.id_departement,
            "poste": self.poste,
            "photo_path": self.photo_path,
            "a_un_encodage": bool(self.encodage_facial),
            "actif": self.actif,
            "present_aujourdhui": self.est_present_aujourdhui(),
        }


class Camera(db.Model):
    __tablename__ = "cameras"
    id_camera = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    emplacement = db.Column(db.String(150))
    adresse_ip = db.Column(db.String(45))
    flux_url = db.Column(db.String(255))
    statut = db.Column(
        db.Enum("en_ligne", "hors_ligne", "maintenance"), default="hors_ligne"
    )
    derniere_activite = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id_camera,
            "code": self.code,
            "nom": self.nom,
            "emplacement": self.emplacement,
            "adresse_ip": self.adresse_ip,
            "flux_url": self.flux_url,
            "statut": self.statut,
            "derniere_activite": (
                self.derniere_activite.isoformat() if self.derniere_activite else None
            ),
        }


class Pointage(db.Model):
    __tablename__ = "pointages"
    id_pointage = db.Column(db.Integer, primary_key=True)
    id_employe = db.Column(db.Integer, db.ForeignKey("employes.id_employe"), nullable=False)
    id_camera = db.Column(db.Integer, db.ForeignKey("cameras.id_camera"))
    type_evenement = db.Column(db.Enum("entree", "sortie"), nullable=False)
    horodatage = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    score_confiance = db.Column(db.Numeric(5, 2))
    statut = db.Column(
        db.Enum("a_lheure", "retard", "anticipe"), default="a_lheure"
    )
    snapshot_path = db.Column(db.String(255))
    source = db.Column(
        db.Enum("reconnaissance_auto", "manuel", "simulation"),
        default="reconnaissance_auto",
    )

    camera = db.relationship("Camera")

    def to_dict(self):
        return {
            "id": self.id_pointage,
            "employe": self.employe.to_dict() if self.employe else None,
            "camera": self.camera.code if self.camera else None,
            "type_evenement": self.type_evenement,
            "horodatage": self.horodatage.isoformat(),
            "heure": self.horodatage.strftime("%H:%M"),
            "score_confiance": float(self.score_confiance) if self.score_confiance else None,
            "statut": self.statut,
            "source": self.source,
        }


class Alerte(db.Model):
    __tablename__ = "alertes"
    id_alerte = db.Column(db.Integer, primary_key=True)
    type_alerte = db.Column(
        db.Enum(
            "absence_non_justifiee",
            "retard_repete",
            "camera_hors_ligne",
            "visage_inconnu",
            "doublon_pointage",
        ),
        nullable=False,
    )
    gravite = db.Column(db.Enum("info", "warning", "critique"), default="warning")
    id_employe = db.Column(db.Integer, db.ForeignKey("employes.id_employe"), nullable=True)
    id_camera = db.Column(db.Integer, db.ForeignKey("cameras.id_camera"), nullable=True)
    message = db.Column(db.String(255), nullable=False)
    lue = db.Column(db.Boolean, default=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id_alerte,
            "type_alerte": self.type_alerte,
            "gravite": self.gravite,
            "message": self.message,
            "lue": self.lue,
            "date_creation": self.date_creation.isoformat(),
        }


class ResultatTest(db.Model):
    __tablename__ = "resultats_tests"
    id_resultat = db.Column(db.Integer, primary_key=True)
    nom_suite = db.Column(db.String(120), nullable=False)
    nb_total = db.Column(db.Integer, default=0)
    nb_reussis = db.Column(db.Integer, default=0)
    nb_echoues = db.Column(db.Integer, default=0)
    duree_secondes = db.Column(db.Numeric(6, 2))
    rapport_html_path = db.Column(db.String(255))
    date_execution = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id_resultat,
            "nom_suite": self.nom_suite,
            "nb_total": self.nb_total,
            "nb_reussis": self.nb_reussis,
            "nb_echoues": self.nb_echoues,
            "taux_reussite": round(
                (self.nb_reussis / self.nb_total * 100) if self.nb_total else 0, 1
            ),
            "duree_secondes": float(self.duree_secondes) if self.duree_secondes else None,
            "date_execution": self.date_execution.isoformat(),
        }
