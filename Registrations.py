import tkinter as tk
import datetime

class Registrations:
    def __init__(self, root_window, database):
        self.root_window = root_window
        self.database = database

    def show_registrations_window(self):
        self.win = tk.Toplevel()
        self.win.wm_title("Registraties")

        #Row 1
        tk.Label(self.win, text='{0:<15}{1:<10}{2:<40}{3:<30}'.format('Datum/In', 'Uit', 'Naam', 'Badge'), font='TkFixedFont'). \
                grid(row=1, column=0, columnspan=4, sticky='w')
        #Row 2-
        self.list_lbx = tk.Listbox(self.win, height=30, width=95, font='TkFixedFont')
        self.list_lbx.grid(row=2, column=0, rowspan=30, columnspan=4)
        #self.list_lbx.bind('<<ListboxSelect>>', self.get_selected_row)
        sb1_sb = tk.Scrollbar(self.win)
        sb1_sb.grid(row=2, column=4, rowspan=30)
        self.list_lbx.config(yscrollcommand=sb1_sb.set)
        sb1_sb.config(command=self.list_lbx.yview)

        #Row 1, Column 5
        tk.Button(self.win, text="Verwijder geselecteerde registratie", width=25, command=self.win.destroy).grid(row=1, column=5)
        tk.Button(self.win, text="Sluit venster", width=25, command=self.win.destroy).grid(row=2, column=5)

        #ROW ?? : extra row to make it better fit the window
        self.msg_lb = tk.Label(self.win, text = "")
        self.msg_lb.grid(sticky='e', columnspan=3)

        l = self.database.find_all_registrations_and_guests()
        ic = 0
        self.list_lbx.delete(0, 'end')
        new_date = datetime.date(2000, 1, 1)
        for i in l:
            date = i.time_in.date()
            if date != new_date:
                new_date = date
                self.list_lbx.insert('end', '{0:15.14}'.format(date.strftime('%d/%m/%Y')))
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
            ic += 1

