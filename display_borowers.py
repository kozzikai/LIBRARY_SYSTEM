from refresh_fines import *

logger = logging.getLogger("SEARCH-BORROWERS")
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


def search_borrowers():
    global tree, back_button, matched_borrowers, result_frame

    try:
        logger.info(
            f"Trying to remove previously loaded search results if they exist")
        result_frame.destroy()
    except Exception as e:
        logger.info(f"No previously loaded search results to remove")

    matched_borrowers = []
    search_pattern = search_entry.get()

    result_frame = Frame(master, bg='black')

    # Creating a treeview
    tree = ttk.Treeview(result_frame, show='headings', selectmode='none')

    # Define the columns
    tree['columns'] = ('CARD_ID', 'SSN', 'BORROWER_NAME', 'ADDRESS', 'PHONE')

    # Get the default font
    default_font = font.nametofont("TkDefaultFont")

    # Measure the width of the character '0'
    char_width = default_font.measure('0')

    # Format the columns to match the new column names and desired widths
    tree.column('CARD_ID', anchor=W, width=10 * char_width)
    tree.column('SSN', anchor=W, width=15 * char_width)
    tree.column('BORROWER_NAME', anchor=W, width=40 * char_width)
    tree.column('ADDRESS', anchor=W, width=50 * char_width)
    tree.column('PHONE', anchor=W, width=15 * char_width)

    # Create Headings to match the new column names
    tree.heading('CARD_ID', text='CARD ID', anchor=W)
    tree.heading('SSN', text='SSN', anchor=W)
    tree.heading('BORROWER_NAME', text='BORROWER NAME', anchor=W)
    tree.heading('ADDRESS', text='ADDRESS', anchor=W)
    tree.heading('PHONE', text='PHONE NUMBER', anchor=W)

    search_query = f"SELECT * FROM {BORROWER_TABLE} WHERE Bname LIKE '%{search_pattern}%' OR Address LIKE '%{search_pattern}%' OR Phone LIKE '%{search_pattern}%' OR Ssn LIKE '%{search_pattern}%'"

    if search_pattern.isdigit():
        if len(search_pattern) == 9:
            ssn_string = convert_to_ssn_format(search_pattern)
            search_query += f" OR CAST(Ssn AS CHAR) LIKE '%{ssn_string}%'"
        if len(search_pattern) == 10:
            phone_string = convert_to_phone_format(search_pattern)
            search_query += f" OR CAST(Phone AS CHAR) LIKE '%{phone_string}%'"

    # Execute search query
    try:
        logger.info(f"Executing search Query: \n{search_query}")
        dict_cur.execute(search_query)
        con.commit()
        matched_borrowers = dict_cur.fetchall()
    except Exception as e:
        logger.error(f"Loan search failed with exception {e}")

    # Now we insert the data into the Treeview
    for borrower in matched_borrowers:
        tree.insert('',
                    END,
                    values=(borrower["Card_id"], borrower["Ssn"],
                            borrower["Bname"], borrower["Address"],
                            borrower["Phone"]))

    result_frame.place(relx=0.02, rely=0.15, relwidth=0.96, relheight=0.7)

    # Add vertical scrollbar
    vscroll = ttk.Scrollbar(result_frame,
                            orient="vertical",
                            command=tree.yview)
    tree.configure(yscrollcommand=vscroll.set)
    vscroll.pack(side='right', fill='y')

    # Add horizontal scrollbar
    hscroll = ttk.Scrollbar(result_frame,
                            orient="horizontal",
                            command=tree.xview)
    tree.configure(xscrollcommand=hscroll.set)
    hscroll.pack(side='bottom', fill='x')

    # Pack the Treeview
    tree.pack(side='left', fill='both', expand=True)
    result_frame.update_idletasks()

    if not tree.get_children():
        messagebox.showinfo(
            "INFO",
            "No borrowers with matching Ssn/Bname/Address/Phone Pattern")


def borrowers_search_page():
    global master, main_canvas, search_bar_frame, search_label, search_entry, search_button, back_button

    master = create_master()

    main_canvas = create_canvas(master, background="burlywood3")

    # Creating Label and Entry for accepting search pattern
    search_label, search_entry = create_label_entry(master,
                                                    text="BORROWER INFO : ",
                                                    background='burlywood3',
                                                    foreground='tan4',
                                                    label_x_pos=0.02,
                                                    entry_x_pos=0.23,
                                                    y_pos=0.05,
                                                    rel_width=0.54,
                                                    font=("Helvetica", 15,
                                                          "bold"))

    # Search Button
    search_button = create_button(master,
                                  text="SEARCH",
                                  background='snow',
                                  foreground='black',
                                  command=search_borrowers,
                                  x_pos=0.80,
                                  y_pos=0.05,
                                  rel_width=0.18,
                                  rel_height=0.05)

    # back Button
    back_button = create_button(master,
                                text="BACK",
                                background='snow',
                                foreground='black',
                                command=master.destroy,
                                x_pos=0.40,
                                y_pos=0.90,
                                rel_width=0.18,
                                rel_height=0.05)

    master.mainloop()
