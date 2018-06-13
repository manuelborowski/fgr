import tkinter as tk
from tkinter import messagebox
from Database import Guest, FGR_DB
from Calendar import Datepicker
import datetime

class Show_registrations:
    def __init__(self, root_window, database):
        self.root_window = root_window
        self.database = database

    def show_registrations_window(self, guest_id):
        self.win = tk.Tk()
        self.win.wm_title('Registraties')

        guest = self.database.find_guest(guest_id)
        if guest.found:
            t = 'Registraties voor : {} {}'.format(guest.first_name, guest.last_name)
        else:
            t = 'Gast niet gevonden, probeer opnieuw'
        #Row 0
        tk.Label(self.win, text=t).grid(row=0, column=0, columnspan=4, sticky='w'
                                                                              '')
        #Row 1
        tk.Label(self.win, text='{0:<15}{1:<10}{2:<10}'.format('Datum', 'IN', 'UIT'), font='TkFixedFont'). \
                grid(row=1, column=0, columnspan=4, sticky='w')

        #ROW 2
        self.list_lbx = tk.Listbox(self.win, height=20, width=35, font='TkFixedFont')
        self.list_lbx.grid(row=2, column=0, rowspan=20, columnspan=4)
        #self.list_lbx.bind('<<ListboxSelect>>', self.get_selected_row)
        sb1_sb = tk.Scrollbar(self.win)
        sb1_sb.grid(row=2, column=4, rowspan=20)
        self.list_lbx.config(yscrollcommand=sb1_sb.set)
        sb1_sb.config(command=self.list_lbx.yview)

        #Row 0
        tk.Button(self.win, text="Sluit venster", width=25, command=self.win.destroy).grid(row=1, column=5)

        #set the minimum size of the window
        self.win.update()
        self.win.minsize(self.win.winfo_width(), self.win.winfo_height())

        l  = self.database.find_registrations_from_guest(guest_id)
        self.show_registrations_list(l)

    def show_registrations_list(self, list):
        ic = 0
        self.list_lbx.delete(0, 'end')
        for i in list:
            date = i.time_in.strftime('%d/%m/%Y')
            time_in = i.time_in.strftime('%H:%M')
            if i.time_out is not None:
                time_out = i.time_out.strftime('%H:%M')
            else:
                time_out='-'
            self.list_lbx.insert('end', '{0:15.14}{1:10.9}{2:10.9}'.format(date, time_in, time_out))
            if i.time_out is None:
                self.list_lbx.itemconfig(ic, bg='orange')
            ic += 1


class Guests:
    def __init__(self, root_window, database, close_cb):
        self.root_window = root_window
        self.database = database
        self.close_cb = close_cb
        self.registrations_window = Show_registrations(root_window, database)


    def show_guests_window(self):
        self.win = tk.Toplevel()
        self.win.wm_title("Gasten")

        #ROW 0
        tk.Label(self.win, text="Voornaam").grid(row=0, column=0)
        self.first_name_txt = tk.StringVar()
        tk.Entry(self.win, textvariable = self.first_name_txt, width=40).grid(row=0, column=1)
        tk.Label(self.win, text="Naam").grid(row=0, column=2)
        self.last_name_txt = tk.StringVar()
        tk.Entry(self.win, textvariable = self.last_name_txt, width=40).grid(row=0, column=3)

        #Row 1
        tk.Label(self.win, text="E-mail").grid(row=1, column=0)
        self.email_txt = tk.StringVar()
        tk.Entry(self.win, textvariable = self.email_txt, width=40).grid(row=1, column=1)
        tk.Label(self.win, text="Telefoon").grid(row=1, column=2)
        self.phone_txt = tk.StringVar()
        tk.Entry(self.win, textvariable = self.phone_txt, width=40).grid(row=1, column=3)

        #Row 2
        self.sub = []
        self.sub_type_txt = tk.StringVar()
        self.sub.append(tk.Radiobutton(self.win, text='Abonnement : van', variable=self.sub_type_txt, value=Guest.SUB_TYPE_SUBSCRIPTION,
                                       command = lambda : self.select_subscription_type(Guest.SUB_TYPE_SUBSCRIPTION)))
        self.sub[0].grid(row=2, column=0, sticky='w')
        self.sub_from_txt = tk.StringVar()
        self.sub.append(Datepicker(self.win, datevar = self.sub_from_txt, entrywidth=40, dateformat="%d %B %Y"))
        self.sub[1].grid(row=2, column=1)
        self.sub_from_txt.trace('w', self.sub_from_changed)
        self.sub.append(tk.Label(self.win, text="tot"))
        self.sub[2].grid(row=2, column=2)
        self.sub_till_txt = tk.StringVar()
        self.sub.append(tk.Entry(self.win, textvariable = self.sub_till_txt, width=40))
        self.sub[3].grid(row=2, column=3)

        #Row 3
        self.payg = []
        self.payg.append(tk.Radiobutton(self.win, text='Beurtenkaart : resterend', variable=self.sub_type_txt, value=Guest.SUB_TYPE_PAYG,
                                        command = lambda : self.select_subscription_type(Guest.SUB_TYPE_PAYG)))
        self.payg[0].grid(row=3, column=0, sticky='w')
        self.payg_left_txt = tk.StringVar()
        self.payg.append(tk.Entry(self.win, textvariable = self.payg_left_txt, width=40))
        self.payg[1].grid(row=3, column=1)
        self.payg.append(tk.Label(self.win, text="type"))
        self.payg[2].grid(row=3, column=2)
        self.payg_max_txt = tk.StringVar()
        self.payg.append(tk.Entry(self.win, textvariable = self.payg_max_txt, width=40))
        self.payg[3].grid(row=3, column=3)

        #Row 4
        tk.Label(self.win, text="Badge-code").grid(row=4, column=0)
        self.badge_code_txt = tk.StringVar()
        tk.Entry(self.win, textvariable = self.badge_code_txt, width=40).grid(row=4, column=1)
        tk.Label(self.win, text="Badge-nummer").grid(row=4, column=2)
        self.badge_number_txt = tk.StringVar()
        tk.Entry(self.win, textvariable = self.badge_number_txt, width=40).grid(row=4, column=3)


        #Row 5
        tk.Label(self.win, text='{0:<20}{1:<20}{2:<15}{3:<15}{4:<10}'.format('Naam', 'Voornaam', 'Abon/Beurten', 'Code', 'Nummer'), font='TkFixedFont'). \
                grid(row=5, column=0, columnspan=4, sticky='w')

        #ROW 6
        self.list_lbx = tk.Listbox(self.win, height=20, width=100, font='TkFixedFont')
        self.list_lbx.grid(row=6, column=0, rowspan=20, columnspan=4)
        self.list_lbx.bind('<<ListboxSelect>>', self.get_selected_row)
        sb1_sb = tk.Scrollbar(self.win)
        sb1_sb.grid(row=6, column=4, rowspan=20)
        self.list_lbx.config(yscrollcommand=sb1_sb.set)
        sb1_sb.config(command=self.list_lbx.yview)

        #Row 0-6, Column 5
        tk.Button(self.win, text="Zoek gast", width=25, command=self.search_guest_command).grid(row=0, column=5)
        tk.Button(self.win, text="Voeg gast toe", width=25, command=self.add_guest_command).grid(row=2, column=5)
        tk.Button(self.win, text="Bewaar veranderingen", width=25, command=self.update_guest_command).grid(row=3, column=5)
        tk.Button(self.win, text="Verwijder geselecteerde gast", width=25, command=self.delete_guest_command).grid(row=4, column=5)
        tk.Button(self.win, text="Toon registraties", width=25, command=self.show_registrations_list_command).grid(row=6, column=5)
        tk.Button(self.win, text="Wis velden", width=25, command=self.clear_inputfields_command).grid(row=8, column=5)
        tk.Button(self.win, text="Alle gasten", width=25, command=self.show_guest_list_command).grid(row=10, column=5)
        tk.Button(self.win, text="Sluit venster", width=25, command=self.close_window_command).grid(row=12, column=5)

        #ROW ?? : extra row to make it better fit the window
        self.msg_lb = tk.Label(self.win, text = "")
        self.msg_lb.grid(sticky='e', columnspan=3)

        #set the minimum size of the window
        self.win.update()
        self.win.minsize(self.win.winfo_width(), self.win.winfo_height())

        self.show_guest_list_command()

    def close_window_command(self):
        self.close_cb()
        self.win.destroy()

    def sub_from_changed(self, index, value, op):
        self.sub_till_txt.set(FGR_DB.add_years_string(self.sub_from_txt.get(), 1))

    def show_message(self, msg, time=2000, color='black'):
        def clear_msg():
            self.msg_lb.config(text = '')
        self.win.focus()
        self.msg_lb.config(text=msg, fg=color)
        self.root_window.after(time, clear_msg)

    def get_selected_row(self, event):
        try:
            idx = self.list_lbx.curselection()[0]
            print(idx, self.idx_to_id[idx])
            guest = self.database.find_guest(self.idx_to_id[idx])
            self.clear_inputfields_command()
            if guest.found:
                print(guest.first_name)
                self.guest_id = guest.id
                self.badge_code_txt.set(guest.badge_code)
                self.badge_number_txt.set(guest.badge_number)
                self.first_name_txt.set(guest.first_name)
                self.last_name_txt.set(guest.last_name)
                self.email_txt.set(guest.email)
                self.phone_txt.set(guest.phone)
                self.sub_type_txt.set(guest.subscription_type)
                self.select_subscription_type(guest.subscription_type)
                if guest.subscription_type == Guest.SUB_TYPE_SUBSCRIPTION:
                    self.sub_from_txt.set(guest.subscribed_from.strftime('%d %B %Y'))
                    #self.sub_till_txt.set(FGR_DB.date_be_add_year(self.sub_from_txt.get(), 1))
                    self.sub_till_txt.set(FGR_DB.add_years(guest.subscribed_from, 1).strftime('%d %B %Y'))
                else:
                    self.payg_left_txt.set(guest.pay_as_you_go_left)
                    self.payg_max_txt.set(guest.pay_as_you_go_max)
        except IndexError:
            pass

    def show_registrations_list_command(self):
        self.registrations_window.show_registrations_window(self.guest_id)

    def show_guest_list_command(self, list=None):
        if not list:
            list = self.database.get_guests()
        self.list_lbx.delete(0, 'end')
        self.idx_to_id = []
        for i in list:
            if i.subscription_type == Guest.SUB_TYPE_SUBSCRIPTION:
                sub_info = i.subscribed_from.strftime('%d %B %Y')
            else:
                sub_info = str(i.pay_as_you_go_left)
            self.list_lbx.insert('end', '{0:20.19}{1:20.19}{2:15.14}{3:15.14}{4:10.9}'. \
                                 format(i.last_name, i.first_name, sub_info, i.badge_code, i.badge_number))
            self.idx_to_id.append(i.id)

    def search_guest_command(self):
        if self.first_name_txt.get():
            print(self.first_name_txt.get())
        else:
            print('niks')
        g = Guest()
        g.first_name = self.first_name_txt.get()
        g.last_name = self.last_name_txt.get()
        g.email = self.email_txt.get()
        g.phone = self.phone_txt.get()
        g.badge_code = self.badge_code_txt.get()
        g.badge_number = self.badge_number_txt.get()
        guest_list = self.database.find_guests_from_keywords(g)
        self.show_guest_list_command(guest_list)


    def add_guest_command(self):
        badge_code = self.badge_code_txt.get()
        guest = self.database.find_guest_from_badge(badge_code)
        if guest.found:
            self.show_message('Opgepast, een gast met die badge bestaat al', color='red')
        else:
            if self.sub_type_txt.get() == '':
                self.sub_type_txt.set(Guest.SUB_TYPE_SUBSCRIPTION)
                self.sub_from_txt.set(datetime.date.today())
            rslt = self.database.add_guest(badge_code, self.badge_number_txt.get(), self.first_name_txt.get(), self.last_name_txt.get(),
                                           self.email_txt.get(), self.phone_txt.get(), self.sub_type_txt.get(),
                                           self.sub_from_txt.get(), self.payg_left_txt.get(), self.payg_max_txt.get())
            if rslt:
                self.show_message('Gast is toegevoegd', color='green')
            else:
                self.show_message('Kon de gast niet toevoegen, onbekende reden', color='red')
        self.clear_inputfields_command()
        self.show_guest_list_command()


    def update_guest_command(self):
        guest = self.database.find_guest(self.guest_id)
        if guest.found:
            rslt = self.database.update_guest(self.guest_id, self.badge_code_txt.get(), self.badge_number_txt.get(), self.first_name_txt.get(), self.last_name_txt.get(),
                                              self.email_txt.get(), self.phone_txt.get(), self.sub_type_txt.get(),
                                              FGR_DB.date_be2iso(self.sub_from_txt.get()), self.payg_left_txt.get(), self.payg_max_txt.get())
            if rslt:
                self.show_message('Gast is aangepast', color='green')
            else:
                self.show_message('Kon de gegevens niet aanpassen, onbekende reden', color='red')
        else:
            self.show_message('Gast niet gevonden, is de badge code juist?', color='red')
        self.clear_inputfields_command()
        self.show_guest_list_command()

    def delete_guest_command(self):
        rslt = messagebox.askyesno('Verwijder gast', 'Als u de gast verwijderd, dan worden alle registraties van die gast ook verwijderd!' \
                                   '\n\nWilt u verder gaan?')
        if rslt == False:
            self.show_message('Geannuleerd', color='green')
        else:
            guest = self.database.find_guest(self.guest_id)
            if guest.found:
                rslt = self.database.delete_guest(self.guest_id)
                if rslt:
                    self.show_message('Gast is verwijderd', color='green')
                else:
                    self.show_message('Kon de gast niet verwijderen, onbekende reden', color='red')
            else:
                self.show_message('Gast niet gevonden, is de badge code juist?', color='red')
        self.show_guest_list_command()
        self.clear_inputfields_command()

    def clear_inputfields_command(self):
        self.first_name_txt.set('')
        self.last_name_txt.set('')
        self.email_txt.set('')
        self.phone_txt.set('')
        self.badge_code_txt.set('')
        self.badge_number_txt.set('')
        self.sub_from_txt.set('')
        self.sub_till_txt.set('')
        self.payg_max_txt.set('')
        self.payg_left_txt.set('')
        self.sub_type_txt.set('')

    def select_subscription_type(self, type):
        if type == Guest.SUB_TYPE_SUBSCRIPTION:
            self.sub[1].config(state='normal')
            self.sub[2].config(state='normal')
            self.sub[3].config(state='normal')
            self.payg[1].config(state='disabled')
            self.payg[2].config(state='disabled')
            self.payg[3].config(state='disabled')
        else:
            self.sub[1].config(state='disabled')
            self.sub[2].config(state='disabled')
            self.sub[3].config(state='disabled')
            self.payg[1].config(state='normal')
            self.payg[2].config(state='normal')
            self.payg[3].config(state='normal')
