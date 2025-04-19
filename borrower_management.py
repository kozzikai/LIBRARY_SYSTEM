from utils import *

def reset_values():
    name_entry.delete(0, END)
    ssn_entry.delete(0, END)
    address_entry.delete(0, END)
    phone_entry.delete(0, END)


def add_borrower():
    global bname, ssn, phone, address
    bname = name_entry.get()
    ssn = ssn_entry.get()
    phone = phone_entry.get()
    address = address_entry.get()

    if not bname or not ssn or not phone or not address:
        messagebox.showerror("Invalid", f"Please fill in all fields")
        return

    if not (ssn.isdigit() and len(ssn) == 9):
        messagebox.showerror("Invalid", f"Invalid SSN: Please enter a valid 9-digit number")
        return

    if not (phone.isdigit() and len(phone) == 10):
        messagebox.showerror("Invalid", f"Invalid Phone: Please enter a valid 10-digit number")
        return

    # Check if entry already exists
    query = f"SELECT * FROM {BORROWER_TABLE} WHERE ssn =  {str(ssn)}"
    entries = cur.execute(query)
    con.commit()

    if entries:
        card_id = cur.fetchone()[0]
        messagebox.showinfo("Invalid", f"Borrower already exists, card_id is {card_id}")
        return

    try:
        cur.execute(f"INSERT INTO {BORROWER_TABLE}(Ssn,Bname,Address,Phone) VALUES('" + str(
            ssn) + "','" + bname + "','" + address + "','" + phone + "')")
        con.commit()
    except:
        messagebox.showinfo("Failure", "Please check values and try again.")
        reset_values()
        return

    try:
        cur.execute(f"SELECT Card_id FROM {BORROWER_TABLE} WHERE Ssn = {ssn}")
        con.commit()
        card_id = cur.fetchone()[0]

        print(f"Card Id: {card_id}")
        messagebox.showinfo("Success", f"Borrower Added, Borrower's card_id is {card_id}")
        master.destroy()
    except:
        messagebox.showerror("Failure", "Borrower Added, Failed to display card_id. Please submit again to get card_id")


def get_borrower_data():
    global master_canvas, master, title_frame, ssn_label, ssn_entry, name_label, name_entry, phone_label, phone_entry, address_label, address_entry

    master = create_master()
    master_canvas = create_canvas(master)

    title_frame = create_frame(master, background='burlywood3', x_pos=0.2, y_pos=0.2, rel_width=0.6, rel_height=0.6,
                               border_width=5)

    bg_colour = 'burlywood3'
    fg_colour = 'snow'

    # Creating Label and Entry for accepting SSN
    ssn_label, ssn_entry = create_label_entry(title_frame, text="SSN : ", background=bg_colour, foreground=fg_colour,
                                               label_x_pos=0.05, entry_x_pos=0.3, y_pos=0.05, rel_width=0.62, font=("Helvetica", 15, "bold"))

    name_label, name_entry = create_label_entry(title_frame, text="NAME : ", background=bg_colour, foreground=fg_colour,
                                               label_x_pos=0.05, entry_x_pos=0.3, y_pos=0.2, rel_width=0.62, font=("Helvetica", 15, "bold"))

    phone_label, phone_entry = create_label_entry(title_frame, text="PHONE : ", background=bg_colour, foreground=fg_colour,
                                               label_x_pos=0.05, entry_x_pos=0.3, y_pos=0.35, rel_width=0.62, font=("Helvetica", 15, "bold"))

    address_label, address_entry = create_label_entry(title_frame, text="ADDRESS : ", background=bg_colour, foreground=fg_colour,
                                               label_x_pos=0.05, entry_x_pos=0.3, y_pos=0.5, rel_width=0.62, font=("Helvetica", 15, "bold"))

    # Submit Button
    create_button(master, text="SUBMIT", background='snow', foreground='black', command=add_borrower, x_pos=0.28, y_pos=0.9, rel_width=0.18, rel_height=0.08)

    # Quit Button
    create_button(master, text="EXIT", background='snow', foreground='black', command=master.destroy,
                  x_pos=0.53, y_pos=0.9, rel_width=0.18, rel_height=0.08)

    master.mainloop()

