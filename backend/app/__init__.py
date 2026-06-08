import os
from flask import Flask
from .config import Config
from .extensions import db, cors

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Make sure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.root_path, '../instance'), exist_ok=True)

    db.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Import and register blueprints here
    from .routes.analyze import analyze_bp
    from .routes.history import history_bp
    from .routes.compare import compare_bp
    from .routes.export import export_bp
    from .routes.interview import interview_bp
    
    app.register_blueprint(analyze_bp, url_prefix='/api')
    app.register_blueprint(history_bp, url_prefix='/api')
    app.register_blueprint(compare_bp, url_prefix='/api')
    app.register_blueprint(export_bp, url_prefix='/api')
    app.register_blueprint(interview_bp, url_prefix='/api')

    with app.app_context():
        from . import models  # Ensure models are imported before creating tables
        db.create_all()

    return app
