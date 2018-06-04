import tkinter as tk
import time
from Database import FGR_DB
from Register import Register
from Guests import Guests
#from Registrations import Registrations
import locale

VERSION = 'V1.1'

#V1.1 : change badge to badge-code and and add badge-number and id.  Registrations point to guest-id

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
        #TODO self.registrations = Registrations(root, self.database)

        #initialize GUI
        self.root=root
        self.root_frm = tk.Frame(self.root)
        self.root_frm.grid()
        self.init_menu()
        self.init_widgets()

        #initialize mode
        self.mode = self.Mode.admin
        self.change_mode()

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
                direction = self.register.add_registration(guest)
                self.show_message("Hallo {}, u heb juist {} gebadged".format(guest.first_name, direction), 4000, 'green')
            else:
                self.show_message("U bent nog niet geregistreerd, gelieve hulp te vragen", 5000, "red")
        self.badge_ent.delete(0, tk.END)

    def update_time(self):
        self.time_lbl.configure(text=time.strftime('%d/%m/%Y %H:%M:%S'))
        root.after(1000, self.update_time)

    def add_guest(self):
        print('voeg een nieuwe gast toe')

    def clear_database(self):
        answer = tk.Message

    def init_menu(self):
        #menu
        self.main_mnu=tk.Menu()
        self.menu_mnu=tk.Menu()
        self.main_mnu.add_cascade(label="Menu", menu=self.menu_mnu)
        self.menu_mnu.add_command(label="Gasten", command=self.guests.show_guests_window)
        #TODO self.menu_mnu.add_command(label="Registraties", command=self.registrations.show_registrations_window)
        #self.menu_mnu.add_command(label="Instellingen", command=self.add_guest)
        #self.menu_mnu.add_command(label="Exporteer", command=self.add_guest)
        self.menu_mnu.add_separator()
        self.menu_mnu.add_command(label="Gast mode", command=self.change_mode)
        #self.menu_mnu.add_command(label="Wis", command=self.clear_database)
        self.root.configure(menu=self.main_mnu)

    def child_window_closes(self):
        self.change_mode(self.Mode.guest)


    def init_widgets(self):
        self.fr1_frm = tk.Frame(self.root_frm)
        self.fr1_frm.grid(row=0, column=0, sticky='W')
        #tk.Label(self.fr1_frm, text='paswoord').grid(row=0, column=0)
        #self.pwd_ent = tk.Entry(self.fr1_frm, show='*')
        #self.pwd_ent.grid(row=0, column=1)
        #self.mode_btn = tk.Button(self.fr1_frm, text='Beheerder', command=self.change_mode)
        #self.mode_btn.grid(row=0, column=2)

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

        self.guest_welcome_lbl = tk.Label(self.root_frm, text ="", font=("Times New Roman", 30))
        self.guest_welcome_lbl.grid(columnspan=3, sticky='W')

        tk.Label(self.root_frm, text = "", font=("Times New Roman", 30)).grid(columnspan=3, sticky='E')


    def show_message(self, msg, time=2000, color='black'):
        def clear_msg():
            self.guest_welcome_lbl.config(text = '')
        #self.root_frm.focus()
        self.guest_welcome_lbl.config(text=msg, fg=color)
        self.root_frm.after(time, clear_msg)


if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, 'nl-BE')
    root = tk.Tk()
    fgr = FGR(root)
    root.mainloop()