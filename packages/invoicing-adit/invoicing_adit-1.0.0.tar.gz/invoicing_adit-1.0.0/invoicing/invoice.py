import os
import pandas as pd
import glob as gb
from fpdf import FPDF
from pathlib import Path


def generate(invoices_path, pdfs_path, sheet_name, image_path, company_name,
             product_id, product_name, amount_purchased,
             price_per_unit, total_price, currency, orientation="P", format_of_page="A4"):
    """
    This function converts Invoice Excell files into PDF invoices.


    :param invoices_path:
    :param pdfs_path:
    :param sheet_name:
    :param image_path:
    :param product_id:
    :param product_name:
    :param amount_purchased:
    :param price_per_unit:
    :param total_price:
    :param currency:
    :param company_name:
    :param orientation:
    :param format_of_page:
    :return:
    """
    filepaths = gb.glob(f"{invoices_path}/*.xlsx")

    for filepath in filepaths:
        pdf = FPDF(orientation=orientation,unit="mm", format=format_of_page)
        pdf.set_auto_page_break(auto=False, margin=0)
        pdf.add_page()
        filename = Path(filepath).stem
        Invoice_no, Date = filename.split("-")

        pdf.set_font(family="Times", style="BI", size=18)
        pdf.cell(w=50, h=8, txt=f"Invoice no: {Invoice_no}", ln=12)

        pdf.set_font(family="Times", style="B", size=10)
        pdf.set_text_color(0,0,0)

        # Current date and time {time.strftime('%d.%m.%Y')}
        pdf.cell(w=50, h=8, txt=f"Date: {Date}", ln=15)
        pdf.ln(10)

        df = pd.read_excel(filepath, sheet_name=sheet_name)

        #Add a header
        raw_co = df.columns
        columns = [item.replace('_', ' ').title() for item in raw_co]

        pdf.set_font(family="Times",style='B', size=10)
        pdf.set_text_color(10, 10, 10)

        pdf.cell(w=30, h=8, txt=columns[0], border=1)
        pdf.cell(w=70, h=8, txt=columns[1], border=1)
        pdf.cell(w=35, h=8, txt=columns[2], border=1)
        pdf.cell(w=30, h=8, txt=columns[3], border=1)
        pdf.cell(w=30, h=8, txt=columns[4], border=1, ln=1)


        total_sum = df["total_price"].sum()


        #Added content
        for index, row in df.iterrows():

            pdf.set_font(family="Times", size=10)
            pdf.set_text_color(10, 10, 10)

            pdf.cell(w=30, h=8, txt=str(row[product_id]), border=1)
            pdf.cell(w=70, h=8, txt=str(row[product_name]), border=1)
            pdf.cell(w=35, h=8, txt=str(row[amount_purchased]), border=1)
            pdf.cell(w=30, h=8, txt=str(row[price_per_unit]), border=1)
            pdf.cell(w=30, h=8, txt=str(row[total_price]), border=1, ln=1)

        pdf.cell(w=30, h=8, border=1)
        pdf.cell(w=70, h=8,  border=1)
        pdf.cell(w=35, h=8,  border=1)
        pdf.cell(w=30, h=8,  border=1)
        pdf.cell(w=30, h=8, txt=str(total_sum), border=1, ln=15)
        pdf.ln(12)

        pdf.set_font(family="Times", style="B", size=10)
        pdf.set_text_color(0,0,0)
        pdf.cell(w=35, h=13, txt=f'The total amount due is {total_sum} {currency}.', ln=1)

     # Added a company name
        pdf.cell(w=35, h=8, txt=company_name)
        pdf.image(image_path, w=15)

        if not os.path.exists(pdfs_path):
            os.makedirs(pdfs_path)
        pdf.output(f"{pdfs_path}/{filename}.pdf")