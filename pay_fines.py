from refresh_fines import *

def pay():
    print("Payment Done")
    print(f"loan_ids : {loan_ids}")
    try:
        # UPDATE FINES SET Paid = 0 WHERE Loan_id in (16,17,18) AND Fine_amt > 0 AND FLOOR(Paid) = 1;
        update_fines_query = f"UPDATE {FINES_TABLE} SET Paid = 1 WHERE Loan_id in ({','.join(loan_ids)}) AND Fine_amt > 0 AND FLOOR(Paid) = 0"
        cur.execute(update_fines_query)
        con.commit()
    except Exception as e:
        print(e)
        messagebox.showinfo("Failure", "Payment Update Failed, please try again")
        master.destroy()

    messagebox.showinfo("Success", "Fine Payment Successful")
    master.destroy()


def display_fine_by_card_id():
    global card_id, loan_ids
    loan_ids = []
    card_id = card_id_entry.get()

    dict_cur.execute("SELECT CURDATE()")
    con.commit()
    today_date = dict_cur.fetchone()["CURDATE()"]

    existing_loans = cur.execute(
        f"SELECT * FROM {LOANS_TABLE} WHERE Card_id = {card_id} AND Date_in IS NULL AND '{today_date}' > Due_date")
    con.commit()
    print(existing_loans)

    # SELECT SUM(F.Fine_amt) as Total_Fine, FLOOR(AVG(F.Paid)) as Paid FROM BOOK_LOANS AS L, FINES AS F WHERE L.Loan_id = F.Loan_id AND Card_id = 123 AND FLOOR(F.Paid) = 0 GROUP BY L.Card_id;
    # Get Fine Details for the given card_id
    existing_fine_count = dict_cur.execute(
        f"SELECT SUM(F.Fine_amt) as Total_Fine, FLOOR(AVG(F.Paid)) as Paid FROM {LOANS_TABLE} AS L,"
        f"{FINES_TABLE} AS F WHERE L.Loan_id = F.Loan_id AND Card_id = {card_id} AND FLOOR(F.Paid) = 0 GROUP BY L.Card_id")
    con.commit()

    if not existing_loans or not existing_fine_count:
        messagebox.showinfo("FAILURE", f"No existing fines for card_id {card_id}")
        master.destroy()
        return

    fine_amount = dict_cur.fetchall()[0]["Total_Fine"]
    print(f"Fine amount : {fine_amount}")

    # SELECT * FROM BOOK_LOANS AS L JOIN FINES AS F USING (Loan_id) WHERE Card_id = 123 AND F.Fine_amt > 0 AND FLOOR(F.Paid) = 0;
    # Get Fine Details for the given card_id
    dict_cur.execute(
        f"SELECT * FROM BOOK_LOANS AS L JOIN FINES AS F USING (Loan_id)"
        f"WHERE Card_id = {card_id} AND F.Fine_amt > 0 AND FLOOR(F.Paid) = 0")
    con.commit()
    fines_list = dict_cur.fetchall()

    loan_ids = [str(fine_entry["Loan_id"]) for fine_entry in fines_list]
    print(f"loan_ids: {loan_ids}")

    main_canvas.destroy()
    frame = Frame(master)
    frame.pack(fill='both', expand='yes')

    canvas = Canvas(frame)
    scrollbar = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side='left', fill='both', expand='yes')
    scrollbar.pack(side='right', fill='y')

    canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')

    print(f"Headers {fines_list[0]}")
    headers = fines_list[0].keys()
    for column, header in enumerate(headers):
        label = Label(scrollable_frame, text=header, font=('bold', 10))
        label.grid(row=0, column=column, padx=5, pady=5)

    for row, entry in enumerate(fines_list, start=1):
        for column, (header, value) in enumerate(entry.items()):
            label = Label(scrollable_frame, text=value)
            label.grid(row=row, column=column, padx=5, pady=5)

    if existing_loans > 0:
        messagebox.showerror("FAILURE", "Please return back books that crossed due date before paying the fine")
        master.destroy()
        return

    button = Button(master, text=f"Pay Fine: {fine_amount}", command=pay)
    button.pack()

    scrollable_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox('all'))

    master.mainloop()


def load_card_number_page():
    global listbox, main_canvas, card_id_label, card_id_entry, get_fine_button, exit_button, entry_frame, master

    master = create_master()
    main_canvas = create_canvas(master, background="#706fd3")

    title_frame = create_frame(master, background="#333945", x_pos=0.25, y_pos=0.1, rel_width=0.5, rel_height=0.13,
                               border_width=5)
    inner_title_frame = create_frame(title_frame, background="#EAF0F1", x_pos=0.01, y_pos=0.05, rel_width=0.98,
                                     rel_height=0.9)

    create_label(inner_title_frame, text="PAY FINE", foreground='black', x_pos=0.25,
                 y_pos=0.15, rel_width=0.5, rel_height=0.5)

    entry_frame = create_frame(master, background='black', x_pos=0.1, y_pos=0.3, rel_width=0.8,
                               rel_height=0.3)

    # Creating Label and Entry for accepting card_id
    card_id_label, card_id_entry = create_label_entry(entry_frame, text="Card ID : ", background='black',
                                                      foreground='white',
                                                      label_x_pos=0.05, entry_x_pos=0.3, y_pos=0.2, rel_width=0.62)

    # Issue Button
    get_fine_button = create_button(master, text="FIND", background='#d1ccc0', foreground='black', command=display_fine_by_card_id,
                                    x_pos=0.28, y_pos=0.75, rel_width=0.18, rel_height=0.08)

    exit_button = create_button(master, text="Exit", background='#aaa69d', foreground='black', command=master.quit,
                                x_pos=0.53, y_pos=0.75, rel_width=0.18, rel_height=0.08)

    master.mainloop()
