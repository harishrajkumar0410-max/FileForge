import fitz
from pypdf import PdfWriter
from flask import (
    Flask,
    render_template,
    request,
    send_file,
    redirect,
    url_for,
    session
)
#from docx2pdf import convert
from pdf2docx import Converter
import img2pdf
import os
import uuid

app = Flask(__name__)
app.secret_key = "fileforge_secret_key"


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------- PDF ----------------
@app.route("/pdf")
def pdf():
    return render_template("pdf.html")


# ---------------- IMAGE ----------------
@app.route("/image")
def image():
    return render_template("image.html")


# ---------------- VIDEO ----------------
@app.route("/video")
def video():
    return render_template("video.html")


# ---------------- AUDIO ----------------
@app.route("/audio")
def audio():
    return render_template("audio.html")


# ---------------- AI ----------------
@app.route("/ai")
def ai():
    return render_template("ai.html")


# ---------------- PREMIUM ----------------
@app.route("/premium")
def premium():
    return render_template("premium.html")

@app.route("/image-to-pdf")
def image_to_pdf():
    return render_template("image_to_pdf.html")

@app.route("/convert-image-to-pdf", methods=["POST"])
def convert_image_to_pdf():

    images = request.files.getlist("images")

    if not images:
        return "No images selected."

    image_paths = []

    os.makedirs("uploads", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    for image in images:

        filepath = os.path.join("uploads", image.filename)
        image.save(filepath)
        image_paths.append(filepath)

    filename = f"FileForge_{uuid.uuid4().hex}.pdf"

    output_pdf = os.path.join("outputs", filename)

    with open(output_pdf, "wb") as f:
        f.write(img2pdf.convert(image_paths))

    session["output_file"] = filename

    return redirect(url_for("result"))

@app.route("/result")
def result():

    filename = session.get("output_file")

    return render_template(
        "result.html",
        filename=filename,
        original_size=session.get("original_size"),
        compressed_size=session.get("compressed_size"),
        saved_percent=session.get("saved_percent")
    )


@app.route("/download-file")
def download_file():

    filename = session.get("output_file")

    if not filename:
        return redirect(url_for("home"))

    filepath = os.path.join("outputs", filename)

    response = send_file(
        filepath,
        as_attachment=True,
        download_name=filename
    )

    # Delete uploaded files
    if os.path.exists("uploads"):
        for file in os.listdir("uploads"):
            try:
                os.remove(os.path.join("uploads", file))
            except:
                pass

    # Delete generated output
    try:
        os.remove(filepath)
    except:
        pass

    session.pop("output_file", None)

    # Remove compression stats if they exist
    session.pop("original_size", None)
    session.pop("compressed_size", None)
    session.pop("saved_percent", None)

    return response

@app.route("/merge-pdf-page")
def merge_pdf_page():
    return render_template("merge_pdf.html")

@app.route("/merge-pdf", methods=["POST"])
def merge_pdf():

    pdfs = request.files.getlist("pdfs")

    if not pdfs:
        return "No PDF files selected."

    os.makedirs("uploads", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    merger = PdfWriter()

    filename = f"FileForge_Merged_{uuid.uuid4().hex}.pdf"
    output_pdf = os.path.join("outputs", filename)

    for pdf in pdfs:

        filepath = os.path.join("uploads", pdf.filename)

        pdf.save(filepath)

        merger.append(filepath)

    merger.write(output_pdf)
    merger.close()

    session["output_file"] = filename

    return redirect(url_for("result"))

@app.route("/split-pdf-page")
def split_pdf_page():
    return render_template("split_pdf.html")

from pypdf import PdfReader, PdfWriter

@app.route("/split-pdf", methods=["POST"])
def split_pdf():

    pdf = request.files["pdf"]

    if pdf.filename == "":
        return "No PDF selected."

    os.makedirs("uploads", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    filepath = os.path.join("uploads", pdf.filename)
    pdf.save(filepath)

    reader = PdfReader(filepath)
    writer = PdfWriter()

    pages_input = request.form["pages"]

    try:

        parts = pages_input.split(",")

        for part in parts:

            part = part.strip()

            # Range (Example: 1-3)
            if "-" in part:

                start, end = map(int, part.split("-"))

                if start < 1 or end > len(reader.pages) or start > end:
                    return "Invalid page range."

                for page in range(start - 1, end):
                    writer.add_page(reader.pages[page])

            # Single page (Example: 5)
            else:

                page = int(part)

                if page < 1 or page > len(reader.pages):
                    return "Invalid page number."

                writer.add_page(reader.pages[page - 1])

    except:
        return "Please enter pages like 1-3,5,7-9"

    filename = f"FileForge_Split_{uuid.uuid4().hex}.pdf"
    output_pdf = os.path.join("outputs", filename)

    with open(output_pdf, "wb") as f:
        writer.write(f)

    session["output_file"] = filename

    return redirect(url_for("result"))

@app.route("/compress-pdf-page")
def compress_pdf_page():
    return render_template("compress_pdf.html")

@app.route("/compress-pdf", methods=["POST"])
def compress_pdf():

    pdf = request.files["pdf"]

    if pdf.filename == "":
        return "No PDF selected."

    os.makedirs("uploads", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    input_path = os.path.join("uploads", pdf.filename)
    pdf.save(input_path)

    filename = f"FileForge_Compressed_{uuid.uuid4().hex}.pdf"
    output_path = os.path.join("outputs", filename)

    doc = fitz.open(input_path)

    quality = request.form["quality"]

    if quality == "low":
        garbage = 2
        deflate = True

    elif quality == "medium":
        garbage = 3
        deflate = True

    else:
        garbage = 4
        deflate = True

    doc.save(
        output_path,
        garbage=garbage,
        deflate=deflate,
        clean=True
    )

    doc.close()

    original_size = os.path.getsize(input_path)
    compressed_size = os.path.getsize(output_path)

    saved = original_size - compressed_size
    saved_percent = (saved / original_size) * 100

    session["original_size"] = round(original_size / (1024 * 1024), 2)
    session["compressed_size"] = round(compressed_size / (1024 * 1024), 2)
    session["saved_percent"] = round(saved_percent, 1)

    session["output_file"] = filename

    return redirect(url_for("result"))

@app.route("/pdf-to-word-page")
def pdf_to_word_page():
    return render_template("pdf_to_word.html")

@app.route("/pdf-to-word", methods=["POST"])
def pdf_to_word():

    pdf = request.files["pdf"]

    if pdf.filename == "":
        return "No PDF selected."

    os.makedirs("uploads", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    input_path = os.path.join("uploads", pdf.filename)
    pdf.save(input_path)

    filename = f"FileForge_{uuid.uuid4().hex}.docx"
    output_path = os.path.join("outputs", filename)

    cv = Converter(input_path)
    cv.convert(output_path)
    cv.close()

    session["output_file"] = filename

    return redirect(url_for("result"))

@app.route("/word-to-pdf-page")
def word_to_pdf_page():
    return render_template("word_to_pdf.html")

@app.route("/word-to-pdf", methods=["POST"])
def word_to_pdf():

    word = request.files["word"]

    if word.filename == "":
        return "No Word document selected."

    os.makedirs("uploads", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    input_path = os.path.join("uploads", word.filename)
    word.save(input_path)

    filename = f"FileForge_{uuid.uuid4().hex}.pdf"
    output_path = os.path.join("outputs", filename)

    convert(input_path, output_path)

    session["output_file"] = filename

    return redirect(url_for("result"))

@app.route("/coming-soon")
def coming_soon():
    return render_template("coming_soon.html")



if __name__ == "__main__":
    app.run(debug=True)