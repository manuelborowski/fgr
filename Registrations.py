import tkinter as tk
from tkinter import messagebox
import datetime
from Database import FGR_DB, Guest
from Calendar import Datepicker

class Registrations:
    def __init__(self, root_window, database, close_cb):
        self.root_window = root_window
        self.database = database
        self.close_cb = close_cb
        self.guest_name_to_id = {}

    def show_registrations_window(self):
        self.win = tk.Toplevel()
        self.win.wm_title("Registraties")

        #ROW 0
        tk.Label(self.win, text="Datum").grid(row=0, column=0)
        self.date_txt = tk.StringVar()
        Datepicker(self.win, datevar=self.date_txt, entrywidth=40, dateformat="%d %B %Y").grid(row=0, column=1)
        #tk.Entry(self.win, textvariable = self.date_txt, width=40).grid(row=0, column=1)
        #tk.Label(self.win, text="Badge").grid(row=0, column=2)
        #self.badge_txt = tk.StringVar()
        #tk.Entry(self.win, textvariable = self.badge_txt, width=40).grid(row=0, column=3)

        #ROW 1
        tk.Label(self.win, text="In").grid(row=1, column=0)
        self.in_txt = tk.StringVar()
        tk.Entry(self.win, textvariable = self.in_txt, width=40).grid(row=1, column=1)
        tk.Label(self.win, text="Uit").grid(row=1, column=2)
        self.out_txt = tk.StringVar()
        tk.Entry(self.win, textvariable = self.out_txt, width=40).grid(row=1, column=3)

        #ROW 2
        tk.Label(self.win, text="Naam").grid(row=2, column=0)
        self.name_txt = tk.StringVar()
        self.name_txt.set('')
        self.guest_list = ['']
        self.name_om = tk.OptionMenu(self.win, self.name_txt, *self.guest_list)
        self.name_om.grid(row=2, column=1, sticky='w')

        #Row 3
        tk.Label(self.win, text='{0:<12}{1:<6}{2:<40}{3:15}{4:<25}'.format('Datum/In', 'Uit', 'Naam', 'Abon/Beurt', 'Badge-C/N'), font='TkFixedFont'). \
                grid(row=3, column=0, columnspan=4, sticky='w')
        #Row 2-
        self.list_lbx = tk.Listbox(self.win, height=20, width=95, font='TkFixedFont')
        self.list_lbx.grid(row=4, column=0, rowspan=20, columnspan=4, sticky='nesw')
        self.list_lbx.bind('<<ListboxSelect>>', self.get_selected_row)
        sb1_sb = tk.Scrollbar(self.win)
        sb1_sb.grid(row=4, column=4, rowspan=30, sticky='nesw')
        self.list_lbx.config(yscrollcommand=sb1_sb.set)
        sb1_sb.config(command=self.list_lbx.yview)

        #Row 1, Column 5
        tk.Button(self.win, text="Voeg reservatie toe", width=25, command=self.add_registration_command).grid(row=0, column=5)
        tk.Button(self.win, text="Bewaar veranderingen", width=25, command=self.update_command).grid(row=1, column=5)
        tk.Button(self.win, text="Verwijder geselecteerde registratie", width=25, command=self.delete_command).grid(row=2, column=5)
        tk.Button(self.win, text="Wis velden", width=25, command=self.clear_inputfields_command).grid(row=4, column=5)
        tk.Button(self.win, text="Alle reservaties", width=25, command=self.show_registrations_list).grid(row=6, column=5)
        tk.Button(self.win, text="Sluit venster", width=25, command=self.close_window_command).grid(row=8, column=5)

        #ROW ?? : extra row to make it better fit the window
        self.msg_lb = tk.Label(self.win, text = "")
        self.msg_lb.grid(sticky='e', columnspan=3)

        #set the minimum size of the window
        self.win.update()
        self.win.minsize(self.win.winfo_width(), self.win.winfo_height())

        self.clear_inputfields_command()
        self.show_registrations_list()

    def close_window_command(self):
        self.close_cb()
        self.win.destroy()


    def show_registrations_list(self):
        l = self.database.get_registrations_and_guests()
        ic = 0
        self.idx_to_id=[]
        self.list_lbx.delete(0, 'end')
        new_date = datetime.date(2000, 1, 1)
        for i in l:
            date = i.time_in.date()
            if date != new_date:
                new_date = date
                self.list_lbx.insert('end', '{0:15.14}'.format(date.strftime('%d/%m/%Y')))
                self.list_lbx.itemconfig(ic, bg='yellow')
                self.idx_to_id.append(None)
                ic += 1

            time_in = i.time_in.strftime('%H:%M')
            if i.time_out is not None:
                time_out = i.time_out.strftime('%H:%M')
            else:
                time_out='-'
            if i.guest.subscription_type == Guest.SUB_TYPE_SUBSCRIPTION:
                sub_info = i.guest.subscribed_from.strftime('%d %B %Y')
            else:
                sub_info = str(i.guest.pay_as_you_go_left)

            self.list_lbx.insert('end', '  {0:10.9}{1:6.5}{2:40.39}{3:15.14}{4:25.24}'.format(time_in, time_out,
                                               i.guest.first_name + ' ' + i.guest.last_name, sub_info, i.guest.badge_code + '/'+ i.guest.badge_number))
            if i.time_out is None:
                self.list_lbx.itemconfig(ic, bg='orange')
            self.idx_to_id.append(i.id)
            ic += 1

    def get_selected_row(self, event):
        try:
            idx = self.list_lbx.curselection()[0]
            print(idx, self.idx_to_id[idx])
            if self.idx_to_id[idx] == None: return #non valid entry
            r = self.database.find_registration(self.idx_to_id[idx])
            if r.found:
                g = self.database.find_guest(r.guest_id)
                if g.found:
                    self.clear_inputfields_command()
                    self.registration_id = r.id
                    print(g.first_name)
                    self.date_txt.set(r.time_in.strftime('%d %B %Y'))
                    time_in = r.time_in.strftime('%H:%M')
                    if r.time_out is not None:
                        time_out = r.time_out.strftime('%H:%M')
                    else:
                        time_out = '-'
                    self.in_txt.set(time_in)
                    self.out_txt.set(time_out)
                    self.update_name_widget()
        except IndexError:
            pass

    def add_registration_command(self):
        time_in = FGR_DB.date_be2iso(self.date_txt.get()) + ' ' + self.in_txt.get() + ':00'
        time_out = FGR_DB.date_be2iso(self.date_txt.get()) + ' ' + self.out_txt.get() + ':00'
        if not self.database.check_registration_time_format(time_in) or not self.database.check_registration_time_format(time_out):
            self.show_message('In- of Uit-tijd is niet correct', color='red')
        else:
            try:
                guest_id = self.guest_name_to_id[self.name_txt.get()]
            except:
                self.show_message('Gast is niet gevonden', color='red')
                return
            rslt = self.database.add_registration(guest_id, time_in, time_out)
            if rslt:
                self.show_message('Registratie is toegevoegd', color='green')
            else:
                self.show_message('Kon de registratie niet toevoegen, onbekende reden', color='red')
            self.show_registrations_list()
            self.clear_inputfields_command()


    def update_command(self):
        registration = self.database.find_registration(self.registration_id)
        if registration.found:
            time_in = FGR_DB.date_be2iso(self.date_txt.get()) + ' ' + self.in_txt.get() + ':00'
            time_out = FGR_DB.date_be2iso(self.date_txt.get()) + ' ' + self.out_txt.get() + ':00'
            if not self.database.check_registration_time_format(
                    time_in) or not self.database.check_registration_time_format(time_out):
                self.show_message('In- of Uit-tijd is niet correct')
            else:
                try:
                    guest_id = self.guest_name_to_id[self.name_txt.get()]
                except:
                    guest_id = registration.guest_id
                rslt = self.database.update_registration(self.registration_id, guest_id, time_in, time_out)
                if rslt:
                    self.show_message('Registratie is aangepast', color='green')
                else:
                    self.show_message('Kon de gegevens niet aanpassen, onbekende reden', color='red')
        else:
            self.show_message('Registratie niet gevonden, onbekende reden', color='red')
        self.show_registrations_list()
        self.clear_inputfields_command()


    def delete_command(self):
        rslt = messagebox.askyesno('Verwijder registratie', 'Wilt u verder gaan?')
        if rslt == False:
            self.show_message('Geannuleerd', color='green')
        else:
            registration = self.database.find_registration(self.registration_id)
            if registration.found:
                rslt = self.database.delete_registration(self.registration_id)
                if rslt:
                    self.show_message('Registratie is verwijderd', color='green')
                else:
                    self.show_message('Kon de registratie niet verwijderen, onbekende reden', color='red')
            else:
                self.show_message('Registratie niet gevonden, onbekende reden?', color='red')
        self.show_registrations_list()
        self.clear_inputfields_command()


    def clear_inputfields_command(self):
        self.name_txt.set('')
        self.date_txt.set('')
        self.in_txt.set('')
        self.out_txt.set('')
        self.registration_id = -1
        self.update_name_widget()


    def update_name_widget(self):
        #Get get guests list
        gl = self.database.get_guests()
        self.guest_list = []
        self.guest_name_to_id = {}
        menu = self.name_om['menu']
        menu.delete(0, 'end')
        for i in gl:
            name = '{} {}'.format(i.last_name, i.first_name)
            self.guest_list.append('{} {}'.format(i.last_name, i.first_name))
            self.guest_name_to_id[name] = i.id
            menu.add_command(label=name,
                             command=lambda value=name: self.name_txt.set(value))

        if self.registration_id > -1:
            r = self.database.find_registration(self.registration_id)
            if r.found:
                g = self.database.find_guest(r.guest_id)
                if g.found:
                    self.name_txt.set('{} {}'.format(g.last_name, g.first_name))


    def show_message(self, msg, time=3000, color='black'):
        def clear_msg():
            self.msg_lb.config(text = '')
        self.win.focus()
        self.msg_lb.config(text=msg, fg=color)
        self.root_window.after(time, clear_msg)

