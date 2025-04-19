from utils import *
from tkinter import ttk


def refresh():
    global today_date

    dict_cur.execute("SELECT CURDATE()")
    con.commit()
    today_date = dict_cur.fetchone()["CURDATE()"]
    print("today's date:")
    print(today_date)
    dict_cur.execute(f"SELECT * FROM {LOANS_TABLE} WHERE Date_in IS NULL")
    con.commit()
    existing_loans = dict_cur.fetchall()
    for loan_entry in existing_loans:
        print(f"\n\n***Entry***")
        date_out = loan_entry["Date_out"]
        due_date = loan_entry["Due_date"]
        loan_id = loan_entry['Loan_id']
        print(f"Date_out: {date_out}, Due_date: {due_date}")

        dict_cur.execute("SELECT DATEDIFF('" + str(today_date) + "','" + str(due_date) + "') AS days")
        con.commit()
        date_diff = dict_cur.fetchone()["days"]
        print(f"difference: {date_diff}")

        if date_diff > 0:
            fine = date_diff * 0.25
            print(f"loan_id: {loan_id}, fine: {fine}")
            dict_cur.execute(f"UPDATE {FINES_TABLE} SET Fine_amt = " + str(fine) + " WHERE Loan_id = " + str(loan_id))
            con.commit()


def display_fines():
    try:
        refresh()
    except Exception as e:
        messagebox.showinfo("Error", "Refresh Fines Failed")
        return

    # Display Fines grouped by card id
    dict_cur.execute(f"SELECT L.Card_id, SUM(F.Fine_amt) as Total_Fine, AVG(F.Paid) as Paid FROM {LOANS_TABLE} AS L,"
                     f"{FINES_TABLE} AS F WHERE L.Loan_id = F.Loan_id GROUP BY L.Card_id")
    # SELECT L.Card_id, SUM(F.Fine_amt) as Total_Fine, AVG(F.Paid) as Paid FROM BOOK_LOANS AS L,FINES AS F WHERE L.Loan_id = F.Loan_id GROUP BY L.Card_id
    con.commit()
    fines_list = dict_cur.fetchall()

    if fines_list:
        for fine in fines_list:
            print(fine)

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

    print(f"Headers {fines_list[0]}")
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


