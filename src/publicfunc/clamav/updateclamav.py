#coding=utf-8

import sys
import os
import shutil
import tarfile
import zlib
import urllib2
import argparse
from convert2yara import parse_ndb, parse_ldb


URL_MAIN = "http://database.clamav.net/main.cvd"
URL_DAILY = "http://database.clamav.net/daily.cvd"

'''
连接上述URL并下载clamav所需文件
'''
def download_file(url):
    """
    Downloads a file.
    Source: https://stackoverflow.com/questions/22676/how-do-i-download-a-file-over-http-using-python
    """
    file_name = url.split('/')[-1]
    try:
        request = urllib2.Request(url)
        request.add_header("User-Agent", "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:35.0) Gecko/20100101 Firefox/38.0")
        u = urllib2.urlopen(url)
    except urllib2.HTTPError as e:
        print "Could not download %s." % url, e
        sys.exit(1)
    outfile = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        outfile.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status += chr(8) * (len(status) + 1)
        print status,

    outfile.close()

'''
解压文件
'''
def zlib_decompress(path, outpath):
    d = zlib.decompressobj(zlib.MAX_WBITS + 16)
    input = open(path, "rb")
    output = open(outpath, "wb")
    if not input or not output:
        print "[!] Error decompressing signatures."
        sys.exit(-1)

    while True:
        chunk = input.read(2048)
        if not chunk:
            break
        uncompressed = d.decompress(chunk)
        output.write(uncompressed)

    input.close()
    output.close()
    os.remove(path)

'''
更新特征规则
规则为base+daily
'''
def update_signatures(url, download):
    # Download CVD file if necessary
    if download:
        download_file(url)
    file_name = url.split('/')[-1]
    file_basename = file_name.split('.')[-2]

    # Extract signatures
    f = open(file_name, "rb")
    if not f or len(f.read(512)) != 512:  # Skip the CVD header
        print "[!] Error reading main.cvd!"
        sys.exit(-1)

    g = open("%s.tar.gz" % file_basename, "wb")
    if not g:
        f.close()
        print "[!] Error writing to %s.tar.gz!" % file_basename
        sys.exit(-1)

    # Create a copy of the virus definitions without the ClamAV header (it becomes a valid TGZ file)
    while True:
        data = f.read(2048)
        if not data:
            break
        g.write(data)

    f.close()
    g.close()

    # We need to keep a set of all the signatures seen, because there are duplicates in the ClamAV database and
    # Yara doesn't like that.
    RULES = set()

    # Excract the signatures
    zlib_decompress("%s.tar.gz" % file_basename, "%s.tar" % file_basename)
    tar = tarfile.open("%s.tar" % file_basename)
    tar.extract("%s.ndb" % file_basename)
    os.chmod("%s.ndb" % file_basename, 0644)
    if "%s.ldb" % file_basename in tar.getnames():
        tar.extract("%s.ldb" % file_basename)
        os.chmod("%s.ldb" % file_basename, 0644)
    tar.close()
    parse_ndb("%s.ndb" % file_basename, "clamav.yara", file_basename != "main")
    if os.path.exists("%s.ldb" % file_basename):
        parse_ldb("%s.ldb" % file_basename, "clamav.yara", file_basename != "main")
        os.remove("%s.ldb" % file_basename)
    os.remove("%s.tar" % file_basename)
    os.remove("%s.ndb" % file_basename)

# Work in the script's directory
if os.path.dirname(sys.argv[0]) != "":
    os.chdir(os.path.dirname(sys.argv[0]))

parser = argparse.ArgumentParser(description="Updates ClamAV signatures for plugin_clamav.")
parser.add_argument("--main", action="store_true", help="Update ClamAV's main signature file.")
parser.add_argument("--skip-download", dest="skipdownload", action="store_false",
                    help="Work with local copies of ClamAV signature files.")
args = parser.parse_args()

try:
    os.remove("clamav.yara")
except OSError:
    pass

if not os.path.exists("clamav.main.yara"):
    args.main = True

if args.main:
    if os.path.exists("clamav.main.yara"):
        os.remove("clamav.main.yara")
    with open("clamav.yara", "wb") as f:
        f.write("import \"pe\"\n\n")  # Do not forget to import our module.
    update_signatures(URL_MAIN, args.skipdownload)
    shutil.copy("clamav.yara", "clamav.main.yara")  # Keep a copy to which we can append future daily signature files.
else:
    # Use the old clamav.main.yara as a base and append the daily rules to it.
    shutil.copy("clamav.main.yara", "clamav.yara")

update_signatures(URL_DAILY, args.skipdownload)

try:
    os.remove("clamav.yarac")
except OSError:
    pass
os.chmod("clamav.yara", 0644)

# TODO: Support .hdb & .mdb (hashes of known malwares / sections) - http://resources.infosecinstitute.com/open-source-antivirus-clamav/
# TODO: Support .ldb (logical signatures)? Seems hard :(
