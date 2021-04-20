import os
import logging


def create_dirs(dirs):
	# TODO: save into a storage

	for d in dirs:
		if not os.path.exists(d):
			logging.info(f'directory {d} does not exists. creating...')
			os.makedirs(d)


def get_args():
	return os.getenv('SUBMIT_BILL', False), os.getenv('CONTAS_HOST'), os.getenv('CONTAS_PORT')
