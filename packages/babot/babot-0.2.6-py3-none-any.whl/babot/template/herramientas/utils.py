from pypdf import PdfReader

def leer_pdf(ruta_archivo):
    """Lee un archivo PDF y devuelve su contenido como texto."""
    try:
        reader = PdfReader(ruta_archivo)
        texto = ""
        for pagina in reader.pages:
            texto += pagina.extract_text() or ""
        return texto
    except Exception as e:
        return f"Error al leer el PDF: {e}"
