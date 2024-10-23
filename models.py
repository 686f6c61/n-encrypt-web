from app import db
from datetime import datetime, timedelta

class MessageVersion(db.Model):
    """
    Modelo para almacenar versiones de mensajes.
    Cada vez que se edita un mensaje, se crea una nueva versión.
    """
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.String(64), db.ForeignKey('message.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    """
    Modelo principal para almacenar mensajes encriptados.
    """
    id = db.Column(db.String(64), primary_key=True)
    content = db.Column(db.Text, nullable=False)
    encryption_key = db.Column(db.String(256), nullable=False)
    personal_key = db.Column(db.String(256), nullable=True)
    third_party_key = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    encryption_algorithm = db.Column(db.String(10), nullable=False, default='SHA256')
    expiration_days = db.Column(db.Integer, nullable=True)
    expiration_hours = db.Column(db.Integer, nullable=True)
    expiration_minutes = db.Column(db.Integer, nullable=True)
    versions = db.relationship('MessageVersion', backref='message', lazy=True, cascade='all, delete-orphan')

    def __init__(self, *args, **kwargs):
        """
        Constructor del modelo Message.
        Establece la fecha de creación y luego la fecha de expiración basada en días, horas y minutos.
        """
        super().__init__(*args, **kwargs)
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        self.set_expiration()
        self.versions.append(MessageVersion(content=self.content))

    def set_expiration(self):
        """
        Calcula y establece la fecha de expiración basada en días, horas y minutos.
        """
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        
        if self.expiration_days or self.expiration_hours or self.expiration_minutes:
            self.expires_at = self.created_at + timedelta(
                days=self.expiration_days or 0,
                hours=self.expiration_hours or 0,
                minutes=self.expiration_minutes or 0
            )
        else:
            self.expires_at = self.created_at + timedelta(days=7)  # Expiración por defecto: 7 días

    def update_content(self, new_content):
        """
        Actualiza el contenido del mensaje y crea una nueva versión.
        """
        self.content = new_content
        self.versions.append(MessageVersion(content=new_content))
