import os
import sys
import logging
from datetime import date
import yagmail
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# === Setup Logging ===
# Good logging setup, no changes needed here.
logging.basicConfig(
    level=logging.INFO, # Changed to INFO to give more feedback during normal operation
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("Program.log", mode="a", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Suppress noisy third-party logs
logging.getLogger("yagmail").setLevel(logging.ERROR)
logging.getLogger("reportlab").setLevel(logging.ERROR)


def create_pdf(successful: list, failed: list, summary_text: str) -> str:
    """Generates a PDF summary of successful and failed orders."""
    
    # --- IMPROVEMENT: Define file path upfront for robustness ---
    # Create the PDF in the same directory as the script.
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    today = date.today()
    pdf_name = f"Order summary ({today}).pdf"
    pdf_path = os.path.join(script_dir, pdf_name)
    
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # === 1. Draw logo in top-left ===
    try:
        # --- IMPROVEMENT: Use a relative path for portability ---
        # Assumes 'Newport-Logo.png' is in the same folder as the script.
        image_path = os.path.join(script_dir, "Newport-Logo.png")
        image_width = 1.5 * inch
        image_height = 1.0 * inch
        c.drawImage(image_path, x=30, y=height - image_height - 30,
                    width=image_width, height=image_height, preserveAspectRatio=True)
    except FileNotFoundError:
        logging.warning("Logo image 'Newport-Logo.png' not found in script directory. Skipping logo.")

    # === 2. Draw title centered near top ===
    title_text = f"Order summary {today}"
    c.setFont("Helvetica-Bold", 20)
    text_width = c.stringWidth(title_text, "Helvetica-Bold", 20)
    center_x = (width - text_width) / 2
    title_y = height - 50
    c.drawString(center_x, title_y, title_text)

    # === 3. Draw summary text below title ===
    c.setFont("Helvetica", 11)
    max_width = width - 60
    summary_y = title_y - 45
    styles = getSampleStyleSheet()
    p = Paragraph(summary_text, styles["Normal"])
    p_width, p_height = p.wrap(max_width, height)
    p.drawOn(c, 30, summary_y - p_height)

    # === 4. Prepare tables ===
    # The data is structured as (Name, PIP, Quantity, Status).
    # The table headers are ["PIP code", "Name", ...].
    # The list comprehension correctly reorders the columns to match the headers.
    headers = ["PIP code", "Name", "Quantity", "Status"]
    success_data = [headers] + [[pip, name, qty, status] for name, pip, qty, status in successful]
    failed_data = [headers] + [[pip, name, qty, status] for name, pip, qty, status in failed]
    col_widths = [80, 250, 60, 100]

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('WORDWRAP', (1, 1), (1, -1), 'CJK'), # Apply word wrap only to 'Name' column
    ])
    
    # Starting Y position for the first table
    y_position = summary_y - p_height - 30

    # === 5. Draw Failed Orders Table ===
    c.setFont("Helvetica-Bold", 13)
    c.drawString(30, y_position, "Failed Orders")
    y_position -= 25

    if len(failed_data) > 1:
        failed_table = Table(failed_data, colWidths=col_widths)
        failed_table.setStyle(style)
        table_width, table_height = failed_table.wrapOn(c, width - 60, height)
        y_position -= table_height
        failed_table.drawOn(c, 30, y_position)
    else:
        c.setFont("Helvetica", 11)
        c.drawString(30, y_position - 15, "No failed orders.")
        y_position -= 30

    # === 6. Draw Successful Orders Table ===
    y_position -= 30
    c.setFont("Helvetica-Bold", 13)
    c.drawString(30, y_position, "Successful Orders")
    y_position -= 25

    if len(success_data) > 1:
        success_table = Table(success_data, colWidths=col_widths)
        success_table.setStyle(style)
        table_width, table_height = success_table.wrapOn(c, width - 60, height)
        y_position -= table_height
        success_table.drawOn(c, 30, y_position)
    else:
        c.setFont("Helvetica", 11)
        c.drawString(30, y_position - 15, "No successful orders.")

    # === 7. Save PDF and return path ===
    c.save()
    logging.info("Successfully created PDF: %s", pdf_path)
    return pdf_path


def email_results(path: str, recipient: str) -> bool:
    # --- Hardcoded credentials (⚠️ less secure) ---
    email_user = "maxbot202@gmail.com"
    email_password = "qgty jfpx lgyl gppq"  # App password

    subject = f"Fullspeed Order Summary - {date.today()}"
    contents = (
        "Dear Team,\n\n"
        "Please find attached the Fullspeed order summary for today. "
        "This includes the list of successful and failed orders.\n\n"
        "Best regards,\n"
        "Maxbot"
    )

    try:
        yag = yagmail.SMTP(email_user, email_password)
        yag.send(
            to=recipient,
            subject=subject,
            contents=[contents],
            attachments=[path]
        )
        logging.warning("✅ Email sent successfully to %s", recipient)
        return True

    except Exception as e:
        logging.error("❌ Failed to send email to %s. Error: %s", recipient, e, exc_info=True)
        return False

# === Optional: Run as script ===
if __name__ == "__main__":
    # Dummy example data for testing
    successful_orders = [
        ("Paracetamol 500mg Tablets", "123456", 10, "Success"),
        ("Ibuprofen 200mg Tablets", "654321", 5, "Success")
    ]
    failed_orders = [
        ("Amoxicillin 250mg Capsules", "111222", 0, "Out of stock")
    ]
    summary_text = (
        "Today’s automated ordering has completed. Below is a summary of all successful and failed product requests. "
        "Please review any failed orders and process them manually if required."
    )

    recipient_email = "new.port@nhs.net"  # <-- Update this address

    pdf_file = create_pdf(successful_orders, failed_orders, summary_text)
    
    if pdf_file:
        email_sent = email_results(pdf_file, recipient_email)
        if email_sent:
            print("Process completed successfully. PDF generated and email sent.")
        else:
            print("Process failed: Could not send the email.")