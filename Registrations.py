import tkinter as tk
import datetime
from Database import FGR_DB
from Calendar import Datepicker

class Registrations:
    def __init__(self, root_window, database):
        self.root_window = root_window
        self.database = database

    def show_registrations_window(self):
        self.win = tk.Toplevel()
        self.win.wm_title("Registraties")


        #ROW 0
        tk.Label(self.win, text="Datum").grid(row=0, column=0)
        self.date_txt = tk.StringVar()
        Datepicker(self.win, datevar=self.date_txt, entrywidth=40, dateformat="%d %B %Y").grid(row=0, column=1)
        #tk.Entry(self.win, textvariable = self.date_txt, width=40).grid(row=0, column=1)
        tk.Label(self.win, text="Badge").grid(row=0, column=2)
        self.badge_txt = tk.StringVar()
        tk.Entry(self.win, textvariable = self.badge_txt, width=40).grid(row=0, column=3)

        #ROW 1
        tk.Label(self.win, text="In").grid(row=1, column=0)
        self.in_txt = tk.StringVar()
        tk.Entry(self.win, textvariable = self.in_txt, width=40).grid(row=1, column=1)
        tk.Label(self.win, text="Uit").grid(row=1, column=2)
        self.out_txt = tk.StringVar()
        tk.Entry(self.win, textvariable = self.out_txt, width=40).grid(row=1, column=3)

        #ROW 2
        tk.Label(self.win, text="Voornaam").grid(row=2, column=0)
        self.first_name_txt = tk.StringVar()
        tk.Entry(self.win, textvariable = self.first_name_txt, width=40).grid(row=2, column=1)
        tk.Label(self.win, text="Naam").grid(row=2, column=2)
        self.last_name_txt = tk.StringVar()
        tk.Entry(self.win, textvariable = self.last_name_txt, width=40).grid(row=2, column=3)

        #Row 3
        tk.Label(self.win, text='{0:<15}{1:<10}{2:<40}{3:<30}'.format('Datum/In', 'Uit', 'Naam', 'Badge'), font='TkFixedFont'). \
                grid(row=3, column=0, columnspan=4, sticky='w')
        #Row 2-
        self.list_lbx = tk.Listbox(self.win, height=30, width=95, font='TkFixedFont')
        self.list_lbx.grid(row=4, column=0, rowspan=30, columnspan=4)
        self.list_lbx.bind('<<ListboxSelect>>', self.get_selected_row)
        sb1_sb = tk.Scrollbar(self.win)
        sb1_sb.grid(row=4, column=4, rowspan=30)
        self.list_lbx.config(yscrollcommand=sb1_sb.set)
        sb1_sb.config(command=self.list_lbx.yview)

        #Row 1, Column 5
        tk.Button(self.win, text="Bewaar veranderingen", width=25, command=self.update_command).grid(row=1, column=5)
        tk.Button(self.win, text="Voeg reservatie toe", width=25, command=self.win.destroy).grid(row=2, column=5)
        tk.Button(self.win, text="Verwijder geselecteerde registratie", width=25, command=self.win.destroy).grid(row=3, column=5)
        tk.Button(self.win, text="Alle reservaties", width=25, command=self.win.destroy).grid(row=4, column=5)
        tk.Button(self.win, text="Sluit venster", width=25, command=self.win.destroy).grid(row=5, column=5)

        #ROW ?? : extra row to make it better fit the window
        self.msg_lb = tk.Label(self.win, text = "")
        self.msg_lb.grid(sticky='e', columnspan=3)

        self.show_registrations_list()

    def show_registrations_list(self):
        l = self.database.find_all_registrations_and_guests()
        ic = 0
        self.idx_to_badge=[]
        self.list_lbx.delete(0, 'end')
        new_date = datetime.date(2000, 1, 1)
        for i in l:
            date = i.time_in.date()
            if date != new_date:
                new_date = date
                self.list_lbx.insert('end', '{0:15.14}'.format(date.strftime('%d/%m/%Y')))
                self.idx_to_badge.append(None)
                ic += 1

            time_in = i.time_in.strftime('%H:%M')
            if i.time_out is not None:
                time_out = i.time_out.strftime('%H:%M')
            else:
                time_out='-'
            self.list_lbx.insert('end', '  {0:13.12}{1:10.9}{2:40.39}{3:30.29}'.format(time_in, time_out,
                                               i.guest.first_name + ' ' + i.guest.last_name, i.guest.badge))
            if i.time_out is None:
                self.list_lbx.itemconfig(ic, bg='orange')
            self.idx_to_badge.append(i.id)
            ic += 1

    def get_selected_row(self, event):
        try:
            idx = self.list_lbx.curselection()[0]
            print(idx, self.idx_to_badge[idx])
            if self.idx_to_badge[idx] == None: return #non valid entry
            r = self.database.find_registration_from_id(self.idx_to_badge[idx])
            if r.found:
                self.registration_id = r.id
                g = self.database.find_guest_from_badge(r.badge_id)
                if g.found:
                    self.clear_inputfields_command()
                    print(g.first_name)
                    self.badge_txt.set(g.badge)
                    self.first_name_txt.set(g.first_name)
                    self.last_name_txt.set(g.last_name)
                    self.date_txt.set(r.time_in.strftime('%d %B %Y'))
                    time_in = r.time_in.strftime('%H:%M')
                    if r.time_out is not None:
                        time_out = r.time_out.strftime('%H:%M')
                    else:
                        time_out = '-'
                    self.in_txt.set(time_in)
                    self.out_txt.set(time_out)
        except IndexError:
            pass

    def update_command(self):
        registration = self.database.find_registration_from_id(self.registration_id)
        if registration.found:
            time_in = FGR_DB.date_be2iso(self.date_txt.get()) + ' ' + self.in_txt.get() + ':00'
            time_out = FGR_DB.date_be2iso(self.date_txt.get()) + ' ' + self.out_txt.get() + ':00'
            rslt = self.database.update_registration(self.registration_id, time_in, time_out, self.badge_txt.get())
            if rslt:
                self.show_message('Registratie is aangepast', color='green')
            else:
                self.show_message('Kon de gegevens niet aanpassen, onbekende reden', color='red')
        else:
            self.show_message('Registratie niet gevonden, onbekende reden', color='red')
        self.show_registrations_list()


    def clear_inputfields_command(self):
        self.first_name_txt.set('')
        self.last_name_txt.set('')
        self.date_txt.set('')
        self.badge_txt.set('')
        self.in_txt.set('')
        self.out_txt.set('')

    def show_message(self, msg, time=2000, color='black'):
        def clear_msg():
            self.msg_lb.config(text = '')
        self.win.focus()
        self.msg_lb.config(text=msg, fg=color)
        self.root_window.after(time, clear_msg)

