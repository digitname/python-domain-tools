import openpyxl
import csv
import io
from .models import Domain

def generate_excel(domains):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Domains"
    sheet.append(["Domain", "Category"])
    for domain in domains:
        sheet.append([domain.name, domain.category])
    
    output = io.BytesIO()
    workbook.save(output)
    output.seek(0)
    return output

def generate_csv(domains):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Domain", "Category"])
    for domain in domains:
        writer.writerow([domain.name, domain.category])
    return output.getvalue()
