from utils import *
import tkinter as tk
from tkinter import ttk
from tkinter import font

logger = logging.getLogger("CHECK-OUT")
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

isbn = "Isbn"
title = "Title"
authors = "Author_Names"
availability = "Availability"
s_no = "S.No"
buttons = {}

def issue():
    card_id = card_id_entry.get()

    # Check if entry already exists
    if not is_valid_card_id(card_id):
        messagebox.showerror(f"Invalid Card Id {card_id}", f"Card_id doesn't exist. Please enter a valid card id")
        return

    issue_button.destroy()
    back_button.destroy()
    exit_button.destroy()
    card_id_label.destroy()
    card_id_entry.destroy()

    # Get the selected items
    selected_ids = tree.selection()
    selected_indices = [tree.index(id) for id in selected_ids]
    logger.info(f"Selected book indices are {selected_indices}")

    existing_loans = cur.execute(
        f"SELECT * FROM {LOANS_TABLE} WHERE Card_id = '{str(card_id)}' AND Date_in IS NULL")
    con.commit()

    if (existing_loans + len(selected_indices) <= 3):
        cur.execute("SELECT CURDATE()")
        today_date = cur.fetchone()[0]

        due_date_loans = cur.execute(
            f"SELECT * FROM {LOANS_TABLE} WHERE Card_id = '{card_id}' AND Date_in IS NULL AND '{today_date}' > Due_date")
        con.commit()

        if due_date_loans > 0:
            logger.error(f"There are existing loans on Card id {card_id} that crossed due date")
            messagebox.showerror("FAILURE",
                                 "Please return back books that crossed due date before borrowing new book(s)")
            master.destroy()
            return

        existing_fine_count = dict_cur.execute(
            f"SELECT SUM(F.Fine_amt) as Total_Fine, FLOOR(AVG(F.Paid)) as Paid FROM {LOANS_TABLE} AS L,"
            f"{FINES_TABLE} AS F WHERE L.Loan_id = F.Loan_id AND Card_id = '{card_id}' AND FLOOR(F.Paid) = 0 GROUP BY L.Card_id")
        con.commit()

        if existing_fine_count:
            fine_amount = dict_cur.fetchall()[0]['Total_Fine']
            if fine_amount > 0:
                logger.error(f"There are unpaid fines on Card id {card_id}. ")
                messagebox.showinfo("FAILURE",
                                    f"Please pay existing fine amount {fine_amount} before borrowing new book(s)")
                master.destroy()
                return

        cur.execute("SELECT DATE_ADD('" + str(today_date) + "', INTERVAL 14 DAY)")
        due_date = cur.fetchone()[0]

        con.commit()

        issued = []

        try:
            for index in selected_indices:
                isbn = str(result_list[index][0])
                logger.info(f"Issuing book with isbn {isbn} on Card id {card_id}")
                cur.execute(f"INSERT INTO {LOANS_TABLE}(Isbn,Card_id,Date_out,Due_date) VALUES(%s,%s,%s,%s)",
                            (str(isbn), str(card_id), str(today_date), str(due_date)))
                cur.execute(f"SELECT * FROM {LOANS_TABLE} WHERE Isbn = '{str(isbn)}' AND Date_in IS NULL")
                loan_id = cur.fetchone()[0]
                logger.info(f"Loan id is: {loan_id}, Current Date: {today_date}, Due date: {due_date}")

                cur.execute(f"INSERT INTO {FINES_TABLE}(Loan_id) VALUES(" + str(loan_id) + ")")
                issued.append(str(isbn))
            con.commit()
            logger.info(f"Succesfully Issued Books: {','.join(issued)}")
            messagebox.showinfo("Success", f"Succesfully Issued Books: {','.join(issued)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to issue selected book(s)")
            logger.error(e)
    else:
        if existing_loans == 3:
            logger.error("Cannot Issue New Books. Maximum No. of Book Loans for a borrower is 3")
            messagebox.showerror("Error", "Cannot Issue New Books. Maximum No. of Book Loans for a borrower is 3")
        else:
            logger.error(f"Maximum No. of Book Loans for a borrower is 3. Please select {3 - existing_loans} or less books")
            messagebox.showerror("Error", f"Maximum No. of Book Loans for a borrower is 3. Please select {3 - existing_loans} or less books")

    master.destroy()


def get_card_number_page():
    global listbox, main_canvas, card_id_label, card_id_entry, issue_button, exit_button, entry_frame, back_button

    main_canvas.destroy()
    main_canvas = create_canvas(master, background="burlywood3")

    create_label(master, text="ISSUE BOOK", foreground='tan4', x_pos=0.25, y_pos=0.05, rel_width=0.5, rel_height=0.5, background="burlywood3", font=("Helvetica", 30, "bold"))

    # Creating Label and Entry for accepting card_id
    card_id_label, card_id_entry = create_label_entry(master, text="CARD ID: ", background='burlywood3',
                                                      foreground='tan4',
                                                      label_x_pos=0.05, entry_x_pos=0.2, y_pos=0.6, rel_width=0.62, font=("Helvetica", 15, "bold"))

    # Issue Button
    issue_button = create_button(master, text="Issue", background='#d1ccc0', foreground='black', command=issue,
                                 x_pos=0.18, y_pos=0.75, rel_width=0.18, rel_height=0.08)

    back_button = create_button(master, text="Back", background='#aaa69d', foreground='black', command=load_search_page,
                                x_pos=0.43, y_pos=0.75, rel_width=0.18, rel_height=0.08)

    exit_button = create_button(master, text="Exit", background='#aaa69d', foreground='black', command=master.destroy,
                                x_pos=0.68, y_pos=0.75, rel_width=0.18, rel_height=0.08)


def on_select(event):
    global tree, selected_ids

    # Get the treeview widget from the event
    tree = event.widget
    last_selected_id = tree.identify_row(event.y)

    logger.info(f"on_select event triggered on selecting index {tree.index(last_selected_id)}")
    if last_selected_id:
        if last_selected_id in tree.selection():
            tree.selection_remove(last_selected_id)
        else:
            tree.selection_add(last_selected_id)

    # Get the availability of the last selected Treeview item
    availability = tree.item(last_selected_id, 'values')[4]

    # If availability is "No", deselect it
    if availability.lower() == "no":
        tree.selection_remove(last_selected_id)
        logger.info(f"Selected book index {tree.index(last_selected_id)} is unavailable")
        messagebox.showwarning("Warning", "Cannot select unavailable books")
        return

    # Get the selected items
    selected_ids = tree.selection()
    selected_indices = [tree.index(id) for id in selected_ids]

    # Limit the selection to 3 items
    if len(selected_ids) > 3:
        tree.selection_remove(last_selected_id)
        messagebox.showwarning("Warning", "Cannot select more than 3 entries at a time")
        logger.info("You can select up to 3 books only.")
        return


def search_by_attribute(search_query):
    global serial_no, result_list, tree

    cur.execute(search_query)
    con.commit()
    matched_entries = cur.fetchall()

    for entry in matched_entries:
        available = "No"
        isbn = entry[0]
        title = entry[1]
        authors = entry[2]
        result = cur.execute(f"SELECT * FROM {LOANS_TABLE} WHERE Isbn = '{str(isbn)}' AND Date_in IS NULL")
        if not result:
            available = "Yes"
        tree.insert('', tk.END, values=((f"{serial_no}", isbn, title, authors, available)))
        result_list.append((isbn, title, authors, available))
        serial_no = serial_no + 1


def update_back_button(text, background, foreground, command, x_pos, y_pos, rel_width, rel_height):
    global back_button

    back_button.place_forget()
    back_button.config(text=text, background=background, foreground=foreground, command=command, bd=0)
    back_button.place_configure(relx=x_pos, rely=y_pos, relwidth=rel_width, relheight=rel_height)
    master.update_idletasks()


def search():
    global search_entry, tree, result_list, serial_no, back_button, buttons, count

    if count:
        for button_name in ["issue_button", "search_bar_frame"]:
            try:
                logger.info(f"Trying to remove previously loaded {button_name} button if they exist")
                buttons[button_name].destroy()
            except Exception as e:
                logger.info(f"No previously loaded {button_name} button to remove")
    count = count + 1

    result_list = []
    serial_no = 1
    search_pattern = search_entry.get()

    if not search_pattern:
        update_back_button("BACK", 'snow', 'black', master.destroy, 0.40, 0.90, 0.18, 0.05)
        messagebox.showerror("Invalid", "Empty search pattern not allowed, Please enter a valid search pattern")
        return

    buttons["search_bar_frame"] = Frame(master, bg='tan4')

    # Creating a treeview
    tree = ttk.Treeview(buttons["search_bar_frame"], show='headings', selectmode='none')

    # Define the columns
    tree['columns'] = ('S.NO', 'ISBN', 'TITLE', 'AUTHOR', 'AVAILABLE')

    # Get the default font
    default_font = font.nametofont("TkDefaultFont")

    # Measure the width of the character '0'
    char_width = default_font.measure('0')

    # Format the columns
    tree.column('#0', width=0, stretch=tk.NO)
    tree.column('S.NO', anchor=tk.W, width=4 * char_width)
    tree.column('ISBN', anchor=tk.W, width=15 * char_width)
    tree.column('TITLE', anchor=tk.W, width=75 * char_width)
    tree.column('AUTHOR', anchor=tk.W, width=30 * char_width)
    tree.column('AVAILABLE', anchor=tk.W, width=10 * char_width)

    # Create Headings
    tree.heading('#0', text='', anchor=tk.W)
    tree.heading('S.NO', text='S.NO', anchor=tk.W)
    tree.heading('ISBN', text='ISBN', anchor=tk.W)
    tree.heading('TITLE', text='TITLE', anchor=tk.W)
    tree.heading('AUTHOR', text='AUTHOR', anchor=tk.W)
    tree.heading('AVAILABLE', text='AVAILABLE', anchor=tk.W)

    search_query = f"""
    SELECT * FROM (
        SELECT
            B.Isbn,
            B.Title,
            GROUP_CONCAT(A.Name ORDER BY A.Name SEPARATOR ', ') AS Authors
        FROM
            {BOOK_TABLE} B
        JOIN
            {BOOK_AUTHOR_TABLE} BA ON B.Isbn = BA.Isbn
        JOIN
            {AUTHOR_TABLE} A ON BA.Author_id = A.Author_id
        GROUP BY
            B.Isbn,
            B.Title
    ) AS SubBookTable
    WHERE Title LIKE '%{search_pattern}%' OR Authors LIKE '%{search_pattern}%' OR Isbn LIKE '%{search_pattern}%'
    """

    # Execute search query
    try:
        logger.info(f"Executing search query: {search_query}")
        search_by_attribute(search_query)
    except Exception as e:
        logger.error(f"Search failed with exception {e}")

    logger.info(f"No. of book entries matching the given search: {len(result_list)}")
    buttons["search_bar_frame"].place(relx=0.02, rely=0.15, relwidth=0.96, relheight=0.7)

    # Add vertical scrollbar
    vscroll = ttk.Scrollbar(buttons["search_bar_frame"], orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vscroll.set)
    vscroll.pack(side='right', fill='y')

    # Add horizontal scrollbar
    hscroll = ttk.Scrollbar(buttons["search_bar_frame"], orient="horizontal", command=tree.xview)
    tree.configure(xscrollcommand=hscroll.set)
    hscroll.pack(side='bottom', fill='x')

    # Pack the Treeview
    tree.pack(side='left', fill='both', expand=True)
    tree.bind('<ButtonRelease-1>', on_select)

    if not tree.get_children():
        # back Button
        update_back_button("BACK", 'snow', 'black', master.destroy, 0.40, 0.90, 0.18, 0.05)

        messagebox.showinfo("INFO", "No books with matching Isbn/Title/Author_Names Pattern")
        return

    buttons["issue_button"] = create_button(master, text="ISSUE", background='black', foreground='#333945', command=get_card_number_page,
                  x_pos=0.30, y_pos=0.9, rel_width=0.18, rel_height=0.05)

    update_back_button("BACK", 'snow', 'black', master.destroy, 0.53, 0.90, 0.18, 0.05)


def load_search_page():
    global master, main_canvas, search_label, search_entry, back_button, count
    count = 0

    try:
        logger.info(f"Trying to remove previously created canvases")
        master.destroy()
    except Exception as e:
        logger.info(f"No previously created canvases")

    master = create_master()
    main_canvas = create_canvas(master, background="burlywood3")

    search_label, search_entry = create_label_entry(master, text="BOOK SEARCH : ", background='burlywood3',
                                                    foreground='tan4',
                                                    label_x_pos=0.02, entry_x_pos=0.22, y_pos=0.05, rel_width=0.54,
                                                    font=("Helvetica", 15, "bold"))

    # Search Button
    create_button(master, text="SEARCH", background='snow', foreground='black',
                                  command=search,
                                  x_pos=0.80, y_pos=0.05, rel_width=0.18, rel_height=0.05)

    # back Button
    back_button = create_button(master, text="BACK", background='snow', foreground='black',
                                  command=master.destroy,
                                  x_pos=0.40, y_pos=0.90, rel_width=0.18, rel_height=0.05)

    master.mainloop()
