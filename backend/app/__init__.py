import os
from flask import Flask
from app.config import config_by_name
from app.extensions import db, cors, jwt


def create_app(env=None):
    env = env or os.getenv("FLASK_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(config_by_name[env])

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["ENCODINGS_FOLDER"], exist_ok=True)

    db.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})
    jwt.init_app(app)

    register_blueprints(app)

    @app.get("/api/health")
    def health():
        return {"status": "ok", "service": "pointage-iot-backend"}

    return app


def register_blueprints(app):
    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.dashboard.routes import dashboard_bp
    from app.blueprints.employees.routes import employees_bp
    from app.blueprints.attendance.routes import attendance_bp
    from app.blueprints.cameras.routes import cameras_bp
    from app.blueprints.recognition.routes import recognition_bp
    from app.blueprints.tests_runner.routes import tests_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(employees_bp, url_prefix="/api/employes")
    app.register_blueprint(attendance_bp, url_prefix="/api/pointages")
    app.register_blueprint(cameras_bp, url_prefix="/api/cameras")
    app.register_blueprint(recognition_bp, url_prefix="/api/reconnaissance")
    app.register_blueprint(tests_bp, url_prefix="/api/tests")
