from utils import *

logger = logging.getLogger("REFRESH FINES")
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


def refresh():
    global today_date

    dict_cur.execute("SELECT CURDATE()")
    con.commit()
    today_date = dict_cur.fetchone()["CURDATE()"]

    dict_cur.execute(
        f"SELECT * FROM {LOANS_TABLE} AS L JOIN FINES AS F USING (Loan_id)"
        f"WHERE  Date_in IS NULL OR (Date_in > Due_date AND F.Paid = 0)")

    con.commit()
    existing_fines = dict_cur.fetchall()
    for loan_entry in existing_fines:
        date_out = loan_entry["Date_out"]
        due_date = loan_entry["Due_date"]
        date_in = loan_entry["Date_in"]
        loan_id = loan_entry['Loan_id']

        if date_in:
            # For book loans which have been returned already but there are unpaid fines on them
            dict_cur.execute("SELECT DATEDIFF('" + str(date_in) + "','" +
                             str(due_date) + "') AS days")
        else:
            # For book loans which haven't been returned till date
            dict_cur.execute("SELECT DATEDIFF('" + str(today_date) + "','" +
                             str(due_date) + "') AS days")

        con.commit()
        date_diff = dict_cur.fetchone()["days"]

        if date_diff > 0:
            fine = date_diff * 0.25
            logger.info(f"Current Fine on loan_id {loan_id} is {fine}")
            dict_cur.execute(f"UPDATE {FINES_TABLE} SET Fine_amt = " +
                             str(fine) + " WHERE Loan_id = " + str(loan_id))
            con.commit()
        else:
            logger.info(f"No pending Fines on loan_id {loan_id}")
            dict_cur.execute(
                f"UPDATE {FINES_TABLE} SET Fine_amt = 0 WHERE Loan_id = " +
                str(loan_id))
            con.commit()


def display_fines():
    try:
        refresh()
    except Exception as e:
        messagebox.showinfo("Error", "Refresh Fines Failed")
        return

    # Display Fines grouped by card id
    dict_cur.execute(
        f"SELECT L.Card_id, SUM(F.Fine_amt) as Total_Fine, 'No' as Paid FROM {LOANS_TABLE} AS L,"
        f"{FINES_TABLE} AS F WHERE L.Loan_id = F.Loan_id AND F.Fine_amt > 0 AND FLOOR(F.Paid) = 0 GROUP BY L.Card_id"
    )
    con.commit()
    fines_list = dict_cur.fetchall()
    logger.info("Refresh Fines Completed.")
    if not fines_list:
        logger.info("No existing fines to display")
        messagebox.showinfo(
            "INFO", "Refresh Fines Completed. No existing fines to display")
        return

    master = create_master(title="FINES")

    frame = Frame(master)
    frame.pack(fill='both', expand='yes')

    canvas = Canvas(frame)
    scrollbar = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side='left', fill='both', expand='yes')
    scrollbar.pack(side='right', fill='y')

    canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')

    headers = fines_list[0].keys()
    for column, header in enumerate(headers):
        label = Label(scrollable_frame, text=header, font=('bold', 10))
        label.grid(row=0, column=column, padx=5, pady=5)

    for row, entry in enumerate(fines_list, start=1):
        for column, (header, value) in enumerate(entry.items()):
            label = Label(scrollable_frame, text=value)
            label.grid(row=row, column=column, padx=5, pady=5)

    button = Button(master, text="Close", command=master.destroy)
    button.pack()

    scrollable_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox('all'))
    master.mainloop()
