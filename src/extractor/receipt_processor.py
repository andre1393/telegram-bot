import numpy as np
import pandas as pd
import cv2
import logging
import os
from extractor.itau_extractor import ItauExtractor
from extractor.extractor import ExtractorDefault
from exceptions.exceptions import InvalidReceipt
from model.institutions import EInstitutions

def __check_receipt(image, template):
    logo = __logo_detector(image, template)
    return True

# read the receipt image and extract information like payer, due date, value etc
def read(receipt_path, logos_path, payer):
    logging.info(f'opening image: {receipt_path}')
    receipt_BGR = cv2.imread(receipt_path)

    logging.info(f'converting to grayscale: {receipt_path}')
    receipt = cv2.cvtColor(receipt_BGR, cv2.COLOR_BGR2GRAY)

    logging.info(f'checking if receipt is valid: {receipt_path}')

    institution = None
    for r, d, f in os.walk(logos_path):
        for file in f:
            if __check_receipt(cv2.imread(receipt_path), cv2.imread(f'{logos_path}{file}')):
                logging.info("receipt recognized")
                institution = EInstitutions[file.replace(".png", "")]
                break
    if institution is EInstitutions.itau:
        logging.info("bill from itau")
        extractor = ItauExtractor()
    elif institution is EInstitutions.nubank:
        logging.info("bill from nubank")
        extractor = ExtractorDefault()
    else:
        raise Exception("institution not recognized")

    return extractor.get_info(receipt, payer)

def __logo_detector(image, template, threshold = 0.9):
    w, h = template.shape[:-1]
    best_val = 0
    for s in np.linspace(0.1, 3.0, 15)[::-1]:
        try:
            img_resize = cv2.resize(image, None, fx=s, fy=s)
            res = cv2.matchTemplate(img_resize,template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if max_val > best_val:
                best_val = max_val
            
            if best_val > threshold:
                return True
        except:
            pass
    logging.info(f'max val: {best_val}')
    return best_val > threshold