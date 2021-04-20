import logging

from PIL import Image # Importando o módulo Pillow para abrir a imagem no script
import pytesseract # Módulo para a utilização da tecnologia OCR

from model.bill import Bill


class ItauExtractor:

    def __init__(self):
        pass

    def get_info(self, receipt, payer):
        logging.info(f'image {receipt}: {receipt.shape}')
        if receipt.shape[1] < 260:  # pagamento de boleto
            logging.info(f'pagamento de boleto: {receipt}')
            bill_name = self.__extract_text(receipt[50:100,:])
            paid_date = self.__extract_text(receipt[200:220,63:130])
            due_date = self.__extract_text(receipt[1090:1110,10:90])
            value = float(self.__extract_text(receipt[110:130, 40:], config='--psm 7').replace(',', '.'))

            return Bill(self.__valid_bill_name(bill_name), value, paid_date, due_date, self.__normalize_payer(payer))
        else:
            text = self.__extract_text(receipt).split('\n')
            logging.info(text)
            
            bill_name = text[0]
            value = float(text[1].replace('RS', '').replace('R$', '').replace(',', '.'))
           
            nxt = False
            for idx, t in enumerate(text, start=0):
                if nxt and len(t) > 1:
                    due_date = t
                    nxt = False
               
                if ('pago em ' in t) or ('pagamento efetuado em' in t):
                    paid_date = t.replace('pago em ', '').replace('pagamento efetuado em', '')
                if 'data do vencimento' in t:
                    nxt = True
                    pass

        return Bill(self.__valid_bill_name(bill_name), value, paid_date, due_date, payer)

    def __extract_text(self, receipt, extractor=pytesseract.image_to_string, config=''):
        return extractor(receipt, config=config)

    def __normalize_payer(self, full_payer):
        payers = ['Andre', 'Barbara']
        for payer in payers:
            if payer.lower() in full_payer.lower():
                return payer
        return full_payer

    def __valid_bill_name(self, bill_name_orig):
        bill_name = bill_name_orig.lower()

        # when user dont fill de description field then it shows comprovante de pagamento titulos itau
        # in this, bot should ask to user wich bill it is
        if 'comprovante' in bill_name and 'pagamento' in bill_name and 'titulos' in bill_name:
            return None
        else:
            return bill_name_orig.replace('\n', ' ')
