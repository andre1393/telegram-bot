import logging
import os
import time
import sys

from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatAction

from integration.submit_bill import submit
import extractor.receipt_processor as rp
from model.bill import Bill, EFields
import config as cfg
from util import get_args, create_dirs


logging.basicConfig(
    format='%(asctime)s - %(levelname)s\t: %(message)s (%(filename)s:%(lineno)d)',
    datefmt='%d-%b-%y %H:%M:%S',
    level=logging.INFO
)

SUBMIT, SET_BILL_NAME, APPLY_CHANGE, CHANGE_VALUE_OPTIONS = range(4)

cache_bill = None


def introduction(bot, update):
    send_message_delay(bot, update, 'Olá eu sou o bot das contas \uD83E\uDD16')
    send_message_delay(bot, update, 'Eu vou te ajudar a cadastrar as suas contas pagas \uD83E\uDD11')
    send_message_delay(bot, update, 'Para começar, me envie um comprovante de pagamento de alguma conta \uD83D\uDCC4')
    send_message_delay(bot, update, 'Eu vou ler as informações no comprovante e cadastrar pra vc \uD83E\uDD13')
    send_message_delay(bot, update, 'Facil né :\uD83D\uDE1C')
    send_message_delay(
        bot, update,
        'Ah, como eu ainda estou evoluindo \uD83D\uDC76 \n Por enquanto eu só aceito comprovantes do Itau.'
    )
    update.message.reply_text(
        'E se quando você realizar o pagamento já incluir o nome da conta na descrição facilita bastante'
    )
    return ConversationHandler.END


def send_message_delay(bot, update, msg, sleep_time = 0.8):
    update.message.reply_text(msg)
    bot.send_chat_action(update.message.chat.id, ChatAction.TYPING)
    time.sleep(sleep_time)


def process_images(bot, update, user_data):
    bot.send_chat_action(update.message.chat.id, ChatAction.TYPING)

    logging.info('receipt received')
    payer = update.message.chat.first_name

    photo = None
    for p in update.message.photo:
        if photo is None:
            photo = p
        
        if p.file_size > photo.file_size:
            photo = p

    temp_dir, receipts_dir = cfg.temp_dir % payer, cfg.receipts_dir % payer
    
    create_dirs([temp_dir, receipts_dir])
    all_images_path = f'{temp_dir}/{photo.file_id}'
    receipts_path = f'{receipts_dir}/{photo.file_id}'

    photo.get_file().download(custom_path=all_images_path)
    logging.info(f'image downloaded: {photo.file_id}')

    logging.info(f'reading image text: {photo.file_id}')

    try:
        bill = rp.read(all_images_path, cfg.logos_path, payer)
        user_data['bill'] = bill
        if bill.name is None:
            cache_bill = bill
            update.message.reply_text('Não consegui identificar o nome dessa conta. Que conta é essa?')
            return SET_BILL_NAME
        else:
            os.rename(all_images_path, receipts_path)
            bill_confirmation_button(update.message, bill)
            return SUBMIT

    except rp.InvalidReceipt as e:
        logging.info(f'recibo invalido: {photo.file_id}')
        update.message.reply_text('Recibo invalido\nPor enquanto só sei cadastrar recibos do banco Itaú :/')

    return ConversationHandler.END


def bill_confirmation_button(message, bill):
    button_list = [ 
        [InlineKeyboardButton('Confirma', callback_data='confirm')],
        [InlineKeyboardButton('Alterar algum valor', callback_data='change_value')],
        [InlineKeyboardButton('Cancelar', callback_data='cancel')]]

    msg = bill.to_text() + '\n\nO que deseja fazer?'
    message.reply_text(msg, reply_markup=InlineKeyboardMarkup(button_list))


def change_value_options_button(message):
    button_list = [
        [InlineKeyboardButton('Alterar conta', callback_data=EFields.name.name)],
        [InlineKeyboardButton('Alterar valor', callback_data=EFields.value.name)],
        [InlineKeyboardButton('Alterar data de Pagamento', callback_data=EFields.paid_date.name)],
        [InlineKeyboardButton('Alterar data de Vencimento', callback_data=EFields.due_date.name)],
        [InlineKeyboardButton('Alterar pagador', callback_data=EFields.payer.name)],
        [InlineKeyboardButton('Cancelar', callback_data='value'), InlineKeyboardButton('Voltar', callback_data='return')]]

    message.reply_text('O que deseja Alterar?', reply_markup=InlineKeyboardMarkup(button_list))


def apply_change(bot, update, user_data):
    bill = user_data['bill']
    setattr(bill, user_data['fix_field'], update.message.text)
    bill_confirmation_button(update.message, bill)
    return SUBMIT


def set_bill_name(bot, update, user_data):
    bill = user_data['bill']
    bill.name = update.message.text

    bill_confirmation_button(update.message, bill)

    return SUBMIT


def callback_change_value_options(bot, update, user_data):
    query = update.callback_query
    answer = query.data

    logging.info(answer)
    if answer == 'cancel':
        return cancel_receipt(bot, update)
    elif answer == 'return':
        bill_confirmation_button(update.callback_query.message, user_data['bill'])
        return SUBMIT
    else:
        msg = f'Qual o valor de {EFields[answer].value} certo?'
        if (EFields[answer] == EFields.paid_date) or (EFields[answer] == EFields.due_date):
            msg += '\nFormato: (dia/mes/ano)'
        update.callback_query.message.reply_text(msg)
        user_data['fix_field'] = answer
        return APPLY_CHANGE


def cancel_receipt(bot, update):
    update.callback_query.message.reply_text('Belê, cancelei o comprovante')
    return ConversationHandler.END


def submit_bill(bot, update, user_data):
    query = update.callback_query
    answer = query.data

    should_submit_bill, contas_host, contas_port = get_args()
    logging.info(f'submit bill: {should_submit_bill}')
    logging.info(f'contas host: {contas_host}')

    if answer == 'confirm':
        logging.debug(query.message.text)
        submit(user_data['bill'], contas_host, contas_port, should_submit_bill)
        update.callback_query.message.reply_text('Conta cadastrada com sucesso!')
        return ConversationHandler.END
    elif answer == "cancel":
        return cancel_receipt(bot, update)
    elif answer == "change_value":
        change_value_options_button(update.callback_query.message)
        return CHANGE_VALUE_OPTIONS

    return ConversationHandler.END


def main():
    logging.info('starting bot')
    updater = Updater(os.getenv('TELEGRAM_TOKEN'))
    dp = updater.dispatcher
    
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.photo, process_images, pass_user_data=True),
                      MessageHandler(Filters.text, introduction)],
        states={
            SET_BILL_NAME: [MessageHandler(Filters.text, set_bill_name, pass_user_data=True)],
            SUBMIT: [CallbackQueryHandler(submit_bill,  pass_user_data=True)],
            APPLY_CHANGE: [MessageHandler(Filters.text, apply_change, pass_user_data=True)],
            CHANGE_VALUE_OPTIONS: [CallbackQueryHandler(callback_change_value_options, pass_user_data=True)]
        },
        fallbacks=[],
        allow_reentry=False
    )

    #dp.add_handler(MessageHandler(Filters.photo, process_images))
    dp.add_handler(conv_handler)
    logging.info('bot started')
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':    
    main()
