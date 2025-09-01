"""
QR Code Generator for FIR verification
"""

import os
import qrcode
import base64
from io import BytesIO
from datetime import datetime, timezone

def generate_verification_qr(fir_number, document_id, base_url=None):
    """
    Generate a QR code for FIR verification

    Args:
        fir_number: The FIR number
        document_id: The document ID
        base_url: The base URL for verification (optional)

    Returns:
        str: Base64 encoded QR code image
    """
    try:
        # Create verification URL
        if base_url:
            verification_url = f"{base_url}/verify/{fir_number}/{document_id}"
        else:
            verification_url = f"fir-verification:{fir_number}:{document_id}"

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(verification_url)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        print(f"Error generating QR code: {e}")
        return None

def generate_document_id(fir_number):
    """
    Generate a unique document ID for the FIR

    Args:
        fir_number: The FIR number

    Returns:
        str: Document ID
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"DOC-{fir_number}-{timestamp}"
