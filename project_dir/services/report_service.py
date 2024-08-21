from dotenv import load_dotenv
import os
import logging
import tempfile
import pandas as pd
import io
import aiofiles
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from PIL import Image

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Email configuration
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'aimlprojectsgroup6@gmail.com')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD', 'aimlgroup6')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL', 'nuvofamilynigeria@gmail.com')

async def send_emergency_email(predicted_class, confidence, image_path):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = f"Emergency Alert: {predicted_class} Detected"
        body = f"An emergency has been detected:\nPredicted Class: {predicted_class}\nConfidence: {confidence:.2f}"
        msg.attach(MIMEText(body, 'plain'))
        
        async with aiofiles.open(image_path, 'rb') as f:
            img_data = await f.read()
        image = MIMEImage(img_data, name=os.path.basename(image_path))
        msg.attach(image)
        
        # Use Gmail's SMTP server
        await aiosmtplib.send(
            msg,
            hostname="smtp.gmail.com",
            port=587,
            use_tls=True,
            username=SENDER_EMAIL,
            password=SENDER_PASSWORD
        )
        logger.info(f"Emergency email sent to {RECIPIENT_EMAIL}")
    except Exception as e:
        logger.error(f"Failed to send emergency email: {e}")

async def generate_report(predicted_class, confidence, image, image_name="image.png"):
    """Generate and return a downloadable report as an Excel file with classification details."""
    report = f"""Burn Classification Report
Predicted Class: {predicted_class}
Confidence: {confidence:.2f}
Description: {await get_burn_description(predicted_class)}
Treatment Plan: {await get_treatment_plan(predicted_class)}
Disclaimer: This report is for educational purposes only. Always consult a medical professional for burn treatment."""
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
        image.save(tmp_file.name, format='PNG')
        tmp_file_path = tmp_file.name

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df = pd.DataFrame({'Report': [report]})
        df.to_excel(writer, sheet_name='Report', index=False)
        worksheet = writer.sheets['Report']
        worksheet.insert_image('B1', tmp_file_path, {'x_offset': 10, 'y_offset': 10, 'x_scale': 0.3, 'y_scale': 0.3})

    # Optionally send an emergency email
    await send_emergency_email(predicted_class, confidence, tmp_file_path)

    return excel_buffer.getvalue()

async def get_burn_description(burn_degree):
    descriptions = {
        '1st degree burn': "First-degree burns affect only the outer layer of skin (epidermis). The burn site is red, painful, dry, and with no blisters. Mild sunburn is an example.",
        '2nd degree burn': "Second-degree burns involve the epidermis and part of the lower layer of skin (dermis). The burn site appears red, blistered, and may be swollen and painful.",
        '3rd degree burn': "Third-degree burns destroy the epidermis and dermis. They may go into the innermost layer of skin (subcutaneous tissue). The burn area may look white or charred."
    }
    return descriptions.get(burn_degree, "Unknown burn degree")

async def get_treatment_plan(burn_degree):
    treatments = {
        '1st degree burn': "Cool the burn, apply aloe vera, take OTC pain reliever if needed, protect with sunscreen.",
        '2nd degree burn': "Cool the burn, don't break blisters, apply antibiotic ointment, cover with sterile bandage, seek medical attention if large or on sensitive area.",
        '3rd degree burn': "Call emergency services immediately, do not remove stuck clothing, cover with cool moist sterile bandage, elevate burned area if possible."
    }
    return treatments.get(burn_degree, "Unknown burn degree. Please consult a medical professional.")
