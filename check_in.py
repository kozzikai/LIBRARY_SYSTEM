from refresh_fines import *


def check_in():
    selected_book_index = listbox.curselection()[0]
    print(selected_book_index)

    refresh()

    # Display -> Loan_id Isbn Card_id Bname Date_out Due_date Date_in
    loan_id = result_list[selected_book_index][0]

    cur.execute("SELECT CURDATE()")
    con.commit()
    curr_date = cur.fetchone()[0]

    try:
        cur.execute(f"UPDATE {LOANS_TABLE} SET Date_in = '{str(curr_date)}' WHERE Loan_id = {loan_id}")
        con.commit()
        messagebox.showinfo("Success", "Successfully Checked in Book")
    except Exception as e:
        messagebox.showinfo("Failed", "Failed to Check-In Book")

    master.destroy()


def search_loans_by_attribute(search_query):
    global result_list, listbox

    cur.execute(search_query)
    con.commit()
    matched_entries = cur.fetchall()

    # Display -> Loan_id Isbn Card_id Bname Date_out Due_date Date_in
    for entry in matched_entries:
        listbox.insert(END,
                       f"{str(entry[0])}          {str(entry[1]):<10}  {str(entry[2]):<5}  {str(entry[8]):<80}  {str(entry[3]):<10}  {str(entry[4]):<10}  {str(entry[5]):<10}")
        result_list.append([entry[0], entry[1], entry[2], entry[8], entry[3], entry[4], entry[5]])


def search_loan():
    global listbox, result_list, check_in_button, exit_button, result_frame


    result_list = []
    search_pattern = search_entry.get()

    result_frame = Frame(master, bg='black')
    scrollbar = Scrollbar(result_frame)

    # Creating a Listbox
    listbox = Listbox(result_frame, yscrollcommand=scrollbar.set, width=300, selectmode=SINGLE, bg='black', fg='white')

    search_query = f"SELECT * FROM {LOANS_TABLE} AS L,{BORROWER_TABLE} AS B WHERE L.Card_id = B.Card_id AND (B.Bname LIKE '%{search_pattern}%'"
    if not search_pattern.isdigit():
        print("Skipping search by isbn and card number because given search pattern is not an integer")
    else:
        search_query += f" OR CAST(L.Isbn AS CHAR) LIKE '%{search_pattern}%' OR CAST(L.Card_id AS CHAR) LIKE '%{search_pattern}%'"
    search_query += f") AND Date_in IS NULL"
    print(f"Search Query is:\n {search_query}")

    # Execute search query
    try:
        print("Executing search query")
        search_loans_by_attribute(search_query)
    except Exception as e:
        print(f"Loan search failed with exception {e}")

    # # search by isbn
    # try:
    #
    #     if not search_pattern.isdigit():
    #         print("Skipping search by isbn because given search pattern is not an integer")
    #     else:
    #         print("Searching by isbn value")
    #         search_query = f"SELECT * FROM {LOANS_TABLE} AS L,{BORROWER_TABLE} AS B WHERE L.Card_id = B.Card_id AND CAST(L.Isbn AS CHAR) LIKE '%{search_pattern}%' AND Date_in IS NULL"
    #         search_loans_by_attribute(search_query)
    # except Exception as e:
    #     print(f"Search by Isbn failed with exception {e}")
    #
    # # search by card number
    # try:
    #     if not search_pattern.isdigit():
    #         print("Skipping search by card number because given search pattern is not an integer")
    #     else:
    #         print("Searching by Card Number")
    #         search_query = f"SELECT * FROM {LOANS_TABLE} AS L,{BORROWER_TABLE} AS B WHERE L.Card_id = B.Card_id AND CAST(L.Card_id AS CHAR) LIKE '%{search_pattern}%' AND Date_in IS NULL"
    #         search_loans_by_attribute(search_query)
    # except Exception as e:
    #     print(f"Search by Card Number with exception {e}")
    #
    # # search by Borrower Name
    # try:
    #     print("Searching by Borrower Name")
    #     search_query = f"SELECT * FROM {LOANS_TABLE} AS L,{BORROWER_TABLE} AS B WHERE L.Card_id = B.Card_id AND B.Bname LIKE '%{search_pattern}%' AND Date_in IS NULL"
    #     search_loans_by_attribute(search_query)
    # except Exception as e:
    #     print(f"Search by Borrower Name failed with exception {e}")

    for entry in result_list:
        print(entry)
    print(f"No. of book entries matching the given search: {len(result_list)}")

    if not listbox.size():
        messagebox.showinfo("INFO", "No book loans with matching Isbn/Card Number/Borrower Name Pattern")
        return

    search_button.destroy()
    exit_button.destroy()
    search_label.destroy()
    search_entry.destroy()

    # Display -> Loan_id Isbn Card_id Bname Date_out Due_date Date_in
    Label(master,
          text=f"{'Loan_id':<5}  {'ISBN':<10}  {'Card_id':<5} {'Bname':<50} {'Date_out':<10} {'Due_date':<10} {'Date_in':<10}",
          anchor='w', bg='black',
          fg='white').place(relx=0.1, rely=0.28, relwidth=0.8)

    result_frame.place(relx=0.1, rely=0.3, relwidth=0.8, relheight=0.5)

    listbox.place(relx=0.05, rely=0.3)
    listbox.pack(side=LEFT, fill=Y)
    # listbox.pack(side=LEFT)

    # Configure Scroll Bar
    scrollbar.pack(side=RIGHT, fill=Y)
    scrollbar.config(command=listbox.yview)

    check_in_button = create_button(master, text="Check-In", background='#d1ccc0', foreground='black', command=check_in,
                                    x_pos=0.28, y_pos=0.85, rel_width=0.18, rel_height=0.08)

    exit_button = create_button(master, text="Back", background='#455A64', foreground='black', command=loans_search_page,
                                x_pos=0.53, y_pos=0.85, rel_width=0.18, rel_height=0.08)


def loans_search_page():
    global master, main_canvas, search_bar_frame, search_label, search_entry, search_button, exit_button

    master = create_master()
    main_canvas = create_canvas(master, background="#706fd3")

    title_frame = create_frame(master, background="#333945", x_pos=0.25, y_pos=0.1, rel_width=0.5, rel_height=0.13,
                               border_width=5)
    inner_title_frame = create_frame(title_frame, background="#EAF0F1", x_pos=0.01, y_pos=0.05, rel_width=0.98,
                                     rel_height=0.9)

    create_label(inner_title_frame, text="BOOK CHECKIN", foreground='black', x_pos=0.25,
                               y_pos=0.15, rel_width=0.5, rel_height=0.5)

    search_bar_frame = create_frame(master, background='black', x_pos=0.1, y_pos=0.3, rel_width=0.8,
                                     rel_height=0.3)

    # Creating Label and Entry for accepting search pattern
    search_label, search_entry = create_label_entry(search_bar_frame, text="Enter Search Pattern : ", background='black', foreground='white',
                                               label_x_pos=0.05, entry_x_pos=0.3, y_pos=0.2, rel_width=0.62)

    # Search Button
    search_button = create_button(master, text="Search", background='#d1ccc0', foreground='black',
                                    command=search_loan,
                                    x_pos=0.28, y_pos=0.75, rel_width=0.18, rel_height=0.08)

    exit_button = create_button(master, text="Exit", background='black', foreground='#333945',
                                    command=master.quit,
                                    x_pos=0.53, y_pos=0.75, rel_width=0.18, rel_height=0.08)

    master.mainloop()

# SELECT * FROM BOOK_LOANS AS L,BORROWER AS B WHERE L.Card_id = B.Card_id AND (B.Bname LIKE '%1%' OR CAST(L.Isbn AS CHAR) LIKE '%1%' OR CAST(L.Card_id AS CHAR) LIKE '%1%') AND Date_in IS NULL