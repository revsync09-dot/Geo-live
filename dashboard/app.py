from __future__ import annotations

import os
from flask import Flask, render_template, send_from_directory
from dotenv import load_dotenv

from dashboard.routes.auth import auth_bp
from dashboard.routes.main import main_bp


def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")

    app.config.update(
        DISCORD_CLIENT_ID=os.getenv("DISCORD_CLIENT_ID", ""),
        DISCORD_CLIENT_SECRET=os.getenv("DISCORD_CLIENT_SECRET", ""),
        REDIRECT_URI=os.getenv("REDIRECT_URI", ""),
        GEOLOGO_URL="/assets/geolive_logo.png",
    )

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    @app.route("/")
    def home():
        return render_template("login.html")

    @app.route("/assets/<path:filename>")
    def assets(filename: str):
        return send_from_directory(os.path.join(app.root_path, "assets"), filename)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
