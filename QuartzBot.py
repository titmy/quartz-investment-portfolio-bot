#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

INITIAL_INVESTMENT = 0.00022 # initial investment in BTC (to improve using returnDepositsWithdrawals())

from random import randint
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
from splinter import Browser
import logging
import poloniex
polo = poloniex.Poloniex(#Polo API)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    )



logger = logging.getLogger(__name__)
fh = logging.FileHandler('debug.log')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

LOCATION, QUARTZ_BAL, BIO = range(3)

browser = Browser('phantomjs')
browser.visit('http://feeds.feedburner.com/Coindesk?format=xml')
news_counter = 1

def start(bot, update):
    reply_keyboard = [['US', 'Singapore', 'Other']]

    update.message.reply_text(
        'Hi! My name is Quartz Bot. I will be your personal portfolio assistant for the Quartz Cryptocurrency Fund \n\n'
        'Just to get started, where are you currently located?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return LOCATION


def location(bot, update):
    # todo: add numpad

    user = update.message.from_user
    logger.info("Location of %s: %s" % (user.first_name, update.message.text))
    update.message.reply_text('I see! Please input the number of Quartz you currently have ',
                              reply_markup=ReplyKeyboardRemove())

    return QUARTZ_BAL


def quartz_bal(bot, update):
    user = update.message.from_user
    logger.info("Quartz Balance of %s: %s" % (user.first_name, update.message.text))
    update.message.reply_text('Ok that is awesome! Tell me more about yourself.',
                              reply_markup=ReplyKeyboardRemove())

    return BIO

def bio(bot, update):
    user = update.message.from_user
    logger.info("Bio of %s: %s" % (user.first_name, update.message.text))
    update.message.reply_text('Thank you! Nice meeting you!\n\n'
                                'To get updates: \n'
                                'type /portfolio to view portfolio balances\n'
                                'type /history to view trading history \n'
                                'type /pnl to view profit and losses since inception'
                                'type /news to get latest cryptocurrency news'
                                )

    return ConversationHandler.END

def help(bot, update):
    update.message.reply_text('Type /portfolio to view portfolio balances\n'
                                'Type /history to view trading history \n'
                                'Type /pnl to view profit and losses since inception'
                                )

def portfolio(bot,update):
    balance = list(polo.returnAvailableAccountBalances('exchange').values())
    balance = balance[0]
    payload = ""
    if not balance:
        payload = 'Portfolio is going to be initiated soon!'
    else:
        for key, value in balance.items():
            payload += key + ': ' + value + '\n'

    update.message.reply_text(payload)


def history(bot,update):
    hist = polo.returnTradeHistory('all')
    if not hist:
        hist = 'Empty history! We are going to start trading soon so stay tune.'
    update.message.reply_text(hist)

def pnl(bot,update):
    balance = polo.returnCompleteBalances()
    pf = list(polo.returnAvailableAccountBalances('exchange').values())[0]
    current_pf_value = 0.0
    for key, value in pf.items():
        current_pf_value += float(balance[key]['btcValue'])
    returns = current_pf_value/INITIAL_INVESTMENT
    if returns > 1:
        percentage_returns = (returns-1)*100
        update.message.reply_text('Returns: ' + '+' + str(percentage_returns) + '%')
    else:
        percentage_loss = (1-returns)*100
        update.message.reply_text('Returns: ' + '-' + str(percentage_loss) + '%')

def news(bot, update):
    link = browser.find_by_xpath('//*[@id="bodyblock"]/ul/li['+ str(randint(1,20)) + ']/h4/a')
    update.message.reply_text(link['href'])

def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation." % user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(#telegram API)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            LOCATION: [RegexHandler('^(US|Singapore|Other)$', location)],

            QUARTZ_BAL: [MessageHandler(Filters.text, quartz_bal)],

            BIO: [MessageHandler(Filters.text, bio)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # on different commands - answer in Telegram

    dp.add_handler(conv_handler)

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("portfolio", portfolio))
    dp.add_handler(CommandHandler("history", history))
    dp.add_handler(CommandHandler("pnl", pnl))
    dp.add_handler(CommandHandler("news", news))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
