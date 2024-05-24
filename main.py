from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest, GetHistoryRequest
from telethon.tl.functions.contacts import SearchRequest, ResolveUsernameRequest
from telethon.tl.functions.channels import (
    GetFullChannelRequest,
)
from telethon.tl.types import (
    InputPeerEmpty,
    ChannelParticipantsAdmins,
    ChatFull,
    ChannelFull,
    Message,
)
import requests
import sys
from bs4 import BeautifulSoup
import re
import time
import json
from config import settings
import csv

chats = []
last_date = None
size_chats = 200
groups = []

ru_alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
en_alphabet = "abcdefghijklmnopqrstuvwxy"


def telegram_parser():
    # Параметры из my.telegram.org
    api_id = settings["tg_api_id"]
    api_hash = settings["tg_api_hash"]
    session = "gazp"

    client = TelegramClient(
        session, api_id, api_hash, system_version="4.16.30-vxCUSTOM"
    )
    client.start()
    groups = []
    users = []
    print("Старт")
    with open("result.csv", "w", encoding="utf-8") as csvfile:
        csvfile.write("")
    with open("result.csv", "a", encoding="utf-8") as scvfile:
        writer = csv.writer(scvfile)
        writer.writerow(["Канал", "Имя", "Никнейм", "Совпало ключевых слов"])
        with open("q_names.txt", encoding="utf-8", mode="r") as f:
            queries = f.readlines()
            for query in queries:
                result = client(SearchRequest(limit=size_chats, q=query))
                for chat in result.chats:
                    if chat.megagroup:
                        continue
                    if chat in groups:
                        continue
                    allow = 0
                    full_chat = client(GetFullChannelRequest(chat))
                    hash = full_chat.chats[0].access_hash
                    messages = client(
                        GetHistoryRequest(chat, 0, None, 0, 300, 0, 0, hash)
                    )
                    for message in messages.messages:
                        if not isinstance(message, Message):
                            continue
                        if any(ext in message.message for ext in queries):
                            allow += 1
                    if allow > 1:
                        print("Ок")
                    else:
                        continue
                    try:
                        linked_chat = full_chat.chats[1]
                        users = []
                        for user in client.iter_participants(
                            linked_chat, 10, filter=ChannelParticipantsAdmins
                        ):
                            writer.writerow(
                                [chat.title, user.first_name, user.username, allow]
                            )
                    except Exception as e:
                        writer.writerow([chat.title, None, None, allow])
                    groups.append(chat)
    for i in range(33):
        for j in range(33):
            with open("result.csv", "a", encoding="utf-8") as scvfile:
                writer = csv.writer(scvfile)
                query = ru_alphabet[i] + ru_alphabet[j] + ru_alphabet[k]
                result = client(SearchRequest(limit=size_chats, q=query))
                for chat in result.chats:
                    if chat.megagroup:
                        continue
                    if chat in groups:
                        continue
                    allow = 0
                    full_chat = client(GetFullChannelRequest(chat))
                    hash = full_chat.chats[0].access_hash
                    messages = client(
                        GetHistoryRequest(chat, 0, None, 0, 300, 0, 0, hash)
                    )
                    for message in messages.messages:
                        if not isinstance(message, Message):
                            continue
                        if any(ext in message.message for ext in queries):
                            allow += 1
                    if allow > 5:
                        print("Ок")
                    else:
                        groups.append(chat)
                        continue
                    try:
                        linked_chat = full_chat.chats[1]
                        users = []
                        for user in client.iter_participants(
                            linked_chat, 10, filter=ChannelParticipantsAdmins
                        ):
                            writer.writerow(
                                [
                                    chat.title,
                                    user.first_name,
                                    user.username,
                                    allow,
                                ]
                            )
                    except Exception as e:
                        writer.writerow([chat.title, None, None, allow])
                    groups.append(chat)


def discord_parser():
    query = "crypto"
    offset = 0
    page = requests.get(f"https://discord.com/servers?query={query}")
    soup = BeautifulSoup(page.text, "html.parser")
    answers = re.match(
        r"\d+",
        soup.find(
            "div",
            class_="colorStandard-1nZ0G7 size20-pPMkrV textMedium-3Ic-hz strong-3oJTBJ",
        ).text,
    ).group()
    headers = {"Authorization": settings["ds_auth"]}
    print(
        json.loads(
            requests.get(
                "https://discord.com/api/v9/channels/319560327719026709/messages?limit=100",
                headers=headers,
            ).text
        )["message"]
    )
    while answers < offset:
        offset += 12
        page = requests.get(f"https://discord.com/servers?query={query}")
        soup = BeautifulSoup(page.text, "html.parser")
        links = soup.find_all(
            "a",
            class_="link-1Mrh4O externalLink-2_8PKT linkDefault-1HiIFh flexRow-11pq_V listItemContainer-1x88Wn",
        )
        for link in links:
            try:
                link = link.get("href")
                link.split("/")[-1]
            except:
                continue


# searchListItem-3mtFl3
# https://discord.com/servers?query=crypto&offset=48

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Введите: main.py <источник поиска>(tg/ds)")
        exit(1)
    match sys.argv[1]:
        case "tg":
            telegram_parser()
        case "ds":
            discord_parser()
