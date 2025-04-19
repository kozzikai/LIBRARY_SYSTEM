from utils import *
import tkinter as tk
from tkinter import ttk
from tkinter import font

isbn = "Isbn"
title = "Title"
authors = "Author_Names"
availability = "Availability"
s_no = "S.No"


def issue():
    card_id = card_id_entry.get()
    issue_button.destroy()
    exit_button.destroy()
    card_id_label.destroy()
    card_id_entry.destroy()

    # Get the selected items
    selected_ids = tree.selection()
    selected_indices = [tree.index(id) for id in selected_ids]
    print(f"Selected indices are {selected_indices}")

    existing_loans = cur.execute(
        f"SELECT * FROM {LOANS_TABLE} WHERE Card_id = " + str(card_id) + " AND Date_in IS NULL")
    con.commit()

    if (existing_loans + len(selected_indices) <= 3):
        cur.execute("SELECT CURDATE()")
        today_date = cur.fetchone()[0]

        existing_loans = cur.execute(
            f"SELECT * FROM {LOANS_TABLE} WHERE Card_id = {card_id} AND Date_in IS NULL AND '{today_date}' > Due_date")
        con.commit()
        print(existing_loans)

        if existing_loans > 0:
            messagebox.showerror("FAILURE",
                                 "Please return back books that crossed due date before borrowing new book(s)")
            master.destroy()
            return

        existing_fine_count = dict_cur.execute(
            f"SELECT SUM(F.Fine_amt) as Total_Fine, FLOOR(AVG(F.Paid)) as Paid FROM {LOANS_TABLE} AS L,"
            f"{FINES_TABLE} AS F WHERE L.Loan_id = F.Loan_id AND Card_id = {card_id} AND FLOOR(F.Paid) = 0 GROUP BY L.Card_id")
        con.commit()
        print(f"existing_fine_count is {existing_fine_count}")
        if existing_fine_count:
            fine_amount = dict_cur.fetchall()[0]['Total_Fine']
            if fine_amount > 0:
                messagebox.showinfo("FAILURE",
                                    f"Please pay existing fine amount {fine_amount} before borrowing new book(s)")
                master.destroy()
                return

        cur.execute("SELECT DATE_ADD('" + str(today_date) + "', INTERVAL 14 DAY)")
        due_date = cur.fetchone()[0]

        print(f"Current Date: {today_date}, Due date: {due_date}")
        con.commit()

        issued = []
        not_issued = []

        for index in selected_indices:
            try:
                print(result_list[index])

                isbn = str(result_list[index][0])
                print(f"{isbn},{card_id},{today_date},{due_date}")
                cur.execute(f"INSERT INTO {LOANS_TABLE}(Isbn,Card_id,Date_out,Due_date) VALUES(%s,%s,%s,%s)",
                            (str(isbn), str(card_id), str(today_date), str(due_date)))
                con.commit()
                cur.execute(f"SELECT * FROM {LOANS_TABLE} WHERE Isbn = " + str(isbn) + " AND Date_in IS NULL")
                con.commit()
                loan_id = cur.fetchone()[0]
                print(f"loan_id: {loan_id}")

                cur.execute(f"INSERT INTO {FINES_TABLE}(Loan_id) VALUES(" + str(loan_id) + ")")
                con.commit()

                issued.append(str(isbn))
                print(f"Done: {isbn}")
            except Exception as e:
                print(f"Failed to issue Book, Book Details -> book_isbn: {isbn}, book_name: {result_list[index][1]}")
                print(e)
                not_issued.append(str(isbn))
    else:
        messagebox.showinfo("Error", "No. of selected books + No. of issued books > 3. Please select lesser books")
        master.destroy()

    if not not_issued:
        messagebox.showinfo("Success", f"Succesfully Issued Books: {','.join(issued)}")
    else:
        messagebox.showinfo("Failure", f"Failed to issue book(s): {','.join(not_issued)}")

    master.destroy()


def get_card_number_page():
    global listbox, main_canvas, card_id_label, card_id_entry, issue_button, exit_button, entry_frame

    main_canvas.destroy()
    main_canvas = create_canvas(master, background="burlywood3")

    create_label(master, text="ISSUE BOOK", foreground='tan4', x_pos=0.25, y_pos=0.05, rel_width=0.5, rel_height=0.5, background="burlywood3", font=("Helvetica", 30, "bold"))

    # Creating Label and Entry for accepting card_id
    card_id_label, card_id_entry = create_label_entry(master, text="CARD ID: ", background='burlywood3',
                                                      foreground='tan4',
                                                      label_x_pos=0.05, entry_x_pos=0.2, y_pos=0.6, rel_width=0.62, font=("Helvetica", 15, "bold"))

    # Issue Button
    issue_button = create_button(master, text="Issue", background='#d1ccc0', foreground='black', command=issue,
                                 x_pos=0.28, y_pos=0.75, rel_width=0.18, rel_height=0.08)

    exit_button = create_button(master, text="Exit", background='#aaa69d', foreground='black', command=master.destroy,
                                x_pos=0.53, y_pos=0.75, rel_width=0.18, rel_height=0.08)


def on_select(event):
    global tree, selected_ids

    # Get the treeview widget from the event
    tree = event.widget
    last_selected_id = tree.identify_row(event.y)
    print(f"Recent Id is {tree.index(last_selected_id)}")
    if last_selected_id:
        if last_selected_id in tree.selection():
            tree.selection_remove(last_selected_id)
        else:
            tree.selection_add(last_selected_id)

    # Get the availability of the last selected Treeview item
    availability = tree.item(last_selected_id, 'values')[4]
    print(f"Availability is {availability}")

    # If availability is "No", deselect it
    if availability.lower() == "no":
        tree.selection_remove(last_selected_id)
        print(f"Book not available.")
        messagebox.showwarning("Warning", "Cannot select unavailable books")
        return

    # Get the selected items
    selected_ids = tree.selection()
    selected_indices = [tree.index(id) for id in selected_ids]
    print(f"Selected indices are {selected_indices}")

    # Limit the selection to 3 items
    if len(selected_ids) > 3:
        tree.selection_remove(last_selected_id)
        messagebox.showwarning("Warning", "Cannot select more than 3 entries at a time")
        print("You can select up to 3 items only.")
        return


# def search_by_attribute(attribute_name, search_value, pattern_type="string"):
def search_by_attribute(search_query):
    global serial_no, result_list, tree

    # attribute_str = f"{attribute_name}"
    # if pattern_type == "int":
    #     attribute_str = f"CAST({attribute_name} AS CHAR)"
    #
    # search_query = f"SELECT * FROM {BOOK_TABLE} WHERE {attribute_str} LIKE '%{search_value}%'"

    # SELECT * FROM {BOOK_TABLE} WHERE Isbn LIKE '%Harry Potter%' or
    print(search_query)
    cur.execute(search_query)
    con.commit()
    matched_entries = cur.fetchall()

    # Author_id Isbn Author_id Name Isbn Title
    # SELECT * FROM BOOK WHERE CAST(Isbn AS CHAR) LIKE '%9789999364492%';
    for entry in matched_entries:
        available = "No"
        isbn = entry[0]
        title = entry[1]
        authors = entry[2]
        result = cur.execute(f"SELECT * FROM {LOANS_TABLE} WHERE Isbn = {str(isbn)} AND Date_in IS NULL")
        if not result:
            available = "Yes"
        tree.insert('', tk.END, values=((f"{serial_no}", isbn, title, authors, available)))
        result_list.append((isbn, title, authors, available))
        serial_no = serial_no + 1


def search():
    global search_bar_frame, search_entry, tree, result_list, serial_no

    result_list = []
    serial_no = 1
    search_pattern = search_entry.get()

    if not search_pattern:
        messagebox.showerror("Invalid", "Empty search pattern not allowed, Please enter a valid search pattern")
        return

    search_bar_frame = Frame(master, bg='tan4')

    # Creating a treeview
    tree = ttk.Treeview(search_bar_frame, show='headings', selectmode='none')

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

    # SELECT * FROM BOOK WHERE Title LIKE '%Harry Potter%' OR Author_Names LIKE '%Harry Potter%'

    # attribute_str = f"{attribute_name}"
    # if pattern_type == "int":
    #     attribute_str = f"CAST({attribute_name} AS CHAR)"
    #
    # search_query = f"SELECT * FROM {BOOK_TABLE} WHERE {attribute_str} LIKE '%{search_value}%'"

    search_query = f"SELECT * FROM {BOOK_TABLE} WHERE Title LIKE '%{search_pattern}%' OR Author_Names LIKE '%{search_pattern}%'"

    if not search_pattern.isdigit():
        print("Skipping search by isbn because given search pattern is not an integer")
    else:
        search_query += f" OR CAST(Isbn AS CHAR) LIKE '%{search_pattern}%'"

    print(f"Search query: {search_query}")

    # Execute search query
    try:
        print("Executing search query")
        search_by_attribute(search_query)
    except Exception as e:
        print(f"Search failed with exception {e}")

    # search by isbn
    # try:
    #     if not search_pattern.isdigit():
    #         print("Skipping search by isbn because given search pattern is not an integer")
    #     else:
    #         print("Searching by isbn value")
    #         search_by_attribute("Isbn", search_pattern, "int")
    # except Exception as e:
    #     print(f"Search by Isbn failed with exception {e}")
    #
    # # search by Title
    # try:
    #     print("Searching by Book Title")
    #     search_by_attribute("Title", search_pattern)
    # except Exception as e:
    #     print(f"Search by Title failed with exception {e}")
    #
    # # search by Authors
    # try:
    #     print("Searching by Author Names")
    #     search_by_attribute("Author_Names", search_pattern)
    # except Exception as e:
    #     print(f"Search by Author Names failed with exception {e}")

    for entry in result_list:
        print(entry)
    print(f"No. of book entries matching the given search: {len(result_list)}")

    if not tree.size():
        messagebox.showinfo("INFO", "No books with matching Isbn/Title/Author_Names Pattern")
        return

    search_bar_frame.place(relx=0.02, rely=0.15, relwidth=0.96, relheight=0.7)

    # Add vertical scrollbar
    vscroll = ttk.Scrollbar(search_bar_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vscroll.set)
    vscroll.pack(side='right', fill='y')

    # Add horizontal scrollbar
    hscroll = ttk.Scrollbar(search_bar_frame, orient="horizontal", command=tree.xview)
    tree.configure(xscrollcommand=hscroll.set)
    hscroll.pack(side='bottom', fill='x')

    # Pack the Treeview
    tree.pack(side='left', fill='both', expand=True)

    tree.bind('<ButtonRelease-1>', on_select)
    # tree.bind('<<TreeviewSelect>>', on_select)

    create_button(master, text="Issue", background='black', foreground='#333945', command=get_card_number_page,
                  x_pos=0.30, y_pos=0.85, rel_width=0.18, rel_height=0.08)

    try:
        # Destroy back button if already exists
        back_button.destroy()
    except Exception as e:
        print("Back button doesn't exist")

    create_button(master, text="Back", background='#455A64', foreground='#333945', command=master.destroy,
                  x_pos=0.53, y_pos=0.85, rel_width=0.18, rel_height=0.08)


def load_search_page():
    global master, main_canvas, title_frame, inner_title_frame
    global search_bar_frame, search_label, search_entry, search_button, back_button

    master = create_master()
    main_canvas = create_canvas(master, background="burlywood3")

    search_label, search_entry = create_label_entry(master, text="BOOK SEARCH : ", background='burlywood3',
                                                    foreground='tan4',
                                                    label_x_pos=0.02, entry_x_pos=0.22, y_pos=0.05, rel_width=0.54,
                                                    font=("Helvetica", 15, "bold"))

    # Search Button
    search_button = create_button(master, text="SEARCH", background='snow', foreground='black',
                                  command=search,
                                  x_pos=0.80, y_pos=0.05, rel_width=0.18, rel_height=0.05)

    # Search Button
    back_button = create_button(master, text="Back", background='snow', foreground='black',
                                  command=master.destroy,
                                  x_pos=0.40, y_pos=0.85, rel_width=0.18, rel_height=0.05)

    master.mainloop()
