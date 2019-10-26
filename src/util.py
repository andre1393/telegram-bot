import os
import logging

def create_dirs(dirs):
	# TODO: save into a storage

	for d in dirs:
		if not os.path.exists(d):
			logging.info(f'directory {d} does not exists. creating...')
			os.makedirs(d)

def get_token(cfg):
	print(f"token: {open(cfg.token).read()}")
	return open(cfg.token).read()

def get_args(sys):
	submit_bill = None
	contas_host = None
	
	if(len(sys.argv) < 3):
		logging.warn("please inform boolean submit_bill indicating that should call contas api, and contas host")
		exit(1)

	submit_bill = sys.argv[1].lower() in ["true"]
	contas_host = sys.argv[2]

	return submit_bill, contas_host