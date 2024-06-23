import fpdf
import tempfile

def download_summary(summary):
    pdf = fpdf.FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, summary)
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf_file_path = temp_file.name
    pdf.output(pdf_file_path)
    temp_file.close()
    
    return pdf_file_path

