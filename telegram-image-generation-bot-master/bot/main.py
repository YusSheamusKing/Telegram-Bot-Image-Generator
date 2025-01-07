from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
import os
import logging
import json
import sqlite3
from dotenv import load_dotenv
from helper import image_gen, helper_code

# Database file path
DB_FILE = "bot_users.db"

# Function to initialize the database
def init_db():
    """
    Creates the `users` table in the database if it doesn't exist.
    This table stores the `telegram_id` and `username` of the bot users.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            username TEXT
        )
    """)
    conn.commit()
    conn.close()

# Function to save user details to the database as djuneyd wanted me to make yes djuneyd i know you read this comment rn how are you?
def save_user_to_db(telegram_id, username):
    """
    Saves a user's Telegram ID and username to the database.
    If the user already exists, it ignores the duplicate entry.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO users (telegram_id, username) VALUES (?, ?)", (telegram_id, username))
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
    finally:
        conn.close()

# BotHandler class to manage bot operations
class BotHandler:
    def __init__(self):
        """
        Initializes the bot, sets up logging, and defines conversation states and handlers.
        """
        load_dotenv("env")  # Load environment variables from the .env file
        logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")  # Get the bot token from environment variables
        self.helper = helper_code  # Helper functions or utilities
        self.image_gen = image_gen  # Image generation utility

        # Define conversation states
        self.WAITING_FOR_PROMPT, self.WAITING_FOR_COUNT, self.WAITING_FOR_SIZE, self.WAITING_FOR_STYLE, self.WAITING_FOR_PRICE_DECISION, self.WAITING_FOR_PRICE = range(6)

        # Initialize the bot application
        self.application = Application.builder().token(self.bot_token).build()

        # Add command handlers and conversation handlers
        self.conv_handler = ConversationHandler(
            entry_points=[CommandHandler("image", self.image)],  # Start conversation with /image
            states={
                self.WAITING_FOR_PROMPT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_image_prompt)],
                self.WAITING_FOR_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_image_count)],
                self.WAITING_FOR_SIZE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_image_size)],
                self.WAITING_FOR_STYLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_image_style)],
                self.WAITING_FOR_PRICE_DECISION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_price_decision)],
                self.WAITING_FOR_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_price)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],  # Cancel conversation with /cancel
        )

        # Add handlers to the application
        self.application.add_handler(CommandHandler("start", self.start))  # Start command
        self.application.add_handler(self.conv_handler)  # Image generation conversation

    async def send_chat_action(self, update, context, action):
        """
        Sends a "typing" or "uploading" chat action to inform the user that the bot is processing.
        """
        try:
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=action)
        except Exception as e:
            logging.error(f"Error while sending chat action: {e}")

    async def start(self, update, context):
        """
        Handles the /start command. Greets the user and saves their details to the database.
        """
        user_id = update.message.from_user.id  # User's Telegram ID
        username = update.message.from_user.username or update.message.from_user.first_name  # Username or first name
        context.user_data["username"] = username
        context.user_data["telegram_id"] = user_id

        # Save user details to the database , yes saving!!!!djuneyds fav
        save_user_to_db(user_id, username)

        # Check if the user is authorized (custom logic in helper)
        if self.helper.is_user(user_id):
            message = (
                f"🌸 Greetings {username}, "
                f"I'm a stability-powered Telegram bot. Use the `/image` command to start generating an image. "
                f"You can type `/cancel` at any point to stop the process."
            )
        else:
            message = "Apologies, you lack the necessary authorization to utilize my services."
        await update.message.reply_text(text=message)

    async def image(self, update, context):
        """
        Starts the image generation conversation.
        """
        user_id = update.message.from_user.id
        if self.helper.is_user(user_id):
            await update.message.reply_text("Please enter a prompt for the image generation:")
            return self.WAITING_FOR_PROMPT
        else:
            await update.message.reply_text("Apologies, you lack the necessary authorization to utilize my services.")
            return ConversationHandler.END

    async def handle_image_prompt(self, update, context):
        """
        Handles the image prompt input from the user.
        """
        prompt = update.message.text
        context.user_data["prompt"] = prompt
        await update.message.reply_text("How many images would you like to generate? (1–4)")
        return self.WAITING_FOR_COUNT

    async def handle_image_count(self, update, context):
        """
        Handles the number of images input and moves to the next step.
        """
        try:
            count = int(update.message.text)
            if 1 <= count <= 4:
                context.user_data["count"] = count
                size_keyboard = [
                    ["landscape", "widescreen", "panorama"],
                    ["square-l", "square", "square-p"],
                    ["portrait", "highscreen", "panorama-p"],
                ]
                reply_markup = ReplyKeyboardMarkup(size_keyboard, one_time_keyboard=True)
                await update.message.reply_text("Please select the preferred size for the image:", reply_markup=reply_markup)
                return self.WAITING_FOR_SIZE
            else:
                await update.message.reply_text("Please enter a valid number between 1 and 4.")
                return self.WAITING_FOR_COUNT
        except ValueError:
            await update.message.reply_text("Invalid input. Please enter a number between 1 and 4.")
            return self.WAITING_FOR_COUNT

    async def handle_image_size(self, update, context):
        """
        Handles the image size input and moves to style selection.
        """
        size = update.message.text
        context.user_data["size"] = size
        style_keyboard = [
            ["photographic", "enhance", "anime"],
            ["digital-art", "comic-book", "fantasy-art"],
            ["line-art", "analog-film", "neon-punk"],
            ["isometric", "low-poly", "origami"],
            ["modeling-compound", "cinematic", "3d-model"],
            ["pixel-art", "tile-texture", "None"],
        ]
        reply_markup = ReplyKeyboardMarkup(style_keyboard, one_time_keyboard=True)
        await update.message.reply_text("Please select a style for the image:", reply_markup=reply_markup)
        return self.WAITING_FOR_STYLE

    async def handle_image_style(self, update, context):
        """
        Handles the image style input, generates the image, and asks for pricing.
        """
        style = update.message.text
        prompt = context.user_data.get("prompt", "")
        size = context.user_data.get("size", "square")
        count = context.user_data.get("count", 1)
        username = context.user_data.get("username", "Anonymous")
        telegram_id = context.user_data.get("telegram_id")

        reply_markup = ReplyKeyboardRemove()
        await update.message.reply_text("Processing your request...", reply_markup=reply_markup)

        for i in range(count):
            generated_image_path = self.image_gen.generate_image(prompt, style, size)
            if generated_image_path:
                # Save metadata to a text file , yes djunik your fav part of saving datas
                metadata_file_path = generated_image_path.replace(".png", ".txt")
                with open(metadata_file_path, "w") as metadata_file:
                    metadata_file.write(f"Prompt: {prompt}\n")
                    metadata_file.write(f"Style: {style}\n")
                    metadata_file.write(f"Size: {size}\n")
                    metadata_file.write(f"User: {username}\n")
                    metadata_file.write(f"Telegram ID: {telegram_id}\n")
                    metadata_file.write("Price: No\n")  # Default price decision

                await self.send_chat_action(update, context, ChatAction.UPLOAD_PHOTO)
                with open(generated_image_path, "rb") as f:
                    await context.bot.send_photo(update.message.chat_id, photo=f)

        await update.message.reply_text("Do you want to set a price for this image? (yes/no)")
        return self.WAITING_FOR_PRICE_DECISION

    async def handle_price_decision(self, update, context):
        """
        Handles the user's decision on whether to set a price for the image.
        """
        decision = update.message.text.strip().lower()
        if decision == "yes":
            await update.message.reply_text("What price do you want to set? (in dollars)")
            return self.WAITING_FOR_PRICE
        else:
            await update.message.reply_text("Price not set. Returning to main menu.")
            return ConversationHandler.END

    async def handle_price(self, update, context):
        """
        Handles the price input from the user and updates the metadata file.
        """
        try:
            price = float(update.message.text)
            # Retrieve the last generated image path
            generated_image_path = context.user_data.get("last_generated_image", None)

            if generated_image_path:
                # Update the metadata file with the price
                metadata_file_path = generated_image_path.replace(".png", ".txt")
                if os.path.exists(metadata_file_path):
                    with open(metadata_file_path, "a") as metadata_file:
                        metadata_file.write(f"Price: {price}\n")
                await update.message.reply_text(f"Price set to ${price}. Returning to main menu.")
            else:
                await update.message.reply_text("Error: No image found to associate the price. Please try again.")
            return ConversationHandler.END
        except ValueError:
            await update.message.reply_text("Invalid input. Please enter a numeric value for the price.")
            return self.WAITING_FOR_PRICE

    async def cancel(self, update, context):
        """
        Handles the /cancel command to terminate the conversation.
        """
        await update.message.reply_text("The operation has been canceled. You can start again by typing /image.")
        return ConversationHandler.END

    def run(self):
        """
        Starts the bot's polling process.
        """
        self.application.run_polling()


# Entry point for the bot , yes djuneyd i know you liked my comments unique style
if __name__ == "__main__":
    init_db()  # Initialize the database on startup
    bot_handler = BotHandler()
    bot_handler.run()

