import requests
from getpass import getpass
import feedparser
import sys
import datetime
import dateutil.parser
import time

fmt = "%A %d. %B"

ISSUES_QUERY = ("https://api.github.com/orgs/{org}/issues"
                "?filter=subscribed&state=all")


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


def get_issues_data(org, auth):
    data = ["="*25 + " Issues feed " + "="*25]
    s = requests.session()
    url = ISSUES_QUERY.format(org=org)
    r = s.get(url, auth=auth)
    issues = r.json()
    for issue in issues:
        title = issue['title']
        if issue['user']['login'] == auth[0]:
            created = issue['created_at']
            dt = dateutil.parser.parse(created)
            data.append(dt.strftime(fmt) + " -- Issue created: " + title)
        else:
            comments = s.get(issue['comments_url'], auth=auth)
            comments = comments.json()
            for comment in comments:
                if comment['user']['login'] == auth[0]:
                    created = comment['created_at']
                    dt = dateutil.parser.parse(created)
                    msg = dt.strftime(fmt) + " -- commented on issue: " + \
                          title
                    data.append(msg)
    return data


def get_user_actor(auth):
    data = ["="*25 + " Private events " + "="*25]
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
        data.append(dt.strftime(fmt) + " -- " + title)
    return data


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
        ind = sys.argv.index("--user")
        try:
            username = sys.argv[ind+1]
        except IndexError:
            username = raw_input("Username: ").strip()
        password = keyring.get_password("github",username)
        
    data1 = get_user_actor((username, password))
    data2 = get_issues_data("enthought",(username, password))
    data1.extend(data2)

    if "-o" in sys.argv:
        ind = sys.argv.index("-o")
        outfile = sys.argv[ind+1]
        s = "\n".join(data1)
        s = s.encode("utf8")
        with open(outfile, "w") as f:
            f.write(s)
    else:
        for line in data1:
            print line


if __name__ == "__main__":
    main()

