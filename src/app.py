from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import requests
import re
import receipt_processor as rp
from bill import Bill

SUBMIT = 0

def error(update, context):
    """Log Errors caused by Updates."""
    print('Update "%s" caused error "%s"', update, context.error)

def process_images(bot, update):
	print("receipt received")

	photo = None
	for p in update.message.photo:
		photo = p
	
	# todo: save into a storage
	receipt_path = '../receipts/' + photo.file_id

	photo.get_file().download(custom_path = receipt_path)
	print('image downloaded')

	print('reading image text')
	bill = rp.read(receipt_path)
	print('teste')
	bill.name = 'teste'
	if bill.name == None:
		#update.message.reply_text('Não consegui identificar o nome dessa conta.\nQue conta é essa?')
		print('pooling')
		try:
			user_update = bot.get_updates(limit = 1, timeout = 20, allowed_updates = ['text'])
		except Exception as e:
			print(e)

		print('get_updates')
		if user_update.message.text != None:
			print('texto diferente de none')
			bill.name = user_update.message.text
			print('atualizando bill name')
			return bill_confirmation(bot, update, bill)
	else:
		return bill_confirmation(bot, update, bill)

def bill_confirmation(bot, update, bill):
	button_list = [[InlineKeyboardButton("Sim", callback_data="yes"), InlineKeyboardButton("Não", callback_data="no")]]
	
	msg = f'conta: {bill.name}\nvalor: {bill.value}\ndata de vencimento: {bill.due_date}\ndata de pagamento: {bill.paid_date}\npagador: {bill.payer}\n\nConfirma?'
	update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(button_list))
	
	return SUBMIT

def get_token():
	return open('../../token.txt').read()

def submit_bill(bot, update):
	query = update.callback_query
	answer = query.data

	if answer == 'yes':
		print(query.message.text)
		update.callback_query.message.reply_text('Conta cadastrada com sucesso!')
	else:
		update.callback_query.message.reply_text('Ok, cancelando cadastrado da conta')

	return True

def main():
	print('starting bot')
	updater = Updater(get_token())
	dp = updater.dispatcher
	
	conv_handler = ConversationHandler(
		entry_points=[MessageHandler(Filters.photo, process_images)],
    	states={
        	SUBMIT: [CallbackQueryHandler(submit_bill)]
    	},
    	fallbacks=[],
    	allow_reentry = True
	)

	#dp.add_handler(MessageHandler(Filters.photo, process_images))
	dp.add_handler(conv_handler)
	print('bot started')
	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
 	main()