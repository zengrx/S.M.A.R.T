--tables from fileinfo.db
CREATE TABLE base_info(
id int primary key not null,
name text,
size int,
type text,
time datetime,
md5 text
);
CREATE TABLE adv_info(
md5 text primary key not null,
sha1 text,
sha256 text,
ssdeep text,
extension text
);
CREATE TABLE pe_info(
md5 text primary key not null,
entrypnt text,
setinfo text,
impinfo text,
cpltime int,
petype int,
entropy real
);
--tables from detected
CREATE TABLE yara_result(
md5 text primary key not null,
ruletype text,
name text,
rule text,
description text,
number int,
judge text
);
CREATE TABLE virustotal_result(
md5 text primary key not null,
apikey text,
result text,
respondcode int
);
