import tkinter as tk
import winsound
import datetime

class Register:
    def __init__(self, root_window, database):
        self.root_window = root_window
        self.database = database

    def add_registration(self, guest):
        print(guest.company)
        time = datetime.datetime.now()
        print(time.date())
        registration_last = self.database.find_registration_from_badge(guest.badge)
        registration_next_to_last = self.database.find_registration_from_badge(guest.badge, -1)
        if not registration_last.found:
            #no registrations yet
            print('First registration')
            direction = 'IN'
        elif registration_last.time.date() == time.date():
            #current date is the same as the previous date, hence badge OUT
            direction = 'UIT'
            if registration_last.direction=='IN':
                print('Second registration on current day')
            else:
                print('Third registration this day, remove the last one and a new one')
                self.database.delete_registration(registration_last.id)
        elif registration_next_to_last.found:
            if registration_last.time.date() == registration_next_to_last.time.date():
                #previous two registrations have the same date, hence badge IN
                print('First registration on current day')
                direction = 'IN'
            else:
                #error : registration of previous visit was not correct, add one to correct
                print('Registration of previous visit was not correct')
                direction = 'IN'
                self.database.add_registration(guest.badge, registration_last.time, 'IN', True)
        else:
            # error : registration of previous visit was not correct, add one to correct
            print('Registration of previous visit was not correct')
            self.database.add_registration(guest.badge, registration_last.time, 'IN', True)
            direction = 'IN'
        self.database.add_registration(guest.badge, time, direction, False)


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
