import socket
import git


def check_internet_connection():
    try:
        host = socket.gethostbyname("www.google.com")
        s = socket.create_connection((host, 80), 2)
        print "internet ok"
        return True
    except:
        pass
        print "internet err"
    return False


def download_yara_rules_git():
    git.Git().clone("https://github.com/Yara-Rules/rules")

