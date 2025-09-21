from datetime import datetime
from typing import Any, Dict, List, Optional

from flask_login import current_user

from extensions import mongo_db


def users_col():
    return mongo_db.users if mongo_db else None


def firs_col():
    return mongo_db.firs if mongo_db else None


def evidence_col():
    return mongo_db.evidence if mongo_db else None


def notes_col():
    return mongo_db.investigation_notes if mongo_db else None


def ensure_indexes():
    if not mongo_db:
        return
    firs_col().create_index('fir_number', unique=True)
    firs_col().create_index('complainant_id')
    firs_col().create_index('processing_officer_id')
    notes_col().create_index('fir_id')


def create_fir(complainant_id: int, description: str, location: str, incident_date: Optional[datetime]) -> Dict[str, Any]:
    doc = {
        'complainant_id': complainant_id,
        'processing_officer_id': None,
        'status': 'draft',
        'urgency_level': 'normal',
        'incident_description': description,
        'incident_location': location,
        'incident_date': incident_date,
        'filed_at': None,
        'created_at': datetime.utcnow(),
        'fir_number': f"FIR{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        'legal_sections': [],
    }
    result = firs_col().insert_one(doc)
    doc['_id'] = result.inserted_id
    return doc


def list_user_firs(user_id: int, is_police: bool) -> List[Dict[str, Any]]:
    if is_police:
        cursor = firs_col().find({'processing_officer_id': user_id})
    else:
        cursor = firs_col().find({'complainant_id': user_id})
    return list(cursor)


def get_fir(fir_id: Any) -> Optional[Dict[str, Any]]:
    from bson import ObjectId

    oid = ObjectId(fir_id) if not isinstance(fir_id, ObjectId) else fir_id
    return firs_col().find_one({'_id': oid})


def update_fir_fields(fir_id: Any, updates: Dict[str, Any]) -> bool:
    from bson import ObjectId

    oid = ObjectId(fir_id) if not isinstance(fir_id, ObjectId) else fir_id
    res = firs_col().update_one({'_id': oid}, {'$set': updates})
    return res.modified_count > 0


def delete_fir(fir_id: Any) -> bool:
    from bson import ObjectId

    oid = ObjectId(fir_id) if not isinstance(fir_id, ObjectId) else fir_id
    res = firs_col().delete_one({'_id': oid})
    return res.deleted_count > 0


def add_note(fir_id: Any, officer_id: int, content: str) -> Dict[str, Any]:
    note = {
        'fir_id': str(fir_id),
        'officer_id': officer_id,
        'content': content,
        'created_at': datetime.utcnow(),
    }
    notes_col().insert_one(note)
    return note


    


