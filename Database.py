import sqlite3
import datetime

class Guest:
    SUB_TYPE_SUBSCRIPTION = 'subscription'
    SUB_TYPE_PAYG = 'payasyougo'

    def __init__(self, db_row=None):

        if db_row is None:
            self.found = False
            return
        self.found = True
        self.first_name = db_row['first_name']
        self.last_name = db_row['last_name']
        self.subscription_type = db_row['subscription_type']
        self.subscribed_from = db_row['subscribed_from']
        self.pay_as_you_go_left = db_row['pay_as_you_go_left']
        self.pay_as_you_go_max = db_row['pay_as_you_go_max']
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
        self.time_in = db_row['time_in']
        self.time_out = db_row['time_out']
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

    def date_be2iso(be_date):
        month_dutch2number = {'januari' : 1, 'februari' : 2, 'maart' : 3, 'april' : 4,
                              'mei' : 5, 'juni' : 6, 'juli' : 7, 'augustus' : 8, 'september' : 9,
                              'october' : 10, 'november' : 11, 'december' : 12}
        l = be_date.split(' ')[::-1]
        l[1] = str(month_dutch2number[l[1]])
        return '-'.join(l)

    def date_be_add_year(be_date, add_year):
        try:
            l = be_date.split(' ')
            l[2] = str(int(l[2]) + add_year)
            return ' '.join(l)
        except:
            return ''

    DB_NAME = 'resources/fgr.db'

    TABLES = {}
    TABLES['guests'] = (
        "CREATE TABLE IF NOT EXISTS guests ("
        "  badge TEXT PRIMARY KEY UNIQUE NOT NULL,"
        "  first_name TEXT,"
        "  last_name TEXT,"
        "  email TEXT,"
        "  phone TEXT,"
        "  subscription_type TEXT,"
        "  subscribed_from DATE,"
        "  pay_as_you_go_left INT,"
        "  pay_as_you_go_max INT"
        ")")

    TABLES['registrations'] = (
        "CREATE TABLE IF NOT EXISTS registrations ("
        "  id integer PRIMARY KEY,"
        "  'time_in' timestamp,"
        "  'time_out' timestamp,"
        "  badge_id TEXT NOT NULL REFERENCES guests (badge) ON DELETE CASCADE"
        ")")

    ADD_GUEST = ("INSERT INTO guests "
                 "(badge, first_name, last_name,  email, phone, subscription_type, subscribed_from, pay_as_you_go_left, pay_as_you_go_max)"
                 "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)")

    UPDATE_GUEST = ("UPDATE guests SET "
                    "first_name=?,"
                    "last_name=?,"
                    "email=?,"
                    "phone=?,"
                    "subscription_type=?,"
                    "subscribed_from=?,"
                    "pay_as_you_go_left=?,"
                    "pay_as_you_go_max=?"
                    "WHERE badge=?;")


    ADD_REGISTRATION =("INSERT INTO registrations "
                 "(time_in, time_out, badge_id)"
                 "VALUES (?, ?, ?)")

    UPDATE_REGISTRATION = ("UPDATE registrations SET "
                        "time_in=?, "
                        "time_out=?, "
                        "badge_id=? "
                        "WHERE id=?;")

    def test_populate_database(self):
        guests = [
            ('11', 'voornaam1', 'achternaam1', 'email1@test.be', '0311111', Guest.SUB_TYPE_SUBSCRIPTION, '2018-3-1', None, None),
            ('22', 'voornaam2', 'achternaam2', 'email2@test.be', '0322222', Guest.SUB_TYPE_PAYG, None, 3, 10),
        ]

        registrations = [
            ('2018-03-02 16:08:13', '2018-03-02 21:09:13', '11'),
            ('2018-03-05 16:10:16', '2018-03-05 21:09:13', '22'),
        ]
        for i in guests:
            self.csr.execute(self.ADD_GUEST, i)

        for i in registrations:
            self.csr.execute(self.ADD_REGISTRATION, i)

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


    def add_guest(self, badge, first_name, last_name, email, phone, sub_type, subed_from, payg_left, payg_max):
        rslt = True
        try:
            self.csr.execute(self.ADD_GUEST, (badge, first_name, last_name, email, phone, sub_type, subed_from, payg_left, payg_max))
        except sqlite3.Error as e:
            rslt = False
        self.cnx.commit()
        print("Guest added : {}, {}, {}, {}, {}, {}".format(first_name, last_name, email, phone, badge, sub_type))
        return rslt


    def delete_guest(self, badge):
        rslt = True
        try:
            self.csr.execute('delete from guests where badge=?',(badge, ))
        except sqlite3.Error as e:
            rslt = False
        return rslt


    def update_guest(self, badge, first_name, last_name, email, phone, sub_type, subed_from, payg_left, payg_max):
        rslt = True
        try:
            self.csr.execute(self.UPDATE_GUEST, (first_name, last_name, email, phone, sub_type, FGR_DB.date_be2iso(subed_from),
                                                        payg_left, payg_max, badge))
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

    def add_registration(self, badge_id, time_in):
        try:
            self.csr.execute(self.ADD_REGISTRATION, (time_in, None, badge_id))
        except sqlite3.Error as e:
            pass
        self.cnx.commit()
        print("Registration added : {}, {}".format(badge_id, time_in))

    def update_registration(self, id, badge_id, time_in, time_out):
        rslt = True
        try:
            self.csr.execute(self.UPDATE_REGISTRATION, (time_in, time_out, badge_id, id))
        except:
            rslt = False
        self.cnx.commit()
        return rslt



    #offset_from_last : 0 (last item), -1 (item before last item), ...
    def find_single_registration_from_badge(self, badge_id, offset_from_last=0):
        if offset_from_last > 0:
            #registration not found
            return Registration()
        self.csr.execute('select * from registrations where badge_id=? order by time_in desc', (badge_id, ))
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


    def find_registrations_from_badge(self, badge_id):
        self.csr.execute('select * from registrations where badge_id=? order by time_in desc', (badge_id, ))
        db_lst = self.csr.fetchall()
        lst = []
        for i in db_lst:
            lst.append(Registration(i))
        return lst


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
