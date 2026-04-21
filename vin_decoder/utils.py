import io
import logging

from xhtml2pdf import pisa

#create logger
logger = logging.getLogger(__name__)


def generate_car_raport_pdf(html_content):
    """Take generated raport in memory and save it as pdf using xhtml2pdf"""

    pisa.showLogging()

    output = io.BytesIO()

#  create pdf in memory
    pisa_status = pisa.CreatePDF(
        html_content,
        dest= output,
        encoding='utf-8'
    )

    if pisa_status.err:
        logger.error(f"Error saving PDF: {pisa_status.err}")

    # set cursor in memory at the beggining
    output.seek(0)

    # return file with according name, file extension (forces download in web browser) 
    return output