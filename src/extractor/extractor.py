from model.bill import Bill
from PIL import Image # Importando o módulo Pillow para abrir a imagem no script
import pytesseract # Módulo para a utilização da tecnologia OCR
import logging
import datetime

def convert_float(x):
    x = x.replace("RS", "").replace("R$", "").replace(",", ".")
    float(x)
    return x

def to_portuguese_date(x):
    return x \
    .replace("FEV", "FEB") \
    .replace("ABR", "APR") \
    .replace("MAI", "MAY") \
    .replace("AGO", "AUG") \
    .replace("SET", "SEP") \
    .replace("DEZ", "DEC")

def convert_date(x):
    formats = ["%d/%m/%Y", "%d %b %Y"]
    for f in formats:
        try:
            return datetime.datetime.strptime(to_portuguese_date(x.lstrip().rstrip()), f)
        except Exception as e:
            pass

    raise Exception("not a date")

def convert_str(x):
    if len(x.lstrip().rstrip()) < 2:
        raise Exception("could not extract information from string")
    return x


VALUE_OPTIONS = ["valor"]
PAID_DATE_OPTIONS = ["pago em ", "pagamento efetuado em"]
DUE_DATE_OPTIONS = ["data do vencimento", "vencimento"]

ALL_PARAMETERS = [(VALUE_OPTIONS, convert_float, "_value"), 
                  (PAID_DATE_OPTIONS, convert_date, "_paid_date"),
                  (DUE_DATE_OPTIONS, convert_date, "_due_date")]


class ExtractorDefault:
    
    def __init__(self):
        self._last = None
        self._bill_name = None
        self._value = None
        self._paid_date = None
        self._due_date = None

    def get_info(self, receipt, payer):
        text = self._extract_text(receipt).split("\n")
        logging.info(text)
           
        for idx, t in enumerate(text, start=0):
            for parameter in ALL_PARAMETERS:
                value = self._isAnyOptions(t, parameter[0], parameter[1])
                if value and (getattr(self, parameter[2]) is None):
                    setattr(self, parameter[2], value)
            self._last = t

        return Bill(self._valid_bill_name(self._bill_name), self._value, self._due_date, self._paid_date, payer)

    def _isAnyOptions(self, text, options, extract_func):
        for o in options:
            if (o.lower() in text.lower()) | ((self._last is not None) and (o.lower() in self._last.lower())):
                return self._get_value(text, extract_func)
        return False

    def _get_value(self, text, extract_func):
        try:
            return extract_func(text)
        except Exception as e:
            pass

    def _extract_text(self, receipt, extractor = pytesseract.image_to_string, config = ''):
        return extractor(receipt, config = config)

    def _valid_bill_name(self, bill_name_orig):
        if bill_name_orig is None:
            return None

        bill_name = bill_name_orig.lower()

        # when user dont fill de description field then it shows comprovante de pagamento titulos itau
        # in this, bot should ask to user wich bill it is
        if 'comprovante' in bill_name and 'pagamento' in bill_name and 'titulos' in bill_name:
            return None
        else:
            return bill_name_orig.replace('\n', ' ')