import tkinter as tk
import winsound
import datetime
import logging

class Register:
    def __init__(self, root_window, database, log_handle):
        self.root_window = root_window
        self.database = database
        self.log = logging.getLogger('{}.Register'.format(log_handle))


    def new_registration(self, guest):
        now = datetime.datetime.now().replace(microsecond=0)
        self.log.info(now.date())
        registration_last = self.database.find_last_registration_from_guest(guest.id)
        direction = 'IN'
        if not registration_last.found:
            #no registrations yet
            self.log.info('First registration')
            self.database.add_registration(guest.id, now)
        elif registration_last.time_in.date() == now.date():
            self.log.info('Registering OUT')
            self.database.update_registration(registration_last.id, guest.id, registration_last.time_in, now)
            direction = 'UIT'
        else:
            self.log.info('Registering IN')
            self.database.add_registration(guest.id, now)
        return direction
