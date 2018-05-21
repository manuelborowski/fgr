import tkinter as tk
import winsound
import datetime

class Register:
    def __init__(self, root_window, database):
        self.root_window = root_window
        self.database = database

    def add_registration(self, guest):
        now = datetime.datetime.now()
        print(now.date())
        registration_last = self.database.find_single_registration_from_badge(guest.badge)
        direction = 'IN'
        if not registration_last.found:
            #no registrations yet
            print('First registration')
            self.database.add_registration(guest.badge, now)
        elif registration_last.time_in.date() == now.date():
            print('Registering OUT')
            self.database.update_registration(registration_last.id, guest.badge, registration_last.time_in, now)
            direction = 'UIT'
        else:
            print('Registering IN')
            self.database.add_registration(guest.badge, now)
        return direction


        #NOT USED : displayed a window with IN and OUT arrow that needed to be pushed
        def button_in_pushed():
            self.database.add_registration(guest.badge, 'IN', False)
            win.destroy()

        def button_out_pushed():
            self.database.add_registration(guest.badge, 'UIT', False)
            win.destroy()

        # beep and show a screen to chose between IN or OUT
        win = tk.Toplevel()
        win.wm_title("Window")

        l = tk.Label(win, text="komt u IN of gaat u UIT?  Klik op de juiste pijl aub", font=("Times New Roman", 30))
        l.grid(row=0, column=0, columnspan=2)

        self.left_out_img = tk.PhotoImage(file="resources/images/links-uit.png")
        out_btn = tk.Button(win, image=self.left_out_img, command=button_out_pushed)
        out_btn.grid(row=1, column=0)

        self.left_in_img = tk.PhotoImage(file="resources/images/links-in.png")
        in_btn = tk.Button(win, image=self.left_in_img, command=button_in_pushed)
        in_btn.grid(row=1, column=1)

        #winsound.Beep(500, 500)
        #winsound.Beep(500, 500)
