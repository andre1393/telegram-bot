import requests
import logging

def submit(bill, contas_host, call_api):
	url = f"http://{contas_host}/update-conta?{bill.to_api_params()}"
	logging.info(url)
	
	if call_api:
		logging.info("calling contas api")
		r = requests.get(url)
		print(r)
	return True
