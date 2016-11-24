import socket
import git


def check_internet_connection():
    try:
        host = socket.gethostbyname("www.google.com")
        s = socket.create_connection((host, 80), 2)
        print "host to baidu"
	return True
    except:
        pass
	print "connect error"
    return False


def download_yara_rules_git():
    git.Git().clone("https://github.com/Yara-Rules/rules")

