import requests


def DiscSendMes(webhook, content, username, avatar_url):
    global data
    data = {
        "content": content,
        "username": username,
        "avatar_url": avatar_url
    }
    resl = requests.post(webhook, json=data)
    if resl.status_code != 200:
        print("Could not send message")


def DiscDelWeb(webhook):
    requests.delete(webhook)

def DiscSpamWeb(webhook, content, username, avatar_url):
    while True:
        DiscSendMes(webhook, content, username, avatar_url)

def DiscChangeName(webhook, name):
    requests.patch(webhook, json={"name": name})

def DiscSendEmbed(webhook, title, description):
    data = {
        "embeds": [
            {
                "description": description,
                "title": title
            }
        ]
    }
    requests.post(webhook, json=data)

