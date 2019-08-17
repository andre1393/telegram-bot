import numpy as np
import pandas as pd
import cv2
from matplotlib import pyplot as plt
from bill import Bill

from PIL import Image # Importando o módulo Pillow para abrir a imagem no script
import pytesseract # Módulo para a utilização da tecnologia OCR

def normalize_payer(full_payer):
    payers = ['Andre', 'Barbara']
    for payer in payers:
        if payer.lower() in full_payer.lower():
            return payer
    return full_payer

def valid_bill_name(bill_name_orig):
    bill_name = bill_name_orig.lower()

    # when user dont fill de description field then it shows comprovante de pagamento titulos itau
    # in this, bot should ask to user wich bill it is
    if 'comprovante' in bill_name and 'pagamento' in bill_name and 'titulos' in bill_name:
        return None
    else:
        return bill_name_orig.replace('\n', ' ')

# read the receipt image and extract information like payer, due date, value etc
def read(receipt_path):
    print('open image')
    receipt_BGR = cv2.imread(receipt_path)
    print('convert to grayscale')
    receipt = cv2.cvtColor(receipt_BGR, cv2.COLOR_BGR2GRAY)

    if receipt.shape[0] >= 1200: # pagamento de boleto
        print('pagamento de boleto')
        try:
            bill_name = extract_text(receipt[50:100,:])
            paid_date = extract_text(receipt[200:220,63:130])
            payer = extract_text(receipt[780:800, :])
            due_date = extract_text(receipt[1090:1110,10:90])
            value = float(extract_text(receipt[110:130, 40:], config = '--psm 7').replace(',', '.'))

            return Bill(valid_bill_name(bill_name), value, paid_date, due_date, normalize_payer(payer))
        except Exception as e:
            print(e)
    else:
        print('receipt not recognized')

def extract_text(receipt, extractor = pytesseract.image_to_string, config = ''):
	return extractor(receipt, config = config)