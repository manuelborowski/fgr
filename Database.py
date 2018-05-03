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
    def __init__(self):
        self.cnx = sqlite3.connect(self.DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.cnx.row_factory = sqlite3.Row
        self.csr = self.cnx.cursor()

        #create tables, if they do not exist yet
        for name, ddl in self.TABLES.items():
            print("Creating table {}: ".format(name), end='')
            self.csr.execute(ddl)

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
        "  badge_id TEXT NOT NULL REFERENCES guests (badge) ON DELETE CASCADE"
        ")")

    ADD_GUEST = ("INSERT INTO guests "
                 "(first_name, last_name, company, email, phone, badge)"
                 "VALUES (?, ?, ?, ?, ?, ?)")

    UPDATE_GUEST = ("UPDATE guests SET "
                    "first_name=?,"
                    "last_name=?,"
                    "company=?,"
                    "email=?,"
                    "phone=?"
                    "WHERE badge=?;")




    ADD_REGISTRATION =("INSERT INTO registrations "
                 "(time, direction, auto_added, badge_id)"
                 "VALUES (?, ?, ?, ?)")

    def test_populate_database(self):
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
            self.csr.execute(self.ADD_GUEST, i)

        for i in registrations:
            d = datetime.datetime.strptime(i[0], '%d/%m/%Y %H:%M:%S')
            self.csr.execute(self.ADD_REGISTRATION, (d,)+i[1])

        print('Database populated')
        self.cnx.commit()


    def find_guest_from_badge(self, badge):
        self.csr.execute('select * from guests where badge=?', (badge,))
        r = self.csr.fetchone()
        if r is None:
            guest = Guest()
        else:
            guest = Guest(r)
        return guest

    def find_guests(self, guest):
        qs = 'SELECT * FROM guests WHERE '
        added = False
        if guest.first_name:
            qs += 'first_name LIKE \'%{}%\''.format(guest.first_name)
            added = True
        if guest.last_name:
            if added:
                qs += ' AND '
            qs += 'last_name LIKE \'%{}%\''.format(guest.last_name)
            added = True

        if guest.company:
            if added:
                qs += ' AND '
            qs += 'company LIKE \'%{}%\''.format(guest.company)
            added = True

        if guest.email:
            if added:
                qs += ' AND '
            qs += 'email LIKE \'%{}%\''.format(guest.email)
            added = True

        if guest.phone:
            if added:
                qs += ' AND '
            qs += 'phone LIKE \'%{}%\''.format(guest.phone)
            added = True

        if guest.badge:
            if added:
                qs += ' AND '
            qs += 'badge LIKE \'%{}%\''.format(guest.badge)
            added = True

        print(qs)
        self.csr.execute(qs)
        r = self.csr.fetchall()
        l = []
        for i in r:
            l.append(Guest(i))
        return l


    def add_guest(self, badge, first_name, last_name, company, email, phone):
        rslt = True
        try:
            self.csr.execute(self.ADD_GUEST, (first_name, last_name, company, email, phone, badge))
        except sqlite3.Error as e:
            rslt = False
        self.cnx.commit()
        print("Guest added : {}, {}, {}, {}, {}, {}".format(first_name, last_name, company, email, phone, badge))
        return rslt


    def delete_guest(self, badge):
        rslt = True
        try:
            self.csr.execute('delete from guests where badge=?',(badge, ))
        except sqlite3.Error as e:
            rslt = False
        return rslt


    def update_guest(self, badge, first_name, last_name, company, email, phone):
        rslt = True
        try:
            self.csr.execute(self.UPDATE_GUEST,(first_name, last_name, company, email, phone, badge))
        except:
            rslt = False
        self.cnx.commit()
        return rslt


    def get_guests(self):
        self.csr.execute('select * from guests')
        r = self.csr.fetchall()
        l = []
        for i in r:
            l.append(Guest(i))
        return l

    def add_registration(self, badge_id, time, direction, auto_added=False):
        try:
            self.csr.execute(self.ADD_REGISTRATION, (time, direction, auto_added, badge_id))
        except sqlite3.Error as e:
            pass
        self.cnx.commit()
        print("Registration added : {}, {}, {}, {}".format(badge_id, time, direction, auto_added))


    #offset_from_last : 0 (last item), -1 (item before last item), ...
    def find_registration_from_badge(self, badge_id, offset_from_last=0):
        if offset_from_last > 0:
            #registration not found
            return Registration()
        self.csr.execute('select * from registrations where badge_id=? order by time desc', (badge_id, ))
        lst = self.csr.fetchmany(1 - offset_from_last)
        if not lst:
            #empty list, nothing found
            registration = Registration()
        else:
            try:
                registration = Registration(lst[0 - offset_from_last])
            except IndexError as e:
                #out of range
                registration = Registration()
        return registration


    def delete_registration(self, id):
        rslt = True
        if id < 1:
            return False
        try:
            self.csr.execute('delete from registrations where id=?',(id, ))
        except sqlite3.Error as e:
            rslt = False
        return rslt


    def close(self):
        self.cnx.close()
