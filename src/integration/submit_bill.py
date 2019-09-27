import requests
import logging

def submit(bill, contas_host, call_api):
	url = f"http://{contas_host}/update-conta?conta={bill.name}&data_vencimento={bill.due_date}&data_pagamento={bill.paid_date}&pagador={bill.payer}&valor_pago={bill.value}&categoria={bill.category}&obs={bill.ps}&tipo_gasto=CONTAS"
	logging.info(url)
	
	if call_api:
		logging.info("calling contas api")
		r = requests.get(url)
		print(r)
	return True
