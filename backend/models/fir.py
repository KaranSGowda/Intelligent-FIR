from datetime import datetime
from . import db

class FIR(db.Model):
    __tablename__ = 'firs'
    
    id = db.Column(db.Integer, primary_key=True)
    fir_number = db.Column(db.String(50), unique=True)
    complainant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    processing_officer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20), default='draft')
    urgency_level = db.Column(db.String(20), default='normal')
    incident_description = db.Column(db.Text)
    filed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
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