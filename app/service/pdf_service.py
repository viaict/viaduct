from app.service import user_service
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from io import BytesIO
import os

TEMPLATE_PATH = "app/templates/athenaeum/discountcard_template.pdf"


def user_discount_card(user_id):

    user = user_service.find_by_id(user_id)

    # Create a new PDF with Reportlab
    memberdetails_buffer = BytesIO()
    can = canvas.Canvas(memberdetails_buffer)

    # Draw the name
    can.setFont('Helvetica', 15)
    name = user.first_name + " " + user.last_name
    can.drawString(45, 620, name)

    # Draw the student id
    can.setFont('Helvetica', 10)
    can.drawString(45, 560, str(user.student_id))

    # Draw the emailaddress
    can.setFont('Helvetica', 10)
    can.drawString(45, 535, user.email)
    can.save()

    # Read both the empty template PDF and the filled in details
    memberdetails_pdf = PdfFileReader(memberdetails_buffer)
    template_filename = os.path.join(os.getcwd(), TEMPLATE_PATH)
    template_pdf = PdfFileReader(template_filename)

    output = PdfFileWriter()

    # Merge the first page of both PDFs
    page = template_pdf.getPage(0)
    page.mergePage(memberdetails_pdf.getPage(0))
    output.addPage(page)

    output_buffer = BytesIO()

    output.write(output_buffer)

    return output_buffer.getvalue()
