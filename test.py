import sqlite3
import datetime

cnx = sqlite3.connect('fgr.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
cnx.row_factory = sqlite3.Row
c = cnx.cursor()
c.execute('select * from registrations')
r = c.fetchone()
print(r[0], r['time'], r[2], r[3], r[4], type(r[1]))