import requests
from getpass import getpass
import feedparser
import sys
import datetime
import time

fmt = "%A %d. %B"

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
    entries = feed.get('entries')[::-1]
    for entry in entries:
        title = entry['title']
        published = entry['published_parsed']
        dt = datetime.datetime.fromtimestamp(time.mktime(published))
        print dt.strftime(fmt) + " -- " + title

def get_user_events(auth):
    s = requests.session()
    url = "https://api.github.com/users/{}/events".format(auth[0])
    r = s.get(url,auth=auth)
    print len(r.json)

def main():
    import keyring
    if "--userpass" in sys.argv:
        username = raw_input("Username: ").strip()
        password = getpass('Password: ')
        keyring.set_password("github",username, password)
    elif "--user" in sys.argv:
        username = raw_input("Username: ").strip()
        password = keyring.get_password("github",username)
        
    get_user_actor((username, password))

if __name__ == "__main__":
    main()

