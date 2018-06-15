import tkinter as tk
import winsound
import datetime

class Register:
    def __init__(self, root_window, database):
        self.root_window = root_window
        self.database = database

    def new_registration(self, guest):
        now = datetime.datetime.now().replace(microsecond=0)
        print(now.date())
        registration_last = self.database.find_last_registration_from_guest(guest.id)
        direction = 'IN'
        if not registration_last.found:
            #no registrations yet
            print('First registration')
            self.database.add_registration(guest.id, now)
        elif registration_last.time_in.date() == now.date():
            print('Registering OUT')
            self.database.update_registration(registration_last.id, guest.id, registration_last.time_in, now)
            direction = 'UIT'
        else:
            print('Registering IN')
            self.database.add_registration(guest.id, now)
        return direction
