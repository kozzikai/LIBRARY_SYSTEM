from refresh_fines import *

logger = logging.getLogger("PAY FINES")
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

count = 0
buttons = {}

def pay():
    try:
        update_fines_query = f"UPDATE {FINES_TABLE} SET Paid = 1 WHERE Loan_id in ({','.join(loan_ids)}) AND Fine_amt > 0 AND FLOOR(Paid) = 0"
        cur.execute(update_fines_query)
        con.commit()
    except Exception as e:
        logger.info(f"Updation of completed payment on loan ids {','.join(loan_ids)} failed with exception: {e}")
        messagebox.showinfo("Failure", "Payment Update Failed, please try again")
        master.destroy()

    logger.info(f"Fine payment on loan ids {','.join(loan_ids)} is successfully completed")
    messagebox.showinfo("Success", "Fine Payment Successful")
    master.destroy()


def destroy_button(name):
    global buttons
    try:
        logger.info(f"Trying to remove previously loaded {name} button if they exist")
        buttons[name].destroy()
    except Exception as e:
        logger.info(f"No previously loaded {name} button to remove")


def update_back_button(text, background, command, x_pos, y_pos, rel_width, rel_height):
    global back_button

    back_button.place_forget()
    back_button.config(text=text, background=background, command=command, bd=0)
    back_button.place_configure(relx=x_pos, rely=y_pos, relwidth=rel_width, relheight=rel_height)
    master.update_idletasks()


def display_fine_by_card_id_new():
    global card_id, loan_ids, back_button, result_frame, pay_fine_button, count, buttons

    if count:
        destroy_button("result_frame")
        destroy_button("pay_fine_button")
    count = count + 1

    loan_ids = []
    card_id = card_id_entry.get()

    if not is_valid_card_id(card_id):
        update_back_button("BACK", 'snow', master.destroy, 0.40, 0.90, 0.18, 0.05)
        logger.info(f"Card_id {card_id} doesn't exist. Please enter a valid card id")
        messagebox.showerror(f"Invalid Card Id {card_id}", f"Card_id doesn't exist. Please enter a valid card id")
        return

    dict_cur.execute("SELECT CURDATE()")
    con.commit()
    today_date = dict_cur.fetchone()["CURDATE()"]

    # Get Fine Details for the given card_id
    existing_fine_count = dict_cur.execute(
        f"SELECT SUM(F.Fine_amt) as Total_Fine, FLOOR(AVG(F.Paid)) as Paid FROM {LOANS_TABLE} AS L,"
        f"{FINES_TABLE} AS F WHERE L.Loan_id = F.Loan_id AND Card_id = '{card_id}' AND F.Fine_amt > 0 AND FLOOR(F.Paid) = 0 GROUP BY L.Card_id")
    con.commit()

    if not existing_fine_count:
        update_back_button("BACK", 'snow', master.destroy, 0.40, 0.90, 0.18, 0.05)
        logger.info(f"No existing fines for card_id {card_id}")
        messagebox.showinfo("FAILURE", f"No existing fines for card_id {card_id}")
        return

    fine_amount = dict_cur.fetchall()[0]["Total_Fine"]
    logger.info(f"Existing Fine amount on card_id {card_id}: {fine_amount}")

    buttons["result_frame"] = Frame(master, bg='black')

    # Creating a treeview
    tree = ttk.Treeview(buttons["result_frame"], show='headings', selectmode='none')

    # Define the columns
    tree['columns'] = ('LOAN_ID', 'ISBN', 'CARD_ID', 'DATE_OUT', 'DUE_DATE', 'DATE_IN', 'FINE_AMOUNT', 'PAID')

    # Get the default font
    default_font = font.nametofont("TkDefaultFont")

    # Measure the width of the character '0'
    char_width = default_font.measure('0')

    # Loan_id | Isbn | Card_id | Date_out | Due_date | Date_in | Fine_amt | Paid
    tree.column('LOAN_ID', anchor=W, width=10 * char_width)
    tree.column('ISBN', anchor=W, width=15 * char_width)
    tree.column('CARD_ID', anchor=W, width=10 * char_width)
    tree.column('DATE_OUT', anchor=W, width=10 * char_width)
    tree.column('DUE_DATE', anchor=W, width=10 * char_width)
    tree.column('DATE_IN', anchor=W, width=10 * char_width)
    tree.column('FINE_AMOUNT', anchor=W, width=10 * char_width)
    tree.column('PAID', anchor=W, width=10 * char_width)

    # Create Headings to match the new column names
    tree.heading('LOAN_ID', text='LOAN ID', anchor=W)
    tree.heading('ISBN', text='ISBN', anchor=W)
    tree.heading('CARD_ID', text='CARD ID', anchor=W)
    tree.heading('DATE_OUT', text='DATE OUT', anchor=W)
    tree.heading('DUE_DATE', text='DUE DATE', anchor=W)
    tree.heading('DATE_IN', text='DATE IN', anchor=W)
    tree.heading('FINE_AMOUNT', text='FINE AMOUNT', anchor=W)
    tree.heading('PAID', text='PAID', anchor=W)

    # Get Fine Details for the given card_id
    dict_cur.execute(
        f"SELECT * FROM BOOK_LOANS AS L JOIN FINES AS F USING (Loan_id)"
        f"WHERE Card_id = '{card_id}' AND F.Fine_amt > 0 AND FLOOR(F.Paid) = 0")
    con.commit()
    fines_list = dict_cur.fetchall()

    for fine_entry in fines_list:
        loan_ids.append(str(fine_entry["Loan_id"]))
        tree.insert('', END, values=(fine_entry["Loan_id"], fine_entry["Isbn"], fine_entry["Card_id"],
                                        fine_entry["Date_out"], fine_entry["Due_date"], fine_entry["Date_in"],
                                     fine_entry["Fine_amt"], fine_entry["Paid"]))

    buttons["result_frame"].place(relx=0.02, rely=0.15, relwidth=0.96, relheight=0.7)

    # Add vertical scrollbar
    vscroll = ttk.Scrollbar(buttons["result_frame"], orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vscroll.set)
    vscroll.pack(side='right', fill='y')

    # Add horizontal scrollbar
    hscroll = ttk.Scrollbar(buttons["result_frame"], orient="horizontal", command=tree.xview)
    tree.configure(xscrollcommand=hscroll.set)
    hscroll.pack(side='bottom', fill='x')

    # Pack the Treeview
    tree.pack(side='left', fill='both', expand=True)

    buttons["result_frame"].update_idletasks()

    existing_loans = cur.execute(
        f"SELECT * FROM {LOANS_TABLE} WHERE Card_id = '{card_id}' AND Date_in IS NULL AND '{today_date}' > Due_date")
    con.commit()

    if existing_loans > 0:
        update_back_button("BACK", 'snow', master.destroy, 0.40, 0.90, 0.18, 0.05)

        messagebox.showerror("FAILURE", "Please return back books that crossed due date before paying the fine")
        return

    buttons["pay_fine_button"] = create_button(master, text=f"Pay Fine: {fine_amount}", background='#d1ccc0', foreground='black', command=pay,
                                    x_pos=0.28, y_pos=0.9, rel_width=0.18, rel_height=0.05)

    update_back_button("BACK", 'snow', master.destroy, 0.53, 0.90, 0.18, 0.05)

    if not tree.get_children():
        messagebox.showinfo("INFO", "No borrowers with matching Ssn/Bname/Address/Phone Pattern")


def load_card_number_page():
    global listbox, main_canvas, card_id_label, card_id_entry, get_fine_button, exit_button, entry_frame, master, back_button, count

    refresh()

    count = 0
    master = create_master()
    main_canvas = create_canvas(master, background="burlywood3")

    # Creating Label and Entry for accepting card_id
    card_id_label, card_id_entry = create_label_entry(master, text="CARD ID: ",  background='burlywood3',
                                                    foreground='tan4',label_x_pos=0.02, entry_x_pos=0.22, y_pos=0.05,
                                                    rel_width=0.54, font=("Helvetica", 15, "bold"))

    # Issue Button
    get_fine_button = create_button(master, text="FIND", background='snow', foreground='black',
                                  command=display_fine_by_card_id_new, x_pos=0.80, y_pos=0.05, rel_width=0.18, rel_height=0.05)

    back_button = create_button(master, text="BACK", background='snow', foreground='black',
                                command=master.destroy,
                                x_pos=0.40, y_pos=0.90, rel_width=0.18, rel_height=0.05)

    master.mainloop()
