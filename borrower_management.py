from utils import *

logger = logging.getLogger("ADD BORROWER")
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


def reset_values():
    name_entry.delete(0, END)
    ssn_entry.delete(0, END)
    address_entry.delete(0, END)
    phone_entry.delete(0, END)


def add_borrower():
    global bname, ssn, phone_no, address
    bname = name_entry.get()
    ssn = ssn_entry.get()
    phone_no = phone_entry.get()
    address = address_entry.get()

    if not bname or not ssn or not phone_no or not address:
        messagebox.showerror("Invalid", f"Please fill in all fields")
        return

    if not (ssn.isdigit() and len(ssn) == 9):
        messagebox.showerror(
            "Invalid", f"Invalid SSN: Please enter a valid 9-digit number")
        return

    if not (phone_no.isdigit() and len(phone_no) == 10):
        messagebox.showerror(
            "Invalid", f"Invalid Phone: Please enter a valid 10-digit number")
        return

    ssn_string = convert_to_ssn_format(ssn)
    phone_string = convert_to_phone_format(phone_no)

    # Check if entry already exists
    query = f"SELECT * FROM {BORROWER_TABLE} WHERE Ssn = '{ssn_string}'"
    entries = cur.execute(query)
    con.commit()

    if entries:
        card_id = cur.fetchone()[0]
        messagebox.showinfo("Invalid",
                            f"Borrower already exists, card_id is {card_id}")
        return

    # SQL query to find the highest id value
    cur.execute(
        f"SELECT Card_id FROM {BORROWER_TABLE} ORDER BY Card_id DESC LIMIT 1")
    highest_id_entry = cur.fetchone()
    current_max_id = highest_id_entry[0] if highest_id_entry else "ID000000"
    new_id = get_next_id(current_max_id)
    try:

        insert_query = f"INSERT INTO {BORROWER_TABLE}(Card_id,Ssn,Bname,Address,Phone) VALUES('{new_id}','{ssn_string}','{bname}','{address}','{phone_string}')"
        logger.info(f"Executing insert query: {insert_query}")
        cur.execute(insert_query)
        con.commit()
        logger.info(f"Card id for borrower {bname} is {new_id}")
        messagebox.showinfo("Success",
                            f"Borrower Added, Borrower's card_id is {new_id}")
        master.destroy()
    except Exception as e:
        logger.error(f"Addition of borrower failed with exception: {e}")
        messagebox.showinfo("Failure", "Please check values and try again.")
        reset_values()
        return


def get_borrower_data():
    global master_canvas, master, title_frame, ssn_label, ssn_entry, name_label, name_entry, phone_label, phone_entry, address_label, address_entry

    master = create_master()
    master_canvas = create_canvas(master)

    title_frame = create_frame(master,
                               background='burlywood3',
                               x_pos=0.2,
                               y_pos=0.2,
                               rel_width=0.6,
                               rel_height=0.6,
                               border_width=5)

    bg_colour = 'burlywood3'
    fg_colour = 'snow'

    # Creating Label and Entry for accepting SSN
    ssn_label, ssn_entry = create_label_entry(title_frame,
                                              text="SSN : ",
                                              background=bg_colour,
                                              foreground=fg_colour,
                                              label_x_pos=0.05,
                                              entry_x_pos=0.3,
                                              y_pos=0.05,
                                              rel_width=0.62,
                                              font=("Helvetica", 15, "bold"))

    name_label, name_entry = create_label_entry(title_frame,
                                                text="NAME : ",
                                                background=bg_colour,
                                                foreground=fg_colour,
                                                label_x_pos=0.05,
                                                entry_x_pos=0.3,
                                                y_pos=0.2,
                                                rel_width=0.62,
                                                font=("Helvetica", 15, "bold"))

    phone_label, phone_entry = create_label_entry(title_frame,
                                                  text="PHONE : ",
                                                  background=bg_colour,
                                                  foreground=fg_colour,
                                                  label_x_pos=0.05,
                                                  entry_x_pos=0.3,
                                                  y_pos=0.35,
                                                  rel_width=0.62,
                                                  font=("Helvetica", 15,
                                                        "bold"))

    address_label, address_entry = create_label_entry(title_frame,
                                                      text="ADDRESS : ",
                                                      background=bg_colour,
                                                      foreground=fg_colour,
                                                      label_x_pos=0.05,
                                                      entry_x_pos=0.3,
                                                      y_pos=0.5,
                                                      rel_width=0.62,
                                                      font=("Helvetica", 15,
                                                            "bold"))

    # Submit Button
    create_button(master,
                  text="SUBMIT",
                  background='snow',
                  foreground='black',
                  command=add_borrower,
                  x_pos=0.28,
                  y_pos=0.9,
                  rel_width=0.18,
                  rel_height=0.08)

    # Quit Button
    create_button(master,
                  text="BACK",
                  background='snow',
                  foreground='black',
                  command=master.destroy,
                  x_pos=0.53,
                  y_pos=0.9,
                  rel_width=0.18,
                  rel_height=0.08)

    master.mainloop()
