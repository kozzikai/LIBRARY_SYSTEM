from utils import *
buttons = {}

logger = logging.getLogger("REFRESH FINES")
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


def check_in():
    global selected_book_id

    selected_book_id = tree.selection()
    selected_book_index = [tree.index(id) for id in selected_book_id]

    cur.execute("SELECT CURDATE()")
    con.commit()
    curr_date = cur.fetchone()[0]

    try:
        for i in selected_book_index:
            update_query = f"UPDATE {LOANS_TABLE} SET Date_in = '{str(curr_date)}' WHERE Loan_id = {result_list[i][0]}"
            logger.info(f"Executing update query: {update_query}")
            cur.execute(update_query)
            logger.error(f"Successfully checked in book with isbn {result_list[i][0]}")
            messagebox.showinfo("Success", "Successfully Checked in Book")
        con.commit()
        search_loan(after_check_in=True)
    except Exception as e:
        logger.error(f"Updation of Book Check-in failed with exception: {e}")
        messagebox.showinfo("Failed", "Failed to Check-In Book")


def on_loan_select(event):
    global tree, selected_book_id
    # Get the treeview widget from the event
    tree = event.widget
    # Identify the item at the location of the mouse click
    clicked_item = tree.identify_row(event.y)

    # Manage the selection state
    current_selection = tree.selection()
    if clicked_item:
        if clicked_item in current_selection:
            # Item is already selected, deselect it
            tree.selection_remove(clicked_item)
        else:
            # Deselect all and select the new item
            tree.selection_remove(*current_selection)
            tree.selection_add(clicked_item)

    # Update the selected_book_id
    selected_book_id = tree.selection()
    selected_book_index = [tree.index(id) for id in selected_book_id]
    logger.info(f"selected_book_index is {selected_book_index}")


def search_loans_by_attribute(search_query):
    global result_list, tree

    cur.execute(search_query)
    con.commit()
    matched_entries = cur.fetchall()

    # Now we insert the data into the Treeview
    for entry in matched_entries:
        loan_id = entry[0]  # Assuming this is the loan ID
        isbn = entry[1]  # Assuming this is the ISBN
        card_id = entry[2]  # Assuming this is the card ID
        borrower_name = entry[8]  # Assuming this is the borrower's name
        date_out = entry[3]  # Assuming this is the date out
        due_date = entry[4]  # Assuming this is the due date
        date_in = entry[5]  # Assuming this is the date in, if present
        tree.insert('', END, values=(loan_id, isbn, card_id, borrower_name, date_out, due_date, date_in))
        result_list.append((loan_id, isbn, card_id, borrower_name, date_out, due_date, date_in))


def update_back_button(text, background, foreground, command, x_pos, y_pos, rel_width, rel_height):
    global back_button

    back_button.place_forget()
    back_button.config(text=text, background=background, foreground=foreground, command=command, bd=0)
    back_button.place_configure(relx=x_pos, rely=y_pos, relwidth=rel_width, relheight=rel_height)
    master.update_idletasks()


def search_loan(after_check_in=False):
    global tree, result_list, back_button, count, buttons
    result_list = []

    if count:
        for button_name in ["check_in_button", "result_frame"]:
            try:
                logger.info(f"Trying to remove previously loaded {button_name} button if they exist")
                buttons[button_name].destroy()
            except Exception as e:
                logger.info(f"No previously loaded {button_name} button to remove")
    count = count + 1

    search_pattern = search_entry.get()

    if not search_pattern:
        update_back_button("BACK", 'snow', 'black', master.destroy, 0.40, 0.90, 0.18, 0.05)
        messagebox.showerror("Invalid", "Empty search pattern not allowed, Please enter a valid search pattern")
        return

    buttons["result_frame"] = Frame(master, bg='black')

    # Creating a treeview
    tree = ttk.Treeview(buttons["result_frame"], show='headings', selectmode='none')

    # Define the columns
    tree['columns'] = ('LOAN_ID', 'ISBN', 'CARD_ID', 'BORROWER_NAME', 'DATE_OUT', 'DUE_DATE', 'DATE_IN')

    # Get the default font
    default_font = font.nametofont("TkDefaultFont")

    # Measure the width of the character '0'
    char_width = default_font.measure('0')

    # Format the columns to match the new column names and desired widths
    tree.column('LOAN_ID', anchor=W, width=10 * char_width)
    tree.column('ISBN', anchor=W, width=15 * char_width)
    tree.column('CARD_ID', anchor=W, width=10 * char_width)
    tree.column('BORROWER_NAME', anchor=W, width=40 * char_width)
    tree.column('DATE_OUT', anchor=W, width=10 * char_width)
    tree.column('DUE_DATE', anchor=W, width=10 * char_width)
    tree.column('DATE_IN', anchor=W, width=10 * char_width)

    # Create Headings to match the new column names
    tree.heading('LOAN_ID', text='LOAN ID', anchor=W)
    tree.heading('ISBN', text='ISBN', anchor=W)
    tree.heading('CARD_ID', text='CARD ID', anchor=W)
    tree.heading('BORROWER_NAME', text='BORROWER NAME', anchor=W)
    tree.heading('DATE_OUT', text='DATE OUT', anchor=W)
    tree.heading('DUE_DATE', text='DUE DATE', anchor=W)
    tree.heading('DATE_IN', text='DATE IN', anchor=W)

    # search_query = f"SELECT * FROM {LOANS_TABLE} AS L,{BORROWER_TABLE} AS B WHERE L.Card_id = B.Card_id AND (B.Bname LIKE '%{search_pattern}%' OR L.Card_id LIKE '%{search_pattern}%'"
    search_query = f"""
        SELECT * FROM {LOANS_TABLE} AS L,{BORROWER_TABLE} AS B
         WHERE L.Card_id = B.Card_id
          AND 
            (
                B.Bname LIKE '%{search_pattern}%'
                OR
                L.Card_id LIKE '%{search_pattern}%'
                OR
                L.Isbn LIKE '%{search_pattern}%'
            ) 
          AND 
            Date_in IS NULL
    """

    logger.info(f"Executing loan search query :\n {search_query}")

    # Execute search query
    try:
        search_loans_by_attribute(search_query)
    except Exception as e:
        logger.error(f"Loan search failed with exception {e}")

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
    tree.bind('<ButtonRelease-1>', on_loan_select)
    buttons["result_frame"].update_idletasks()

    if not tree.get_children():
        # back Button
        update_back_button("BACK", 'snow', 'black', master.destroy, 0.40, 0.90, 0.18, 0.05)
        if not after_check_in:
            messagebox.showinfo("INFO", "No book loans with matching Isbn/Card id/Borrower Name Pattern")
        return

    buttons["check_in_button"] = create_button(master, text="CHECK-IN", background='#d1ccc0', foreground='black', command=check_in,
                                    x_pos=0.28, y_pos=0.9, rel_width=0.18, rel_height=0.05)

    update_back_button("BACK", 'snow', 'black', master.destroy, 0.53, 0.90, 0.18, 0.05)


def loans_search_page():
    global master, main_canvas, search_bar_frame, search_label, search_entry, search_button, back_button, count
    count = 0

    master = create_master()

    main_canvas = create_canvas(master, background="burlywood3")

    # Creating Label and Entry for accepting search pattern
    search_label, search_entry = create_label_entry(master, text="BOOK CHECKIN : ",  background='burlywood3',
                                                    foreground='tan4',label_x_pos=0.02, entry_x_pos=0.22, y_pos=0.05,
                                                    rel_width=0.54, font=("Helvetica", 15, "bold"))

    # Search Button
    search_button = create_button(master, text="SEARCH", background='snow', foreground='black',
                                  command=search_loan, x_pos=0.80, y_pos=0.05, rel_width=0.18, rel_height=0.05)

    # back Button
    back_button = create_button(master, text="BACK", background='snow', foreground='black',
                                command=master.destroy,
                                x_pos=0.40, y_pos=0.90, rel_width=0.18, rel_height=0.05)

    master.mainloop()
