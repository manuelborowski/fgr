import sqlite3
import datetime
import os
from shutil import copyfile

class Guest:
    SUB_TYPE_SUBSCRIPTION = 'subscription'
    SUB_TYPE_PAYG = 'payasyougo'

    def __init__(self, db_row=None):

        if db_row is None:
            self.found = False
            return
        self.found = True
        self.id = db_row['id']
        self.first_name = db_row['first_name']
        self.last_name = db_row['last_name']
        self.subscription_type = db_row['subscription_type']
        self.subscribed_from = db_row['subscribed_from']
        self.pay_as_you_go_left = db_row['pay_as_you_go_left']
        if not self.pay_as_you_go_left: self.pay_as_you_go_left=0
        self.pay_as_you_go_max = db_row['pay_as_you_go_max']
        if not self.pay_as_you_go_max: self.pay_as_you_go_max=0
        self.email = db_row['email']
        self.phone = db_row['phone']
        self.badge_code = db_row['badge_code']
        self.badge_number = db_row['badge_number']

class Registration:
    def __init__(self, db_row=None):
        if db_row is None:
            self.found = False
            return
        self.found = True
        self.id = db_row['id']
        self.time_in = db_row['time_in']
        self.time_out = db_row['time_out']
        self.guest_id = db_row['guest_id']
        if 'first_name' in db_row.keys():
            self.guest = Guest(db_row)


class FGR_DB :
    def __init__(self):
        self.cnx = sqlite3.connect(self.DB_DEST, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.cnx.row_factory = sqlite3.Row
        self.csr = self.cnx.cursor()

        #create tables, if they do not exist yet
        for name, ddl in self.TABLES.items():
            print("Creating table {}: ".format(name), end='')
            self.csr.execute(ddl)

        #make e backup
        self.backup_database()

    def date_be2iso(be_date):
        try:
            month_dutch2number = {'januari' : '01', 'februari' : '02', 'maart' : '03', 'april' : '04',
                                  'mei' : '05', 'juni' : '06', 'juli' : '07', 'augustus' : '08', 'september' : '09',
                                  'october' : '10', 'november' : '11', 'december' : '12'}
            l = be_date.split(' ')[::-1]
            l[1] = str(month_dutch2number[l[1]])
            return '-'.join(l)
        except:
            return None

    def add_years_string(be_date, add_year):
        try:
            l = be_date.split(' ')
            l[2] = str(int(l[2]) + add_year)
            return ' '.join(l)
        except:
            return ''

    def add_years(d, years):
        try:
            # Return same day of the current year
            return d.replace(year=d.year + years)
        except ValueError:
            # If not same day, it will return other, i.e.  February 29 to March 1 etc.
            return d + (datetime.date(d.year + years, 1, 1) - datetime.date(d.year, 1, 1))

    DB_FILE = 'fgr.db'
    DB_LOCATION = 'resources'
    DB_DEST = os.path.join(DB_LOCATION, DB_FILE)
    DB_BACKUP_LOCATION = os.path.join(DB_LOCATION, 'backup')

    TABLES = {}
    TABLES['guests'] = (
        "CREATE TABLE IF NOT EXISTS guests ("
        "  id INTEGER PRIMARY KEY UNIQUE NOT NULL,"
        "  badge_number TEXT,"
        "  badge_code TEXT UNIQUE NOT NULL,"
        "  first_name TEXT,"
        "  last_name TEXT,"
        "  email TEXT,"
        "  phone TEXT,"
        "  subscription_type TEXT,"
        "  subscribed_from DATE,"
        "  pay_as_you_go_left INT,"
        "  pay_as_you_go_max INT"
        ")")

    ADD_GUEST = ("INSERT INTO guests "
                 "(badge_code, badge_number, first_name, last_name,  email, phone, subscription_type, subscribed_from, pay_as_you_go_left, pay_as_you_go_max)"
                 "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")

    UPDATE_GUEST = ("UPDATE guests SET "
                    "badge_code=?,"
                    "badge_number=?,"
                    "first_name=?,"
                    "last_name=?,"
                    "email=?,"
                    "phone=?,"
                    "subscription_type=?,"
                    "subscribed_from=?,"
                    "pay_as_you_go_left=?,"
                    "pay_as_you_go_max=?"
                    "WHERE id=?;")


    TABLES['registrations'] = (
        "CREATE TABLE IF NOT EXISTS registrations ("
        "  id INTEGER PRIMARY KEY UNIQUE NOT NULL,"
        "  'time_in' timestamp,"
        "  'time_out' timestamp,"
        "  guest_id INTEGER NOT NULL REFERENCES guests (id) ON DELETE CASCADE"
        ")")

    ADD_REGISTRATION =("INSERT INTO registrations "
                 "(time_in, time_out, guest_id) VALUES (?, ?, ?)")

    UPDATE_REGISTRATION = ("UPDATE registrations SET time_in=?, time_out=?, guest_id=? WHERE id=?;")

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


    def find_guest(self, id):
        self.csr.execute('SELECT * FROM guests WHERE id=?', (id,))
        r = self.csr.fetchone()
        return Guest(r)

    def find_guest_from_badge(self, badge_code):
        self.csr.execute('SELECT * FROM guests WHERE badge_code=?', (badge_code,))
        r = self.csr.fetchone()
        return Guest(r)

    def get_guests(self):
        self.csr.execute('SELECT * FROM guests ORDER BY last_name, first_name')
        r = self.csr.fetchall()
        l = []
        for i in r:
            l.append(Guest(i))
        return l

    def find_guests_from_keywords(self, guest):
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

        if guest.badge_code:
            if added:
                qs += ' AND '
            qs += 'badge_code LIKE \'%{}%\''.format(guest.badge_code)
            added = True

        if guest.badge_number:
            if added:
                qs += ' AND '
            qs += 'badge_number LIKE \'%{}%\''.format(guest.badge_number)
            added = True

        print(qs)
        self.csr.execute(qs)
        l = []
        r = self.csr.fetchall()
        for i in r:
            l.append(Guest(i))
        return l


    def add_guest(self, badge_code, badge_number, first_name, last_name, email, phone, sub_type, subed_from, payg_left, payg_max):
        rslt = True
        try:
            self.csr.execute(self.ADD_GUEST, (badge_code, badge_number, first_name, last_name, email, phone, sub_type, subed_from, payg_left, payg_max))
        except sqlite3.Error as e:
            rslt = False
        self.cnx.commit()
        print("Guest added : {}, {}, {}, {}, {}, {}".format(first_name, last_name, email, phone, badge_number, sub_type))
        return rslt


    def delete_guest(self, id):
        rslt = True
        try:
            self.csr.execute('DELETE FROM guests WHERE id=?',(id, ))
        except sqlite3.Error as e:
            rslt = False
        self.cnx.commit()
        return rslt


    def update_guest(self, id, badge_code, badge_number, first_name, last_name, email, phone, sub_type, subed_from, payg_left, payg_max):
        rslt = True
        try:
            self.csr.execute(self.UPDATE_GUEST, (badge_code, badge_number, first_name, last_name, email, phone, sub_type, subed_from, payg_left, payg_max, id))
        except:
            rslt = False
        self.cnx.commit()
        return rslt

    def check_registration_time_format(self, time_string):
        try:
            dt = datetime.datetime.strptime(time_string, '%Y-%m-%d %H:%M:%S')
            return True
        except Exception as e:
            return False

    def add_registration(self, guest_id, time_in, time_out=None):
        rslt = True
        try:
            time_in.replace(microsecond=0)
            if time_out:
                time_out.replace(microsecond=0)
            self.csr.execute(self.ADD_REGISTRATION, (time_in, time_out, guest_id))
        except sqlite3.Error as e:
            rslt = False
        self.cnx.commit()
        print("Registration added : {}, {}".format(guest_id, time_in))
        return rslt

    def update_registration(self, id, guest_id, time_in, time_out):
        rslt = True
        try:
            self.csr.execute(self.UPDATE_REGISTRATION, (time_in, time_out, guest_id, id))
        except:
            rslt = False
        self.cnx.commit()
        return rslt

    def find_last_registration_from_guest(self, guest_id):
        l = self.find_registrations_from_guest(guest_id)
        if l:
            r = l[0] #newest registration
        else:
            r = Registration()
        return r


    def find_registrations_from_guest(self, guest_id):
        self.csr.execute('select * FROM registrations WHERE guest_id=? ORDER BY time_in DESC', (guest_id,))
        db_lst = self.csr.fetchall()
        lst = []
        for i in db_lst:
            lst.append(Registration(i))
        return lst


    def find_registration(self, id):
        self.csr.execute('SELECT * FROM registrations WHERE id=?', (id,))
        r = self.csr.fetchone()
        return  Registration(r)


    def get_registrations_and_guests(self, return_db_rows=False):
        raw_select = self.csr.execute('SELECT * FROM registrations JOIN guests ON registrations.guest_id = guests.id ORDER BY time_in DESC')
        if return_db_rows: return raw_select
        db_lst = self.csr.fetchall()
        lst = []
        for i in db_lst:
            lst.append(Registration(i))
        return lst


    def delete_registration(self, id):
        rslt = True
        try:
            self.csr.execute('DELETE FROM registrations WHERE id=?',(id, ))
        except sqlite3.Error as e:
            rslt = False
        self.cnx.commit()
        return rslt


    def close(self):
        self.cnx.close()

    def backup_database(self):
        try:
            absolute_backup_path = os.path.join(os.getcwd(), self.DB_BACKUP_LOCATION)
            if not os.path.isdir(absolute_backup_path):
                os.mkdir(absolute_backup_path)
            backup_dest = os.path.join(self.DB_BACKUP_LOCATION, datetime.datetime.now().strftime('%Y%m%d%H%M%S') + ' ' + self.DB_FILE )
            copyfile(self.DB_DEST, backup_dest)
        except:
            print("Could not backup database")
