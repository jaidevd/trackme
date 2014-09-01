import requests
from getpass import getpass
import feedparser

def get_repos_list(auth):
    s = requests.session()
    i = 1
    repos_request = ""
    repo_list = []
    while True:
        repos = s.get(repos_request.format(i), auth=auth).json()
        repo_list.extend(repos)
        i += 1
        if len(repos) == 0:
            break
    return repo_list

def get_user_actor(auth):
    s = requests.session()
    url = "https://api.github.com/feeds"
    r = s.get(url, auth=auth)
    actor_url = r.json()['current_user_actor_url']
    r = s.get(actor_url, auth=auth)
    user_feed = r.text.encode(r.encoding)
    feed = feedparser.parse(user_feed)
    for entry in feed.get('entries'):
        print entry['title']

def main():
    username = raw_input("Username: ").strip()
    password = getpass('Password: ')
    get_user_actor((username, password))

if __name__ == "__main__":
    main()

