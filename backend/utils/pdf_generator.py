from flask import render_template, current_app
import pdfkit
import os
import base64
from datetime import datetime, timezone
import logging
import json
from utils.qr_generator import generate_verification_qr, generate_document_id
from models import LegalSection, Evidence, User

# Try to import reportlab for alternative PDF generation
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

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
        pdf_dir = r'K:\IntelligentFirSystem\Intelligent-FIR\static\pdfs'
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
        try:
            pdfkit.from_string(html_content, pdf_path, options=options)
        except OSError as e:
            if "wkhtmltopdf" in str(e):
                # Fallback to alternative PDF generation
                logger.warning("wkhtmltopdf not found, using alternative PDF generation")
                return generate_pdf_alternative(fir, user, legal_sections, evidence_items)
            else:
                raise

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
        pdf_dir = r'K:\IntelligentFirSystem\Intelligent-FIR\static\pdfs'
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
        try:
            pdfkit.from_string(html_content, pdf_path)
        except OSError as e:
            if "wkhtmltopdf" in str(e):
                # Fallback to alternative PDF generation
                logger.warning("wkhtmltopdf not found, using alternative simple PDF generation")
                return generate_simple_pdf_alternative(fir, user, legal_sections)
            else:
                raise

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

def generate_simple_pdf_alternative(fir, user, legal_sections):
    """
    Generate a PDF using reportlab when wkhtmltopdf is not available
    """
    try:
        if not REPORTLAB_AVAILABLE:
            # Fallback to text file if reportlab is not available
            return generate_text_fallback(fir, user, legal_sections)

        # Create directory to store PDFs if it doesn't exist
        pdf_dir = r'K:\IntelligentFirSystem\Intelligent-FIR\static\pdfs'
        os.makedirs(pdf_dir, exist_ok=True)

        # Generate a unique filename
        filename = f"fir_{fir.fir_number}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.pdf"
        pdf_path = os.path.join(pdf_dir, filename)

        # Create PDF document
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph("FIRST INFORMATION REPORT", title_style))
        story.append(Spacer(1, 12))

        # FIR Number
        story.append(Paragraph(f"<b>FIR Number:</b> {fir.fir_number}", styles['Normal']))
        story.append(Paragraph(f"<b>Filed on:</b> {fir.filed_at.strftime('%d-%m-%Y %H:%M') if fir.filed_at else 'Not submitted'}", styles['Normal']))
        story.append(Spacer(1, 12))

        # Complainant Details
        story.append(Paragraph("<b>COMPLAINANT DETAILS</b>", styles['Heading2']))
        story.append(Paragraph(f"<b>Name:</b> {user.full_name}", styles['Normal']))
        story.append(Paragraph(f"<b>Contact:</b> {user.phone or 'Not provided'}", styles['Normal']))
        story.append(Paragraph(f"<b>Address:</b> {user.address or 'Not provided'}", styles['Normal']))
        story.append(Spacer(1, 12))

        # Incident Details
        story.append(Paragraph("<b>INCIDENT DETAILS</b>", styles['Heading2']))
        story.append(Paragraph(f"<b>Date & Time:</b> {fir.incident_date.strftime('%d-%m-%Y %H:%M') if fir.incident_date else 'Not specified'}", styles['Normal']))
        story.append(Paragraph(f"<b>Location:</b> {fir.incident_location or 'Not specified'}", styles['Normal']))
        story.append(Paragraph(f"<b>Status:</b> {fir.get_status_label()}", styles['Normal']))
        story.append(Paragraph(f"<b>Urgency:</b> {fir.get_urgency_label()}", styles['Normal']))
        story.append(Spacer(1, 12))

        # Description - Dynamic sizing based on content length
        story.append(Paragraph("<b>DESCRIPTION:</b>", styles['Heading3']))

        description_text = fir.incident_description or 'No description provided'

        # Create a custom style for description that handles long text better
        description_style = ParagraphStyle(
            'DescriptionStyle',
            parent=styles['Normal'],
            fontSize=10,
            leading=12,
            spaceAfter=6,
            alignment=0,  # Left alignment
            leftIndent=0,
            rightIndent=0,
            wordWrap='LTR'
        )

        # Split long descriptions into multiple paragraphs for better readability
        if len(description_text) > 500:
            # For very long descriptions, break into smaller chunks
            words = description_text.split()
            chunks = []
            current_chunk = []
            current_length = 0

            for word in words:
                if current_length + len(word) > 400:  # ~400 chars per chunk
                    if current_chunk:
                        chunks.append(' '.join(current_chunk))
                        current_chunk = [word]
                        current_length = len(word)
                else:
                    current_chunk.append(word)
                    current_length += len(word) + 1  # +1 for space

            if current_chunk:
                chunks.append(' '.join(current_chunk))

            # Add each chunk as a separate paragraph
            for i, chunk in enumerate(chunks):
                story.append(Paragraph(chunk, description_style))
                if i < len(chunks) - 1:  # Add small space between chunks except after last
                    story.append(Spacer(1, 6))
        else:
            # For shorter descriptions, use single paragraph
            story.append(Paragraph(description_text, description_style))

        story.append(Spacer(1, 12))

        # Legal Sections - Dynamic table sizing
        if legal_sections:
            story.append(Paragraph("<b>APPLICABLE LEGAL SECTIONS</b>", styles['Heading2']))

            # Create table data for legal sections with dynamic description handling
            table_data = [['Section Code', 'Section Name', 'Description']]

            for section in legal_sections:
                # Handle long descriptions by wrapping them in Paragraph objects
                description_text = section.description

                # Create a paragraph for the description to handle text wrapping
                desc_style = ParagraphStyle(
                    'TableDescStyle',
                    parent=styles['Normal'],
                    fontSize=8,
                    leading=10,
                    leftIndent=2,
                    rightIndent=2,
                    spaceAfter=2
                )

                # Wrap description in Paragraph for better text handling
                if len(description_text) > 150:
                    # For very long descriptions, truncate but keep it readable
                    truncated_desc = description_text[:150] + "..."
                    desc_paragraph = Paragraph(truncated_desc, desc_style)
                else:
                    desc_paragraph = Paragraph(description_text, desc_style)

                table_data.append([
                    Paragraph(section.code, desc_style),
                    Paragraph(section.name, desc_style),
                    desc_paragraph
                ])

            # Create table with dynamic column widths
            # Adjust column widths based on content
            available_width = 6.5 * inch  # Total available width
            col_widths = [1.2*inch, 1.8*inch, 3.5*inch]  # Code, Name, Description

            table = Table(table_data, colWidths=col_widths, repeatRows=1)
            table.setStyle(TableStyle([
                # Header styling
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 8),

                # Data rows styling
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),

                # Alignment and borders
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),

                # Alternating row colors for better readability
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.lightgrey]),
            ]))

            story.append(table)
            story.append(Spacer(1, 12))

        # Footer
        story.append(Spacer(1, 24))
        story.append(Paragraph("This is an officially generated FIR document from the Intelligent FIR Filing System.", styles['Normal']))
        story.append(Paragraph(f"Generated on: {datetime.now(timezone.utc).strftime('%d-%m-%Y %H:%M:%S')}", styles['Normal']))

        # Build PDF
        doc.build(story)

        logger.info(f"Generated PDF using reportlab: {pdf_path}")
        return pdf_path

    except Exception as e:
        logger.error(f"Failed to generate PDF with reportlab: {str(e)}", exc_info=True)
        # Fallback to text file
        return generate_text_fallback(fir, user, legal_sections)

def generate_text_fallback(fir, user, legal_sections):
    """
    Generate a simple text file as final fallback
    """
    try:
        # Create directory to store PDFs if it doesn't exist
        pdf_dir = r'K:\IntelligentFirSystem\Intelligent-FIR\static\pdfs'
        os.makedirs(pdf_dir, exist_ok=True)

        # Generate a unique filename
        filename = f"fir_{fir.fir_number}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.txt"
        txt_path = os.path.join(pdf_dir, filename)

        # Create text content
        content = f"""
FIRST INFORMATION REPORT
========================

FIR Number: {fir.fir_number}
Filed on: {fir.filed_at.strftime('%d-%m-%Y %H:%M') if fir.filed_at else 'Not submitted'}

COMPLAINANT DETAILS:
-------------------
Name: {user.full_name}
Contact: {user.phone or 'Not provided'}
Address: {user.address or 'Not provided'}

INCIDENT DETAILS:
----------------
Date & Time: {fir.incident_date.strftime('%d-%m-%Y %H:%M') if fir.incident_date else 'Not specified'}
Location: {fir.incident_location or 'Not specified'}
Description: {fir.incident_description}
Status: {fir.get_status_label()}
Urgency: {fir.get_urgency_label()}

APPLICABLE LEGAL SECTIONS:
-------------------------
"""

        for section in legal_sections:
            content += f"- {section.code}: {section.name} - {section.description}\n"

        content += f"""

This is an officially generated FIR document from the Intelligent FIR Filing System.
Generated on: {datetime.now(timezone.utc).strftime('%d-%m-%Y %H:%M:%S')}
"""

        # Write to text file
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Generated text-based FIR document: {txt_path}")
        return txt_path

    except Exception as e:
        logger.error(f"Failed to generate text fallback: {str(e)}", exc_info=True)
        raise Exception(f"Failed to generate document: {e}")

def generate_pdf_alternative(fir, user, legal_sections, evidence_items):
    """
    Alternative PDF generation method (same as simple for now)
    """
    return generate_simple_pdf_alternative(fir, user, legal_sections)
