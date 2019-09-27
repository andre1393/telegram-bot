import numpy as np
import pandas as pd
import cv2
import logging
from extractor.itau_extractor import ItauExtractor
from exceptions.exceptions import InvalidReceipt

def __check_receipt(image, template):
    logo = __logo_detector(image, template)
    if not logo:
        raise InvalidReceipt()
    return True

# read the receipt image and extract information like payer, due date, value etc
def read(receipt_path, logos_path, payer):
    logging.info(f'opening image: {receipt_path}')
    receipt_BGR = cv2.imread(receipt_path)

    logging.info(f'converting to grayscale: {receipt_path}')
    receipt = cv2.cvtColor(receipt_BGR, cv2.COLOR_BGR2GRAY)

    logging.info(f'checking if receipt is valid: {receipt_path}')
    __check_receipt(cv2.imread(receipt_path), cv2.imread(logos_path))

    extractor = ItauExtractor()
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