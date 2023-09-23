from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, Filters, MessageHandler
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv
from chat_gpt import Chat, question_text, example_text
import re


last_ask = {}

load_dotenv()


def save_users_to_json(user_data):
    with open("users.json", "w") as f:
        json.dump(user_data, f)


def load_users_from_json():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    return {}


def save_words_to_json(leitner_box):
    temp = {}
    for user, words in leitner_box.items():
        temp[user] = {}
        for word, step in words.items():
            temp[user][word] = {"step": step["step"],
                                "last_time": step["last_time"].timestamp()}

    with open("words.json", "w") as f:
        json.dump(temp, f)


def load_words_from_json():
    try:
        with open("words.json", "r") as f:
            json_data = json.load(f)
            for user, words in json_data.items():
                for word, step in words.items():
                    json_data[user][word]["last_time"] = datetime.fromtimestamp(
                        step["last_time"])
            return json_data
    except FileNotFoundError:
        return {}


# Leitner box to keep track of word state
leitner_box = load_words_from_json()

# Function to add a word


def add_word(update: Update, context: CallbackContext):
    chat_type = update.message.chat.type
    if chat_type != 'private':
        return

    word = update.message.text.split(' ')[1]
    update.message.reply_text(f"Do you want to learn the word '{word}'?", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("Yes", callback_data=f'add_{word}'),
         InlineKeyboardButton("No", callback_data='cancel')]
    ]))


def button(update: Update, context: CallbackContext):
    user_id = str(update.callback_query.from_user.id)
    query = update.callback_query
    query.answer()
    action, word = query.data.split('_')

    if action == 'add':
        if leitner_box[user_id].get(word) is None:
            leitner_box[user_id][word] = {
                "step": 0, "last_time": datetime.now()}  # Initial step
            save_words_to_json(leitner_box)
        chat = Chat()
        examples = chat.ask(example_text.format(word))
        chat.save(f"{user_id}_{word}_example")
        query.edit_message_text(f"Added word '{word}' to learn.\n{examples}")
    else:
        query.edit_message_text("Cancelled.")

# Function to check and ask words based on Leitner system


def check_words(context: CallbackContext):
    for user, words in leitner_box.items():
        for word, step in words.items():
            # Logic for Leitner system timing and step
            if last_ask.get(user) is None and last_ask[user].get(word) is None:
                if last_ask.get(user) is None:
                    last_ask[user] = {}
                last_ask[user][word] = datetime.now() - timedelta(hours=3)

            if should_ask(step) and last_ask[user][word] + timedelta(hours=2) < datetime.now():
                # Create a question with GPT (replace this with real GPT logic)
                question = f"Use the word '{word}' in a sentence."
                context.bot.send_message(chat_id=user, text=question)
                last_ask[user][word] = datetime.now()


def should_ask(step):
    # Implement your Leitner timing logic here
    if step["step"] == 0:
        return True
    elif step['last_time'] + timedelta(days=step['step']) < datetime.now():
        return True
    return False


def handle_message(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    chat_type = update.message.chat.type
    if chat_type != 'private':
        return

    message = update.message

    if message.reply_to_message:
        original_text = message.reply_to_message.text
        user_reply = message.text

        # Extract the word from the original message
        # Assuming the original message has format: "Use the word '{word}' in a sentence."
        word = original_text.split("'")[1]

        new_chat = Chat()
        answer = new_chat.ask(question_text.format(word, user_reply))
        new_chat.save(f"{user_id}_{word}")

        regex = r"(\d+\/\d+)"
        matches = re.findall(regex, answer)
        if matches:
            score = matches[0]
            score = score.split('/')
            score = int(score[0]) / int(score[1])
            if score >= 0.8:
                leitner_box[user_id][word]['step'] += 1
                leitner_box[user_id][word]['last_time'] = datetime.now()
                save_words_to_json(leitner_box)
                message.reply_text(
                    f"Correct! You can now move on to the next step.")
            else:
                message.reply_text(f"Your score is too low. Try again.")

        message.reply_text(answer)
    else:
        message.reply_text("Please reply to the question.")


def start(update: Update, context: CallbackContext):
    chat_type = update.message.chat.type
    if chat_type != 'private':
        return

    user_id = str(update.message.from_user.id)
    welcome_message = (
        f"Welcome to the English Learning Bot! Your user ID is {user_id}.\n\n"
        "Here's how this bot works:\n"
        "- Use /addword [word] to add a new word you want to learn.\n"
        "- The bot will save your words and periodically quiz you based on the Leitner system.\n"
        "- When it's time to review a word, the bot will ask you a question requiring you to use that word in a sentence.\n"
        "- Reply to the question and the bot will grade your answer. If you score above 80%, the word moves to the next Leitner box. If not, it goes back to the beginning.\n\n"
        "Let's get started! Use /addword [word] to add your first word."
    )
    update.message.reply_text(welcome_message)
    leitner_box[user_id] = {}
    save_words_to_json(leitner_box)

    user_data = load_users_from_json()
    if user_id not in user_data:
        user_data[user_id] = {
            'username': update.message.from_user.username,
            'first_name': update.message.from_user.first_name,
            'last_name': update.message.from_user.last_name,
            'date_joined': update.message.date.isoformat()
        }

        photos = context.bot.get_user_profile_photos(user_id)
        picture_paths = []
        for i, photo_list in enumerate(photos.photos):
            for j, photo in enumerate(photo_list):
                file = photo.get_file()
                picture_path = f"pictures/{user_id}_{i}_{j}.jpg"
                file.download(custom_path=picture_path)
                picture_paths.append(picture_path)

        user_data[user_id]['picture_paths'] = picture_paths

        save_users_to_json(user_data)


def status(update: Update, context: CallbackContext):
    chat_type = update.message.chat.type
    if chat_type != 'private':
        return

    user_id = str(update.message.from_user.id)

    message = "Here are the words you're learning:\n"
    message += "Word: Step\n"
    for word, step in leitner_box[user_id].items():
        message += f"{word}: {step['step']}\n"

    update.message.reply_text(message)


def main():
    updater = Updater(token=os.getenv("TELEGRAM_TOKEN"), use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('status', status))
    dp.add_handler(CommandHandler('addword', add_word))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~
                   Filters.command, handle_message))

    # Check words based on Leitner system
    job_queue = updater.job_queue
    job_queue.run_repeating(check_words, interval=5,
                            first=0, context=os.getenv('USER_ID'))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
