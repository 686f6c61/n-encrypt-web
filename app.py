import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase
from flask_cors import CORS

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
migrate = Migrate()

app = Flask(__name__)
# Configure CORS with specific settings
CORS(app, resources={
    r"/*": {
        "origins": ["chrome-extension://*", "http://localhost:*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)
migrate.init_app(app, db)

with app.app_context():
    import models
    db.create_all()

import routes

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
