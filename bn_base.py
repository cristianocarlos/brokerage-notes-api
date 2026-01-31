import re
import pdfplumber
from datetime import date, datetime

def get_value_or_default(data_list, index, default_value=None):
    try:
        return data_list[index]
    except IndexError:
        return default_value

def pdf_content(pdf_path: str):
    content = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"📄 PDF has {len(pdf.pages)} pages")
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()

                if page_text:
                    content += f"\n{'=' * 60}\n"
                    content += f"PAGE {page_num + 1}\n"
                    content += f"{'=' * 60}\n\n"
                    content += page_text + "\n"

                    print(f"✅ Processed page {page_num + 1} - {len(page_text)} characters")
                else:
                    print(f"⚠️  No text found on page {page_num + 1}")
        return content
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def format_br_date_to_db(br_date: str):
    date_obj = datetime.strptime(br_date, '%d/%m/%Y')
    return date_obj.strftime('%Y-%m-%d')

def format_us_date_to_db(br_date: str):
    date_obj = datetime.strptime(br_date, '%m/%d/%Y')
    return date_obj.strftime('%Y-%m-%d')

def resolve_auction_date(content: str):
    date_values = re.findall(r'\b\d{1,2}/\d{1,2}/\d{4}\b', content)
    return date_values[0]

def resolve_settlement_date(content: str):
    date_values = re.findall(r'\b\d{1,2}/\d{1,2}/\d{4}\b', content)
    br_today_date = date.today().strftime('%d/%m/%Y')
    last_value = get_value_or_default(date_values, 1, br_today_date)
    if date_values[0] == last_value:
        return get_value_or_default(date_values, 2, br_today_date) # quando tem mais de uma página
    return last_value