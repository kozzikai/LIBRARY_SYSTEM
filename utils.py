from tkinter import *
from tkinter import messagebox
import pymysql
from tkinter import ttk

BOOK_TABLE = "BOOK"
AUTHOR_TABLE = "AUTHORS"
BOOK_AUTHOR_TABLE = "BOOK_AUTHORS"
EMPLOYEE_TABLE = "EMPLOYEE"
BORROWER_TABLE = "BORROWER"
LOANS_TABLE = "BOOK_LOANS"
FINES_TABLE = "FINES"


try:
    # con = pymysql.connect(host='localhost', user='root', password='MoMDaD924754*', unix_socket="/tmp/mysql.sock",
    #                       database='LIBRARY_FINAL')
    con = pymysql.connect(host='localhost', user='root', password='Kozzibannu@8', unix_socket="/tmp/mysql.sock",
                          database='LIBRARY_FINAL')
    cur = con.cursor()
    dict_cur = con.cursor(pymysql.cursors.DictCursor)
    print("Was able to connect to DB")
except:
    print("Failed to connect to DB")
    messagebox.showinfo("Failure","Failed to connect to My SQL Db, please try again")


def create_canvas(master, background="burlywood3"):
    canvas = Canvas(master)
    canvas.config(bg=background, width=600, height=500)
    canvas.pack(expand=True, fill=BOTH)
    return canvas


def create_master(title="LIBRARY", geometry="700x580", width=500, height=500):
    master = Tk()
    master.title(title)
    master.minsize(width=width, height=height)
    master.geometry(geometry)

    return master


def create_frame(master, background, x_pos, y_pos, rel_width, rel_height, border_width=0):
    frame = Frame(master, bg=background, bd=border_width)
    frame.place(relx=x_pos, rely=y_pos, relwidth=rel_width, relheight=rel_height)
    return frame


def create_label(master, text, foreground, x_pos, y_pos, rel_width, rel_height, background='burlywood3', font=None):
    if background:
        label = Label(master, text=text, fg=foreground, bg=background)
    else:
        label = Label(master, text=text, fg=foreground)

    if font:
        label.config(font=font)

    label.place(relx=x_pos, rely=y_pos, relwidth=rel_width, relheight=rel_height)
    return label


def create_label_entry(master_frame, text, background, foreground, label_x_pos, entry_x_pos, y_pos, rel_width, font=None):
    label = Label(master_frame, text=text, bg=background, fg=foreground)
    label.place(relx=label_x_pos, rely=y_pos)

    entry = Entry(master_frame)
    entry.place(relx=entry_x_pos, rely=y_pos, relwidth=rel_width)
    if font:
        label.config(font=font)
    return label, entry


def create_button(master, text, foreground, x_pos, y_pos, rel_width, rel_height, command, background='tan4'):
    button = Button(master, text=text, bg=background, fg=foreground, command=command, bd=0)
    button.config(borderwidth=0, relief="flat", highlightthickness=0)
    button.place(relx=x_pos, rely=y_pos, relwidth=rel_width, relheight=rel_height)

    return button


