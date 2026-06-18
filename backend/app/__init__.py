import os
import logging
from flask import Flask, jsonify
from .config import Config
from .extensions import db, cors

logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ── Structured logging setup ──────────────────────────────────────────────
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S',
    )

    # ── Ensure required directories exist ────────────────────────────────────
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.root_path, '../instance'), exist_ok=True)

    # ── Initialize extensions ─────────────────────────────────────────────────
    db.init_app(app)

    # B7 FIX: Use specific origins from config, not wildcard
    allowed_origins = app.config.get('ALLOWED_ORIGINS', ['http://localhost:5173'])
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": allowed_origins}},
        supports_credentials=False,
    )

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    try:
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address

        limiter = Limiter(
            key_func=get_remote_address,
            app=app,
            default_limits=["200 per hour", "30 per minute"],
            storage_uri=app.config.get('RATELIMIT_STORAGE_URL', 'memory://'),
        )
        app.extensions['limiter'] = limiter
        logger.info("Rate limiter initialized.")
    except ImportError:
        logger.warning("flask-limiter not installed. Rate limiting disabled.")

    # ── Register Blueprints ───────────────────────────────────────────────────
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

    # ── Health Check Endpoint ─────────────────────────────────────────────────
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Production health check endpoint for load balancers / uptime monitors."""
        from .extensions import db
        try:
            db.session.execute(db.text('SELECT 1'))
            db_status = "healthy"
        except Exception as e:
            logger.error(f"DB health check failed: {e}")
            db_status = "unhealthy"

        gemini_configured = bool(app.config.get('GEMINI_API_KEY'))

        status = "healthy" if db_status == "healthy" else "degraded"
        return jsonify({
            "status": status,
            "database": db_status,
            "gemini_api": "configured" if gemini_configured else "not configured",
            "version": "2.0.0",
        }), 200 if status == "healthy" else 503

    # ── Global Error Handlers ─────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found.", "code": 404}), 404

    @app.errorhandler(429)
    def ratelimit_error(e):
        return jsonify({
            "error": "Too many requests. Please slow down.",
            "code": 429,
            "retry_after": str(e.description)
        }), 429

    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Internal server error: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred.", "code": 500}), 500

    # ── DB table creation ─────────────────────────────────────────────────────
    with app.app_context():
        from . import models  # Ensure models are imported before creating tables
        db.create_all()
        logger.info("Database tables verified/created.")

    return app
