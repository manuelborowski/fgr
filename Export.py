from tkinter import filedialog
import datetime
import csv
import os

class Export:
    def __init__(self, root_window, database, close_cb):
        self.root_window = root_window
        self.database = database
        self.close_cb = close_cb


    def export_database(self):
        now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        options = {}
        options['defaultextension'] = '.csv'
        options['filetypes'] = [('CSV file', '.csv')]
        options['initialdir'] = os.path.expanduser("~")+"/Downloads/"
        options['initialfile'] = 'fgr-export-' + now
        options['title'] = 'Bewaar database in CSV bestand'
        filename = filedialog.asksaveasfilename(**options)
        print(filename)
        try:
            f = open(filename, 'w', newline="")
            data = self.database.get_registrations_and_guests(True)
            writer = csv.writer(f, delimiter=';')
            first_item = next(data)  # get first item to get keys
            writer.writerow(first_item.keys())  # keys=title you're looking for
            writer.writerow(first_item)
            # write the rest
            writer.writerows(data)
            f.close()
        except:
            pass

        self.close_cb()
