import requests
from dotenv import load_dotenv
import os


def get_telegram_updates():
    load_dotenv()
    api_key = os.getenv("TELEGRAM_BOT_API_KEY")
    GET_UPDATES_URL = f"https://api.telegram.org/bot{api_key}/getUpdates"
    updates = requests.get(GET_UPDATES_URL).json()
    return updates


def find_telegram_chat_id(user_telegram_username):
    updates = get_telegram_updates()
    found_chat_id = -1

    for result in updates["result"]:
        if result["message"]["from"]["username"] == user_telegram_username:
            found_chat_id = result["message"]["chat"]["id"]
            break

    return found_chat_id


def find_telegram_chat_ids(telegram_usernames: list) -> list:
    updates = get_telegram_updates()
    results_list = list()
    for username in telegram_usernames:
        for result in updates["result"]:
            if result["message"]["from"]["username"] == username:
                found_chat_id = result["message"]["chat"]["id"]
                results_list.append({
                    "username": username,
                    "chat_id": found_chat_id
                })
                break

    return results_list


def send_telegram_message(chat_id, message):
    load_dotenv()
    api_key = os.getenv("TELEGRAM_BOT_API_KEY")

    SEND_MESSAGE_URL = f"https://api.telegram.org/bot{api_key}/sendMessage?chat_id={chat_id}&text={message}&parse_mode=HTML"
    r = requests.get(SEND_MESSAGE_URL)
    print(r)
