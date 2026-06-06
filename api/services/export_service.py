import csv
import io

from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


class ExportService:
    @staticmethod
    def csv_bytes(rows):
        output = io.StringIO()
        columns = list(rows[0].keys()) if rows else []
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
        return output.getvalue().encode("utf-8")

    @staticmethod
    def xlsx_bytes(rows):
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Analytics"
        columns = list(rows[0].keys()) if rows else []
        sheet.append(columns)
        for row in rows:
            sheet.append([row.get(column) for column in columns])
        output = io.BytesIO()
        workbook.save(output)
        return output.getvalue()

    @staticmethod
    def pdf_bytes(title, sections):
        output = io.BytesIO()
        document = canvas.Canvas(output, pagesize=A4)
        width, height = A4
        document.setTitle(title)
        document.setFont("Helvetica-Bold", 18)
        document.drawString(48, height - 52, title)
        y = height - 86
        document.setFont("Helvetica", 10)
        for label, value in sections:
            if y < 60:
                document.showPage()
                y = height - 52
            document.setFont("Helvetica-Bold", 10)
            document.drawString(48, y, str(label))
            document.setFont("Helvetica", 10)
            document.drawString(210, y, str(value)[:90])
            y -= 18
        document.save()
        return output.getvalue()
