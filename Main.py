import tkinter as tk
from tkinter import messagebox
import time, os
from datetime import datetime, date
from Database import FGR_DB, Guest
from Register import Register
from Guests import Guests
from Registrations import Registrations
from Export import Export
import locale

VERSION = 'V2.1'

#V1.1 : change badge to badge-code and and add badge-number and id.  Registrations point to guest-id
#V1.2 : added registrations, refactored code, updated table headers and content, bugfixes
#V2.0 : added export function.  Database is backed up when program is started.  Added icon.
#V2.1 : bugfix : guest subscription date was saved in wrong format

def write_slogan():
    print("Tkinter is easy to use!")

class FGR:
    class Mode:
        guest = 'GEBRUIKER'
        admin = 'BEHEERDER'


    def __init__(self, root=None):

        #initialize database
        self.database = FGR_DB()
        #{self.database.test_populate_database()

        #initialize register
        self.register = Register(root, self.database)

        #initialize Guests
        self.guests = Guests(root, self.database, self.child_window_closes)

        #initialize Registrations
        self.registrations = Registrations(root, self.database, self.child_window_closes)

        #initialize Export
        self.export = Export(root, self.database, self.child_window_closes)

        #initialize GUI
        self.root=root
        self.root_frm = tk.Frame(self.root)
        self.root_frm.grid()
        self.init_menu()
        self.init_widgets()

        #initialize mode
        self.mode = self.Mode.admin
        self.change_mode()

        #set the minimum size of the window
        root.update()
        root.minsize(root.winfo_width(), root.winfo_height())

    #change mode from guest to admin and vice verse
    def change_mode(self, force_mode=None):
        if force_mode:
            self.mode = force_mode
        elif self.mode == self.Mode.guest:
            self.mode = self.Mode.admin
        else:
            self.mode = self.Mode.guest

        if self.mode == self.Mode.admin:
            #change mode to admin
            self.main_mnu.entryconfig('Menu', state='normal')
            #self.mode_btn.configure(text='Gast')
            self.root_frm.winfo_toplevel().title("Fablab Gebruikers Registratie {} :: ADMIN MODE".format(VERSION))
        else:
            #change mode to guest
            self.main_mnu.entryconfig('Menu', state='disabled')
            #self.mode_btn.configure(text='Beheerder')
            self.root_frm.winfo_toplevel().title("Fablab Gebruikers Registratie {}".format(VERSION))
        #set focus to the badge entry
        self.badge_ent.focus()

    def get_mode(self):
        return self.mode

    def badge_entered(self, event):
        #check if the admin code is used.  If so, switch to admin mode
        if self.badge_ent.get() == '2500':
            self.change_mode(force_mode=self.Mode.admin)
        else:
            guest = self.database.find_guest_from_badge(self.badge_ent.get())
            if guest.found :
                direction = self.register.new_registration(guest)
                till_string = ''
                if direction == 'IN':
                    if guest.subscription_type == Guest.SUB_TYPE_SUBSCRIPTION:
                        print(type(guest.subscribed_from))
                        print(guest.subscribed_from, FGR_DB.add_years(guest.subscribed_from, 1))
                        delta = FGR_DB.add_years(guest.subscribed_from, 1) - date.today()
                        print(delta.days)
                        if delta.days < 0:
                            messagebox.showwarning('Abonnement is verlopen',
                                                   'Opgelet, uw abonnement is verlopen.\nVraag info aan een medewerker')
                        else:
                            till_string = ', abonnement is nog {} dagen geldig'.format(delta.days)
                    else:
                        guest.pay_as_you_go_left -= 1
                        if guest.pay_as_you_go_left < 0:
                            messagebox.showwarning('Beurtenkaart is verlopen',
                                                   'Opgelet, uw beurtenkaart is verlopen.\nVraag info aan een medewerker')
                        else:
                            till_string = ', er zijn nog {} geldige beurten'.format(guest.pay_as_you_go_left)
                        rslt = self.database.update_guest(guest.id, guest.badge_code,
                                                          guest.badge_number, guest.first_name,
                                                          guest.last_name,
                                                          guest.email, guest.phone,
                                                          guest.subscription_type,
                                                          guest.subscribed_from,
                                                          guest.pay_as_you_go_left, guest.pay_as_you_go_max)
                self.show_message("Hallo {}, u heb juist {} gebadged{}".format(guest.first_name, direction, till_string), 4000, 'green')
            else:
                self.show_message("U bent nog niet geregistreerd, gelieve hulp te vragen", 5000, "red")
        self.badge_ent.delete(0, tk.END)

    def update_time(self):
        self.time_lbl.configure(text=time.strftime('%d/%m/%Y %H:%M:%S'))
        root.after(1000, self.update_time)

    def clear_database(self):
        answer = tk.Message

    def init_menu(self):
        #menu
        self.main_mnu=tk.Menu()
        self.menu_mnu=tk.Menu()
        self.main_mnu.add_cascade(label="Menu", menu=self.menu_mnu)
        self.menu_mnu.add_command(label="Gasten", command=self.guests.show_guests_window)
        self.menu_mnu.add_command(label="Registraties", command=self.registrations.show_registrations_window)
        self.menu_mnu.add_command(label="Export", command=self.export.export_database)
        self.menu_mnu.add_separator()
        self.menu_mnu.add_command(label="Gast mode", command=self.change_mode)
        #self.menu_mnu.add_command(label="Wis", command=self.clear_database)
        self.root.configure(menu=self.main_mnu)

    def child_window_closes(self):
        self.change_mode(self.Mode.guest)


    def init_widgets(self):
        self.fr1_frm = tk.Frame(self.root_frm)
        self.fr1_frm.grid(row=0, column=0, sticky='W')

        tk.Label(self.root_frm, text = "Welkom bij het fablab\nGelieve uw badge aan te bieden", font=("Times New Roman", 60)).grid(row=1, columnspan=3)

        self.time_lbl = tk.Label(self.root_frm, text=time.strftime('%d/%m/%Y %H:%M:%S'), font=("Times New Roman", 60))
        self.time_lbl.grid(row=2, columnspan=3)
        self.update_time()

        tk.Label(self.root_frm, text = "", font=("Times New Roman", 30)).grid(columnspan=3, sticky='E')

        self.fr2_frm = tk.Frame(self.root_frm)
        self.fr2_frm.grid(columnspan=3, sticky='W')
        tk.Label(self.fr2_frm, text = "BADGE", font=("Times New Roman", 30)).pack(side='left')
        self.badge_ent = tk.Entry(self.fr2_frm, show='*', font=("Times New Roman", 30))
        self.badge_ent.pack(side='left')
        self.badge_ent.bind('<Return>', self.badge_entered)

        self.guest_welcome_lbl = tk.Label(self.root_frm, text ="", font=("Times New Roman", 20))
        self.guest_welcome_lbl.grid(columnspan=3, sticky='W')

        tk.Label(self.root_frm, text = "", font=("Times New Roman", 30)).grid(columnspan=3, sticky='E')


    def show_message(self, msg, time=2000, color='black'):
        def clear_msg():
            self.guest_welcome_lbl.config(text = '')
        #self.root_frm.focus()
        self.guest_welcome_lbl.config(text=msg, fg=color)
        self.root_frm.after(time, clear_msg)


if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, '')
    root = tk.Tk()
    root.iconbitmap(os.path.join(os.getcwd(), 'resources//fgr.ico'))
    fgr = FGR(root)
    root.mainloop()
