import sqlite3
import datetime

class Guest:
    def __init__(self, db_row=None):
        if db_row is None:
            self.found = False
            return
        self.found = True
        self.first_name = db_row['first_name']
        self.last_name = db_row['last_name']
        self.company = db_row['company']
        self.email = db_row['email']
        self.phone = db_row['phone']
        self.badge = db_row['badge']

class Registration:
    def __init__(self, db_row=None):
        if db_row is None:
            self.found = False
            return
        self.found = True
        self.id = db_row['id']
        self.time = db_row['time']
        self.direction = db_row['direction']
        self.auto_added = db_row['auto_added']
        self.badge_id = db_row['badge_id']

class FGR_DB :
    DB_NAME = 'resources/fgr.db'

    TABLES = {}
    TABLES['guests'] = (
        "CREATE TABLE IF NOT EXISTS guests ("
        "  first_name TEXT,"
        "  last_name TEXT,"
        "  company TEXT,"
        "  email TEXT,"
        "  phone TEXT,"
        "  badge TEXT PRIMARY KEY UNIQUE NOT NULL"
        ")")

    TABLES['registrations'] = (
        "CREATE TABLE IF NOT EXISTS registrations ("
        "  id integer PRIMARY KEY,"
        "  'time' timestamp,"
        "  direction TEXT,"
        "  auto_added BOOL,"
        "  badge_id TEXT NOT NULL REFERENCES guests (badge)"
        ")")

    ADD_GUEST = ("INSERT INTO guests "
                 "(first_name, last_name, company, email, phone, badge)"
                 "VALUES (?, ?, ?, ?, ?, ?)")

    ADD_REGISTRATION =("INSERT INTO registrations "
                 "(time, direction, auto_added, badge_id)"
                 "VALUES (?, ?, ?, ?)")

    def test_populate_database(self):
        cursor = self.cnx.cursor()
        guests = [
            ('voornaam1', 'achternaam1', 'bedrijf1', 'email1@test.be', '0311111', '11'),
            ('voornaam2', 'achternaam2', 'bedrijf2', 'email2@test.be', '0322222', '22'),
        ]

        registrations = [
            ['18/2/2018 15:08:13', ('IN', 'F', '11')],
            ['18/2/2018 20:00:00', ('UIT', 'T', '11')],
            ['18/2/2018 15:01:13', ('IN', 'F', '22')],
            ['18/2/2018 19:59:13', ('UIT', 'F', '22')],
        ]
        for i in guests:
            cursor.execute(self.ADD_GUEST, i)

        for i in registrations:
            d = datetime.datetime.strptime(i[0], '%d/%m/%Y %H:%M:%S')
            cursor.execute(self.ADD_REGISTRATION, (d,)+i[1])

        print('Database populated')
        self.cnx.commit()
        cursor.close()


    def __init__(self):
        self.cnx = sqlite3.connect(self.DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.cnx.row_factory = sqlite3.Row
        cursor = self.cnx.cursor()

        for name, ddl in self.TABLES.items():
            print("Creating table {}: ".format(name), end='')
            cursor.execute(ddl)

        cursor.close()

    def find_guest_from_badge(self, badge):
        c = self.cnx.cursor()
        c.execute('select * from guests where badge=?', (badge,))
        r = c.fetchone()
        if r is None:
            guest = Guest()
        else:
            guest = Guest(r)
        c.close()
        return guest

    def add_registration(self, badge_id, time, direction, auto_added=False):
        c = self.cnx.cursor()
        c.execute(self.ADD_REGISTRATION, (time, direction, auto_added, badge_id))
        self.cnx.commit()
        print("Registration added : {}, {}, {}, {}".format(badge_id, time, direction, auto_added))
        c.close()

    #offset_from_last : 0 (last item), -1 (item before last item), ...
    def get_registration(self, badge_id, offset_from_last=0):
        if offset_from_last > 0:
            #registration not found
            return Registration()
        c = self.cnx.cursor()
        c.execute('select * from registrations where badge_id=? order by time desc', (badge_id, ))
        lst = c.fetchmany(1 - offset_from_last)
        if not lst:
            #empty list, nothing found
            registration = Registration()
        else:
            try:
                registration = Registration(lst[0 - offset_from_last])
            except IndexError as e:
                #out of range
                registration = Registration()
        c.close()
        return registration

    def clear_registration(self, id):
        if id < 1:
            return
        c = self.cnx.cursor()
        try:
            c.execute('delete from registrations where id=?',(id, ))
        except sqlite3.Error as e:
            pass
        c.close()

    def close(self):
        self.cnx.close()
