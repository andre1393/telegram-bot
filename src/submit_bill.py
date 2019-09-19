import requests

def submit(bill):
	url = f"http://35.188.218.51/update-conta?conta={bill.name}&data_vencimento={bill.due_date}&data_pagamento={bill.paid_date}&pagador={bill.payer}&valor_pago={bill.value}&categoria={bill.category}&obs={bill.ps}&tipo_gasto=CONTAS"
	print(url)
	r = requests.get(url)
	print(r)
	return True