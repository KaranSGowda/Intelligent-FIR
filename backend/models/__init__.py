# Import necessary modules
from datetime import datetime, timezone
import json
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Import db from extensions to avoid circular imports
from extensions import db

# Many-to-many relationship between FIR and LegalSection
fir_legal_sections = db.Table('fir_legal_sections',
    db.Column('fir_id', db.Integer, db.ForeignKey('firs.id'), primary_key=True),
    db.Column('legal_section_id', db.Integer, db.ForeignKey('legal_sections.id'), primary_key=True)
)

# Define user roles
class Role:
    PUBLIC = "public"
    POLICE = "police"
    ADMIN = "admin"

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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    legal_sections = db.Column(db.Text, nullable=True)  # JSON string of legal sections with metadata

    # Relationships
    processing_officer = db.relationship('User', foreign_keys=[processing_officer_id])
    evidence = db.relationship('Evidence', backref='fir', lazy=True, cascade="all, delete-orphan")

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
    type = db.Column(db.String(50))  # image, document, video, audio, other
    file_path = db.Column(db.String(255))
    description = db.Column(db.Text, nullable=True)
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # New fields for enhanced evidence handling
    category = db.Column(db.String(50), nullable=True)  # e.g., physical, digital, testimonial, documentary
    tags = db.Column(db.Text, nullable=True)  # JSON array of tags
    analysis_result = db.Column(db.Text, nullable=True)  # JSON with analysis results
    file_metadata = db.Column(db.Text, nullable=True)  # JSON with metadata (e.g., EXIF for images)
    location = db.Column(db.String(255), nullable=True)  # Where the evidence was collected
    collected_at = db.Column(db.DateTime, nullable=True)  # When the evidence was collected
    chain_of_custody = db.Column(db.Text, nullable=True)  # JSON array of custody events
    is_verified = db.Column(db.Boolean, default=False)  # Whether the evidence has been verified

    def get_tags(self):
        """Get tags as a list"""
        if not self.tags:
            return []
        try:
            return json.loads(self.tags)
        except:
            return []

    def set_tags(self, tags_list):
        """Set tags from a list"""
        if not tags_list:
            self.tags = None
        else:
            self.tags = json.dumps(tags_list)

    def get_analysis(self):
        """Get analysis as a dictionary"""
        if not self.analysis_result:
            return {}
        try:
            return json.loads(self.analysis_result)
        except:
            return {}

    def set_analysis(self, analysis_dict):
        """Set analysis from a dictionary"""
        if not analysis_dict:
            self.analysis_result = None
        else:
            self.analysis_result = json.dumps(analysis_dict)

    def get_metadata(self):
        """Get metadata as a dictionary"""
        if not self.file_metadata:
            return {}
        try:
            return json.loads(self.file_metadata)
        except:
            return {}

    def set_metadata(self, metadata_dict):
        """Set metadata from a dictionary"""
        if not metadata_dict:
            self.file_metadata = None
        else:
            self.file_metadata = json.dumps(metadata_dict)

    def get_chain_of_custody(self):
        """Get chain of custody as a list"""
        if not self.chain_of_custody:
            return []
        try:
            return json.loads(self.chain_of_custody)
        except:
            return []

    def add_custody_event(self, user_id, action, notes=None):
        """Add a custody event to the chain"""
        events = self.get_chain_of_custody()
        events.append({
            'user_id': user_id,
            'action': action,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'notes': notes
        })
        self.chain_of_custody = json.dumps(events)

class LegalSection(db.Model):
    __tablename__ = 'legal_sections'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50))
    name = db.Column(db.String(100))
    description = db.Column(db.Text)

