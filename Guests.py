import tkinter as tk
from tkinter import messagebox
from Database import Guest

class Guests:
    def __init__(self, root_window, database):
        self.root_window = root_window
        self.database = database

    def show_guests_window(self):
        # beep and show a screen to chose between IN or OUT
        self.win = tk.Toplevel()
        self.win.wm_title("Gasten")

        #ROW 0-2
        tk.Label(self.win, text="Voornaam").grid(row=0, column=0)
        tk.Label(self.win, text="Naam").grid(row=0, column=2)
        tk.Label(self.win, text="Bedrijf").grid(row=1, column=0)
        tk.Label(self.win, text="E-mail").grid(row=1, column=2)
        tk.Label(self.win, text="Telefoon").grid(row=2, column=0)
        tk.Label(self.win, text="Badge").grid(row=2, column=2)


        self.first_name_txt = tk.StringVar()
        tk.Entry(self.win, textvariable = self.first_name_txt, width=40).grid(row=0, column=1)
        self.last_name_txt = tk.StringVar()
        tk.Entry(self.win, textvariable = self.last_name_txt, width=40).grid(row=0, column=3)
        self.company_txt = tk.StringVar()
        tk.Entry(self.win, textvariable = self.company_txt, width=40).grid(row=1, column=1)
        self.email_txt = tk.StringVar()
        tk.Entry(self.win, textvariable = self.email_txt, width=40).grid(row=1, column=3)
        self.phone_txt = tk.StringVar()
        tk.Entry(self.win, textvariable = self.phone_txt, width=40).grid(row=2, column=1)
        self.badge_txt = tk.StringVar()
        tk.Entry(self.win, textvariable = self.badge_txt, width=40).grid(row=2, column=3)

        tk.Button(self.win, text="Bewaar veranderingen", width=25, command=self.update_command).grid(row=0, column=5)
        tk.Button(self.win, text="Zoek gast", width=25, command=self.search_command).grid(row=1, column=5)
        tk.Button(self.win, text="Voeg gast toe", width=25, command=self.add_command).grid(row=2, column=5)
        tk.Button(self.win, text="Wis velden", width=25, command=self.clear_inputfields_command).grid(row=3, column=5)

        #ROW 3
        tk.Label(self.win, text='{0:<20}{1:<20}{2:<20}{3:<40}{4:<10}{5:<10}'.format('Voornaam', 'Naam', 'Bedrijf', 'E-mail', 'Telefoon', 'Badge'), font='TkFixedFont'). \
                grid(row=3, column=0, columnspan=4, sticky='w')

        #ROW 4
        self.list_lbx = tk.Listbox(self.win, height=20, width=120, font='TkFixedFont')
        self.list_lbx.grid(row=4, column=0, rowspan=20, columnspan=4)
        self.list_lbx.bind('<<ListboxSelect>>', self.get_selected_row)
        sb1_sb = tk.Scrollbar(self.win)
        sb1_sb.grid(row=4, column=4, rowspan=20)
        self.list_lbx.config(yscrollcommand=sb1_sb.set)
        sb1_sb.config(command=self.list_lbx.yview)

        #ROW 3, COLUMN 5
        tk.Button(self.win, text="Alle gasten", width=25, command=self.view_command).grid(row=6, column=5)
        tk.Button(self.win, text="Verwijder geselecteerde gast", width=25, command=self.delete_command).grid(row=7, column=5)
        tk.Button(self.win, text="Sluit venster", width=25, command=self.win.destroy).grid(row=8, column=5)

        #ROW ?? : extra row to make it better fit the window
        self.msg_lb = tk.Label(self.win, text = "")
        self.msg_lb.grid(sticky='e', columnspan=3)

        self.view_command()

    def show_message(self, msg, time=2000, color='black'):
        def clear_msg():
            self.msg_lb.config(text = '')
        self.win.focus()
        self.msg_lb.config(text=msg, fg=color)
        self.root_window.after(time, clear_msg)

    def get_selected_row(self, event):
        try:
            idx = self.list_lbx.curselection()[0]
            print(idx, self.idx_to_badge[idx])
            guest = self.database.find_guest_from_badge(self.idx_to_badge[idx])
            if guest.found:
                print(guest.first_name)
                self.first_name_txt.set(guest.first_name)
                self.last_name_txt.set(guest.last_name)
                self.company_txt.set(guest.company)
                self.email_txt.set(guest.email)
                self.phone_txt.set(guest.phone)
                self.badge_txt.set(guest.badge)
        except IndexError:
            pass

    def show_guest_list(self, list):
        self.list_lbx.delete(0, 'end')
        self.idx_to_badge = []
        for i in list:
            print(i.first_name)
            self.list_lbx.insert('end', '{0:20.19}{1:20.19}{2:20.19}{3:40.39}{4:10.9}{5:10.9}'. \
                                 format(i.first_name, i.last_name, i.company, i.email, i.phone, i.badge))
            self.idx_to_badge.append(i.badge)

    def view_command(self):
        guest_list = self.database.get_guests()
        self.show_guest_list(guest_list)

    def search_command(self):
        if self.first_name_txt.get():
            print(self.first_name_txt.get())
        else:
            print('niks')
        g = Guest()
        g.first_name = self.first_name_txt.get()
        g.last_name = self.last_name_txt.get()
        g.company  = self.company_txt.get()
        g.email = self.email_txt.get()
        g.phone = self.phone_txt.get()
        g.badge = self.badge_txt.get()
        guest_list = self.database.find_guests(g)
        self.show_guest_list(guest_list)


    def add_command(self):
        badge = self.badge_txt.get()
        guest = self.database.find_guest_from_badge(badge)
        if guest.found:
            self.show_message('Opgepast, een gast met die badge bestaat al', color='red')
        else:
            rslt = self.database.add_guest(badge, self.first_name_txt.get(), self.last_name_txt.get(),
                                           self.company_txt.get(), self.email_txt.get(), self.phone_txt.get())
            if rslt:
                self.show_message('Gast is toegevoegd', color='green')
            else:
                self.show_message('Kon de gast niet toevoegen, onbekende reden', color='red')
        self.view_command()


    def update_command(self):
        badge = self.badge_txt.get()
        guest = self.database.find_guest_from_badge(badge)
        if guest.found:
            rslt = self.database.update_guest(badge, self.first_name_txt.get(), self.last_name_txt.get(),
                                          self.company_txt.get(), self.email_txt.get(), self.phone_txt.get())
            if rslt:
                self.show_message('Gast is aangepast', color='green')
            else:
                self.show_message('Kon de gegevens niet aanpassen, onbekende reden', color='red')
        else:
            self.show_message('Gast niet gevonden, is de badge code juist?', color='red')
        self.view_command()

    def delete_command(self):
        rslt = messagebox.askyesno('Verwijder gast', 'Als u de gast verwijderd, dan worden alle registraties van die gast ook verwijderd!' \
                                   '\n\nWilt u verder gaan?')
        self
        if rslt == False:
            self.show_message('Geannuleerd', color='green')
        else:
            badge = self.badge_txt.get()
            guest = self.database.find_guest_from_badge(badge)
            if guest.found:
                rslt = self.database.delete_guest(badge)
                if rslt:
                    self.show_message('Gast is verwijderd', color='green')
                else:
                    self.show_message('Kon de gast niet verwijderen, onbekende reden', color='red')
            else:
                self.show_message('Gast niet gevonden, is de badge code juist?', color='red')
        self.view_command()

    def clear_inputfields_command(self):
        self.first_name_txt.set('')
        self.last_name_txt.set('')
        self.company_txt.set('')
        self.email_txt.set('')
        self.phone_txt.set('')
        self.badge_txt.set('')


