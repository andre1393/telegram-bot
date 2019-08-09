from telegram.ext import Updater, CommandHandler
import requests
import re

def submit(bot, update):
	print("message received")
	chat_id = update.message.chat_id
	bot_token = get_token()
	message = "mensagem recebida"
	send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + str(chat_id) + '&parse_mode=Markdown&text=' + message
	response = requests.get(send_text)

	return response

def get_token():
	return open('../token.txt').read()

def main():
	print('iniciando bot')
	updater = Updater('930261692:AAFeGW_nb7zsbe_7iExRcrXymRHpozN-F_8')
	dp = updater.dispatcher
	dp.add_handler(CommandHandler('submit',submit))
	updater.start_polling()
	updater.idle()
    
if __name__ == '__main__':
 	main()