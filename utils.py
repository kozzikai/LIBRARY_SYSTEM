from tkinter import Tk, Canvas, BOTH, Frame, Label, Entry, Button, messagebox, Toplevel, ttk, font, W, END
import pymysql
from load_env import *

logger = logging.getLogger("UTILS")
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

try:
    con = pymysql.connect(host=DB_HOST,
                          user=DB_USERNAME,
                          password=DB_PASSWORD,
                          unix_socket="/tmp/mysql.sock",
                          database=DB_NAME)
    cur = con.cursor()
    dict_cur = con.cursor(pymysql.cursors.DictCursor)
    logger.info("Was able to connect to DB")
except:
    logger.error("Failed to connect to DB")
    messagebox.showinfo("Failure",
                        "Failed to connect to My SQL Db, please try again")
    exit(1)


def is_valid_card_id(card_id):
    query = f"SELECT * FROM {BORROWER_TABLE} WHERE Card_id = '{card_id}'"
    entries = cur.execute(query)
    con.commit()

    if not entries:
        return False
    return True


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


def create_frame(master,
                 background,
                 x_pos,
                 y_pos,
                 rel_width,
                 rel_height,
                 border_width=0):
    frame = Frame(master, bg=background, bd=border_width)
    frame.place(relx=x_pos,
                rely=y_pos,
                relwidth=rel_width,
                relheight=rel_height)
    return frame


def create_label(master,
                 text,
                 foreground,
                 x_pos,
                 y_pos,
                 rel_width,
                 rel_height,
                 background='burlywood3',
                 font=None):
    if background:
        label = Label(master, text=text, fg=foreground, bg=background)
    else:
        label = Label(master, text=text, fg=foreground)

    if font:
        label.config(font=font)

    label.place(relx=x_pos,
                rely=y_pos,
                relwidth=rel_width,
                relheight=rel_height)
    return label


def create_label_entry(master_frame,
                       text,
                       background,
                       foreground,
                       label_x_pos,
                       entry_x_pos,
                       y_pos,
                       rel_width,
                       font=None):
    label = Label(master_frame, text=text, bg=background, fg=foreground)
    label.place(relx=label_x_pos, rely=y_pos)

    entry = Entry(master_frame)
    entry.place(relx=entry_x_pos, rely=y_pos, relwidth=rel_width)
    if font:
        label.config(font=font)
    return label, entry


def create_button(master,
                  text,
                  foreground,
                  x_pos,
                  y_pos,
                  rel_width,
                  rel_height,
                  command,
                  background='tan4'):
    button = Button(master,
                    text=text,
                    bg=background,
                    fg=foreground,
                    command=command,
                    bd=0)
    button.config(borderwidth=0, relief="flat", highlightthickness=0)
    button.place(relx=x_pos,
                 rely=y_pos,
                 relwidth=rel_width,
                 relheight=rel_height)

    return button


def show_modal_message_box(message, title="ERROR"):
    """ Display a non-modal error message """
    error_window = Toplevel()
    error_window.title(title)
    foreground = "#0000FF"
    title = title.upper()
    if title in ["ERROR", "FAILURE"]:
        foreground = "red"
    elif title in ["SUCCESS"]:
        foreground = "green"
    elif title in ["WARNING"]:
        foreground = "yellow"

    Label(error_window, text=message, fg=foreground).pack(pady=10, padx=10)
    Button(error_window, text="Ok", command=error_window.destroy).pack(pady=5)

    # Make the window modal
    error_window.transient(
        error_window.master
    )  # Make the dialog transient with respect to the main window
    error_window.grab_set()  # Ensure all events are directed to this window
    error_window.wait_window()  # Wait here until the window is destroyed


def convert_to_ssn_format(ssn_no):
    return f"{ssn_no[0:3]}-{ssn_no[3:5]}-{ssn_no[5:]}"


def convert_to_phone_format(phone_no):
    return f"({phone_no[0:3]}) {phone_no[3:6]}-{phone_no[6:]}"


def get_next_id(current_id):

    # Extract the numerical part and increment it
    next_id_num = int(current_id[2:]) + 1
    next_id = f"ID{next_id_num:06d}"  # Formats the number as a zero-padded string
    return next_id
