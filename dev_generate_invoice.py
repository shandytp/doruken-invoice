from weasyprint import HTML, CSS
from jinja2 import Template
from src.utils.helper import generate_json_invoice
import os


context_data = generate_json_invoice(nama = "test tepe")

invoice_number = context_data.get("invoiceNumber")
first_name = context_data["client"].get("firstName")

OUTPUT_FILENAME = f"tmp/invoice-harris-{invoice_number}-{first_name}"

TEMPLATE_HTML_PATH = "template/invoice_template_001.html"

TEMPLATE_CSS = [
    CSS("static/invoice_template_001.css"),
    CSS("https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css"),
    CSS("https://maxcdn.bootstrapcdn.com/font-awesome/4.3.0/css/font-awesome.min.css")
]


def render_template(template_file: str, context: dict, styles: list, output_filename: str) -> str:
    """
    Render a Jinja template to PDF using WeasyPrint.
    """
    # Load and render the Jinja template with the provided context
    template = Template(template_file)
    rendered_html = template.render(context)

    # Save rendered HTML to a file
    html_file = f"{output_filename}.html"
    pdf_file = f"{output_filename}.pdf"

    with open(html_file, 'w') as file:
        file.write(rendered_html)

    # Convert HTML to PDF using WeasyPrint with the provided stylesheets
    HTML(html_file).write_pdf(pdf_file, stylesheets=styles)
    
    # os.remove(html_file)

    return pdf_file


# Load Jinja template content
with open(TEMPLATE_HTML_PATH) as template:
    template_html = template.read()

# Render the template and generate the PDF
pdf_filename = render_template(template_html, context_data, TEMPLATE_CSS, OUTPUT_FILENAME)
print(f"PDF generated: {pdf_filename}")
