import sqlite3


sqlconn = sqlite3.connect("./fileinfo.db")
sql = sqlconn.cursor()
sql.execute("select pe_info.setinfo, pe_info.impinfo from pe_info, base_info where pe_info.md5 = base_info.md5 and base_info.name = '/home/zrx/code/S.M.A.R.T/dist/main/main.exe")
sqlconn.commit()
sql.fetchone()
a = sql.fetchone()


