from bn_base import pdf_content
import os
import bn_btg
import bn_itau
import bn_dw

def dw(pdf_path):
    content = pdf_content(pdf_path)
    bn_dw.brokerage_notes(content)
    bn_dw.trades(content)

def itau(pdf_path):
    content = pdf_content(pdf_path)
    bn_itau.brokerage_notes(content)
    bn_itau.trades(content)

def btg(pdf_path):
    content = pdf_content(pdf_path)
    bn_btg.brokerage_notes(content)
    bn_btg.trades(content)

'''
input_path = Path('2022-05-btg')
pdf_files = list(input_path.glob("*.pdf"))
for pdf_file in pdf_files:
    print(pdf_file)
    btg_trades(pdf_file)

for root, dirs, files in os.walk('import'):
    for file in files:
        file_path = os.path.join(root, file)
        if '.pdf' in file_path:
            print(file_path)
            dw(file_path)
'''

# print('import/tmp.pdf')
