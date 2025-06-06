import os

from pyrogram import Client, filters, enums
from pyrogram.handlers import BusinessConnectionHandler, MessageHandler, RawUpdateHandler, BusinessMessageHandler, CallbackQueryHandler

from handlers import MediaHandler, UpdatesHandler, CommandsHandler, RawUpdatesHandler, MessagesHandler, CallbackQueriesHandler

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

# Initialize the Telegram client
app = Client(
    name="RMUserBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    parse_mode=enums.ParseMode.HTML
)

app.add_handler(BusinessMessageHandler(MessagesHandler.handle_outgoing_message, filters.outgoing))
app.add_handler(BusinessMessageHandler(MessagesHandler.handle_incoming_message, filters.incoming))
app.add_handler(BusinessConnectionHandler(UpdatesHandler.handle_connection_update))
app.add_handler(MessageHandler(MediaHandler.handle_contact, filters.contact))
app.add_handler(MessageHandler(CommandsHandler.handle_start_command, filters.command("start")))
app.add_handler(CallbackQueryHandler(callback=CallbackQueriesHandler.handle_get_user_callback, filters=filters.regex(r"^get_user_(\d+)$")))
app.add_handler(RawUpdateHandler(RawUpdatesHandler.handle_raw_update))

if __name__ == "__main__":
    app.run()