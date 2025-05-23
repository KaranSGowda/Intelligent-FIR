from flask import render_template, current_app
import pdfkit
import os
import base64
from datetime import datetime, timezone
import logging
import json
from utils.qr_generator import generate_verification_qr, generate_document_id
from models import LegalSection, Evidence, User

# Configure logging
logger = logging.getLogger(__name__)

def generate_fir_pdf(fir, user, legal_sections, evidence=None):
    """
    Generate a professional PDF file for the FIR

    Args:
        fir: The FIR object
        user: The user who filed the complaint
        legal_sections: List of legal sections applied
        evidence: List of evidence items (optional)

    Returns:
        str: The path to the generated PDF file
    """
    try:
        # Create directory to store PDFs if it doesn't exist
        pdf_dir = os.path.join('static', 'pdfs')
        os.makedirs(pdf_dir, exist_ok=True)

        # Generate a unique document ID
        document_id = generate_document_id(fir.fir_number)

        # Generate QR code for verification
        verification_qr = generate_verification_qr(
            fir_number=fir.fir_number,
            document_id=document_id,
            base_url=current_app.config.get('BASE_URL', 'http://localhost:5000')
        )

        # Get the path to the national emblem
        emblem_path = os.path.join('static', 'images', 'pdf', 'national_emblem.svg')

        # Prepare evidence items if provided
        evidence_items = []
        if evidence:
            for item in evidence:
                # Convert relative paths to absolute paths for PDF generation
                if item.file_path and os.path.exists(item.file_path):
                    evidence_items.append({
                        'type': item.type,
                        'file_path': os.path.abspath(item.file_path),
                        'description': item.description,
                        'uploaded_at': item.uploaded_at
                    })

        # Prepare template context
        context = {
            'fir': fir,
            'user': user,
            'legal_sections': legal_sections,
            'evidence': evidence_items,
            'document_id': document_id,
            'verification_qr': verification_qr,
            'emblem_path': os.path.abspath(emblem_path),
            'generation_date': datetime.now(timezone.utc).strftime('%d-%m-%Y %H:%M:%S'),
            'police_station_name': 'Central Police Station',
            'district_name': 'Central District',
            'state_name': 'State'
        }

        # Render the HTML template
        html_content = render_template('pdf/fir_template.html', **context)

        # Generate a unique filename
        filename = f"fir_{fir.fir_number}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.pdf"
        pdf_path = os.path.join(pdf_dir, filename)

        # Configure PDF options
        options = {
            'page-size': 'A4',
            'margin-top': '10mm',
            'margin-right': '10mm',
            'margin-bottom': '10mm',
            'margin-left': '10mm',
            'encoding': 'UTF-8',
            'no-outline': None,
            'enable-local-file-access': None
        }

        # Generate PDF from HTML
        pdfkit.from_string(html_content, pdf_path, options=options)

        logger.info(f"Generated PDF for FIR {fir.fir_number}: {pdf_path}")
        return pdf_path
    except Exception as e:
        logger.error(f"Failed to generate PDF: {str(e)}", exc_info=True)
        raise Exception(f"Failed to generate PDF: {e}")

def generate_fir_pdf_simple(fir, user, legal_sections):
    """
    Generate a simple PDF file for the FIR (fallback method)

    Args:
        fir: The FIR object
        user: The user who filed the complaint
        legal_sections: List of legal sections applied

    Returns:
        str: The path to the generated PDF file
    """
    try:
        # Create directory to store PDFs if it doesn't exist
        pdf_dir = os.path.join('static', 'pdfs')
        os.makedirs(pdf_dir, exist_ok=True)

        # Generate HTML content for PDF
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>FIR #{fir.fir_number}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                .header {{ text-align: center; border-bottom: 1px solid #000; padding-bottom: 10px; margin-bottom: 20px; }}
                .section {{ margin-bottom: 15px; }}
                .section-title {{ font-weight: bold; margin-bottom: 5px; }}
                .footer {{ margin-top: 30px; border-top: 1px solid #000; padding-top: 10px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                table, th, td {{ border: 1px solid #000; }}
                th, td {{ padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>FIRST INFORMATION REPORT</h1>
                <h2>FIR Number: {fir.fir_number}</h2>
                <p>Filed on: {fir.filed_at.strftime('%d-%m-%Y %H:%M') if fir.filed_at else 'Not submitted'}</p>
            </div>

            <div class="section">
                <div class="section-title">COMPLAINANT DETAILS:</div>
                <p>Name: {user.full_name}</p>
                <p>Contact: {user.phone or 'Not provided'}</p>
                <p>Address: {user.address or 'Not provided'}</p>
            </div>

            <div class="section">
                <div class="section-title">INCIDENT DETAILS:</div>
                <p>Date & Time: {fir.incident_date.strftime('%d-%m-%Y %H:%M') if fir.incident_date else 'Not specified'}</p>
                <p>Location: {fir.incident_location or 'Not specified'}</p>
                <p>Description: {fir.incident_description}</p>
                <p>Status: {fir.get_status_label()}</p>
                <p>Urgency: {fir.get_urgency_label()}</p>
            </div>

            <div class="section">
                <div class="section-title">APPLICABLE LEGAL SECTIONS:</div>
                <table>
                    <tr>
                        <th>Section</th>
                        <th>Description</th>
                    </tr>
        """

        # Add legal sections to the HTML
        for section in legal_sections:
            html_content += f"""
                    <tr>
                        <td>{section.code}</td>
                        <td>{section.name} - {section.description}</td>
                    </tr>
            """

        html_content += """
                </table>
            </div>

            <div class="footer">
                <p>This is an officially generated FIR document from the Intelligent FIR Filing System.</p>
            </div>
        </body>
        </html>
        """

        # Generate a unique filename
        filename = f"fir_{fir.fir_number}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.pdf"
        pdf_path = os.path.join(pdf_dir, filename)

        # Generate PDF from HTML
        pdfkit.from_string(html_content, pdf_path)

        return pdf_path
    except Exception as e:
        logger.error(f"Failed to generate simple PDF: {str(e)}", exc_info=True)
        raise Exception(f"Failed to generate PDF: {e}")

def generate_and_store_fir_pdf(fir_id):
    """
    Generate a PDF for an FIR and store the path in the database.
    This function is called when an FIR is submitted.

    Args:
        fir_id: The ID of the FIR to generate a PDF for

    Returns:
        str: The path to the generated PDF file, or None if generation failed
    """
    from models import db, FIR, User, Evidence

    try:
        # Get the FIR and related data
        fir = FIR.query.get(fir_id)
        if not fir:
            logger.error(f"FIR with ID {fir_id} not found")
            return None

        # Get the user who filed the complaint
        user = User.query.get(fir.complainant_id)
        if not user:
            logger.error(f"User with ID {fir.complainant_id} not found")
            return None

        # Parse legal sections from JSON if available
        legal_sections = []
        if fir.legal_sections:
            try:
                legal_sections_data = json.loads(fir.legal_sections)
                # Convert to objects with the expected attributes for the PDF generator
                for section_data in legal_sections_data:
                    # Create a dynamic object with the required attributes
                    section_obj = type('LegalSection', (), {
                        'code': section_data.get('section_code', section_data.get('code', 'Unknown')),
                        'name': section_data.get('section_name', section_data.get('name', 'Unknown')),
                        'description': section_data.get('section_description', section_data.get('description', ''))
                    })()
                    legal_sections.append(section_obj)
            except Exception as json_error:
                logger.error(f"Error parsing legal sections JSON: {str(json_error)}")

        # Get evidence items
        evidence = Evidence.query.filter_by(fir_id=fir.id).all()

        # Try to generate the enhanced PDF first
        pdf_path = None
        try:
            pdf_path = generate_fir_pdf(fir, user, legal_sections, evidence)
            logger.info(f"Generated enhanced PDF for FIR {fir.fir_number}: {pdf_path}")
        except Exception as pdf_error:
            logger.warning(f"Enhanced PDF generation failed, falling back to simple version: {str(pdf_error)}")
            try:
                # If enhanced PDF generation fails, fall back to simple version
                pdf_path = generate_fir_pdf_simple(fir, user, legal_sections)
                logger.info(f"Generated simple PDF for FIR {fir.fir_number}: {pdf_path}")
            except Exception as simple_pdf_error:
                logger.error(f"Simple PDF generation also failed: {str(simple_pdf_error)}")
                return None

        # Store the PDF path in the database
        if pdf_path:
            try:
                fir.pdf_path = pdf_path
                db.session.commit()
                logger.info(f"Stored PDF path in database for FIR {fir.fir_number}")
                return pdf_path
            except Exception as db_error:
                logger.error(f"Error storing PDF path in database: {str(db_error)}")
                return pdf_path  # Still return the path even if we couldn't store it

        return None
    except Exception as e:
        logger.error(f"Error in generate_and_store_fir_pdf: {str(e)}", exc_info=True)
        return None
