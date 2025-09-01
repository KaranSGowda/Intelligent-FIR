from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

# Define user roles
class Role:
    PUBLIC = "public"
    POLICE = "police"
    ADMIN = "admin"

# Many-to-many relationship between FIR and LegalSection
fir_legal_sections = db.Table('fir_legal_sections',
    db.Column('fir_id', db.Integer, db.ForeignKey('firs.id'), primary_key=True),
    db.Column('legal_section_id', db.Integer, db.ForeignKey('legal_sections.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(256))
    full_name = db.Column(db.String(100))
    role = db.Column(db.String(20), default=Role.PUBLIC)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    firs = db.relationship('FIR', backref='complainant', lazy=True,
                      foreign_keys='FIR.complainant_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == Role.ADMIN

    def is_police(self):
        return self.role == Role.POLICE

    def is_public(self):
        return self.role == Role.PUBLIC

class FIR(db.Model):
    __tablename__ = 'firs'

    id = db.Column(db.Integer, primary_key=True)
    fir_number = db.Column(db.String(50), unique=True)
    complainant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    processing_officer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20), default='draft')
    urgency_level = db.Column(db.String(20), default='normal')
    incident_description = db.Column(db.Text)
    incident_location = db.Column(db.String(200))
    incident_date = db.Column(db.DateTime, nullable=True)
    filed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    transcription = db.Column(db.Text, nullable=True)
    legal_sections = db.Column(db.Text, nullable=True)  # JSON string of legal sections
    pdf_path = db.Column(db.String(255), nullable=True)  # Path to the stored PDF file

    # Relationships
    processing_officer = db.relationship('User', foreign_keys=[processing_officer_id])
    evidence = db.relationship('Evidence', backref='fir', lazy=True, cascade="all, delete-orphan")
    investigation_notes = db.relationship(
        'InvestigationNote', backref='fir', lazy=True, cascade="all, delete-orphan", order_by="desc(InvestigationNote.created_at)"
    )

    def get_status_label(self):
        status_labels = {
            'draft': 'Draft',
            'filed': 'Filed',
            'under_investigation': 'Under Investigation',
            'closed': 'Closed'
        }
        return status_labels.get(self.status, self.status)

    def get_urgency_label(self):
        urgency_labels = {
            'low': 'Low',
            'normal': 'Normal',
            'high': 'High',
            'critical': 'Critical'
        }
        return urgency_labels.get(self.urgency_level, self.urgency_level)

class Evidence(db.Model):
    __tablename__ = 'evidence'

    id = db.Column(db.Integer, primary_key=True)
    fir_id = db.Column(db.Integer, db.ForeignKey('firs.id'))
    type = db.Column(db.String(50))
    file_path = db.Column(db.String(255))
    description = db.Column(db.Text, nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class LegalSection(db.Model):
    __tablename__ = 'legal_sections'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50))
    name = db.Column(db.String(100))
    description = db.Column(db.Text)

class InvestigationNote(db.Model):
    __tablename__ = 'investigation_notes'
    id = db.Column(db.Integer, primary_key=True)
    fir_id = db.Column(db.Integer, db.ForeignKey('firs.id'), nullable=False)
    officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    officer = db.relationship('User', foreign_keys=[officer_id])




