from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import requests
import re

def error(update, context):
    """Log Errors caused by Updates."""
    print('Update "%s" caused error "%s"', update, context.error)

def submit(bot, update):
	print("submit command received")
	chat_id = update.message.chat_id
	bot_token = get_token()
	message = "comando de submit recebido"
	update.message.reply_text(message)

def process_images(bot, update):
	print("receipt received")
	print(type(update.message))
	photo = None
	for p in update.message.photo:
		photo = p
	
	# todo: save into a storage
	photo.get_file().download(custom_path = './receipts/' + photo.file_id)

	update.message.reply_text('Comprovante recebido com sucesso, obrigado ' + update.message.chat.first_name)

def get_token():
	return open('../token.txt').read()

def main():
	print('starting bot')
	updater = Updater(get_token())
	dp = updater.dispatcher
	dp.add_handler(CommandHandler('submit',submit))
	dp.add_handler(MessageHandler(Filters.photo, process_images))
	print('bot started')
	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
 	main()