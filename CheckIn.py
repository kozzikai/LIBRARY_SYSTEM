from tkinter import *
from tkinter import messagebox
import pymysql

LOANS_TABLE = "BOOK_LOANS"
BORROWERS_TABLE = "BORROWER"


con = pymysql.connect(host="localhost",user="root",password='MoMDaD924754*',database='LIBRARY_FINAL',unix_socket="/tmp/mysql.sock")
cur = con.cursor()

def refresh():
    global today_date
    try:
        cur.execute("SELECT CURDATE()")
        con.commit()
        today_date = cur.fetchone()[0]
        print("today's date:")
        print(today_date)
        cur.execute("SELECT * FROM BOOK_LOANS WHERE Date_in IS NULL")
        con.commit()
        existing_loans = cur.fetchall()
        for loan_entry in existing_loans:
            print("***Entry***")
            date_out = loan_entry[3]
            due_date = loan_entry[4]
            print(f"date_out: {date_out}, due_date: {due_date}")

            cur.execute("SELECT DATEDIFF('"+str(today_date)+"','"+str(loan_entry[3])+"') AS days")
            con.commit()
            date_diff = cur.fetchone()[0]
            print(f"difference: {date_diff}")

            if date_diff > 14:
                fine = date_diff[0]*0.25
                print("fine:")
                print(fine)      
                cur.execute("UPDATE FINES SET Fine_amt = "+str(fine)+" WHERE Loan_id = "+str(i[0]))
                con.commit()
            else:
                continue
                
        messagebox.showinfo("Success","Refresh Complete")        
    except:
        messagebox.showinfo("Error","Cannot Refresh")

def last():
    variable = en1.get()
    if variable.lower() == 'yes':
        cur.execute("UPDATE FINES SET Paid = True WHERE Loan_id = "+str(Loan_id))
        con.commit()
        cur.execute("UPDATE BOOK_LOANS SET Date_in = '"+str(today_date)+"' WHERE Loan_id = "+str(Loan_id))
        con.commit()
        messagebox.showinfo("Success","Book Checked in")
    else:
        messagebox.showinfo("Failed","Please collect fine first!")
   
        
def check():
    global labelFrame,checkBtn,en1, result_list

    selected_book_index = listbox.curselection()[0]
    print(selected_book_index)

    checkBtn.destroy()
    labelFrame.destroy()

    # Display -> Loan_id Isbn Card_id Bname Date_out Due_date Date_in
    loan_id = result_list[selected_book_index][0]
    print(f"loan_id: {loan_id}, isbn: {result_list[selected_book_index][1]}  {result_list[selected_book_index][4]} {result_list[selected_book_index][5]} {result_list[selected_book_index][6]}")

    refresh()

    cur.execute("SELECT CURDATE()")
    con.commit()
    curr_date = cur.fetchone()[0]

    # Get the corresponding loan_id entry from FINES table
    cur.execute(f"SELECT * FROM FINES WHERE Loan_id = {str(loan_id)}")
    con.commit()
    paid = cur.fetchone()[0]
    fine_amount = cur.fetchone()[1]
    if paid:
        cur.execute(f"UPDATE BOOK_LOANS SET Date_in = '{str(curr_date)}' WHERE Loan_id = {loan_id}")
        con.commit()
        messagebox.showinfo("Success","Successfully Checked in Book")
    else:
        labelFrame = Frame(root,bg='black')
        labelFrame.place(relx=0.1,rely=0.3,relwidth=0.8,relheight=0.3)

        lb1 = Label(labelFrame,text=f"Is {fine_amount} Fine Paid: ", bg='black', fg='white')
        lb1.place(relx=0.05,rely=0.2)

        en1 = Entry(labelFrame)
        en1.place(relx=0.3,rely=0.2, relwidth=0.62)

        checkBtn = Button(root,text="Confirm",bg='#d1ccc0', fg='black',command=lambda: last())
        checkBtn.place(relx=0.28,rely=0.85, relwidth=0.18,relheight=0.08)


def search_loans_by_attribute(search_query):
    global result_list, listbox

    cur.execute(search_query)
    con.commit()
    matched_entries = cur.fetchall()

    # Display -> Loan_id Isbn Card_id Bname Date_out Due_date Date_in
    for entry in matched_entries:
        listbox.insert(END, f"{str(entry[0]):<5}  {str(entry[1]):<10}  {str(entry[2]):<5}  {str(entry[8]):<80}  {str(entry[3]):<10}  {str(entry[4]):<10}  {str(entry[4]):<10}")
        result_list.append([entry[0], entry[1], entry[2], entry[8], entry[3], entry[4], entry[5]])


def bookCheckin():
    
    global quitBtn, labelFrame, found, checkBtn,Loan_id, listbox, result_list
    result_list = []
    found = False
    search_pattern = en1.get()
    

    labelFrame = Frame(root,bg='black')
    scrollbar = Scrollbar(labelFrame)

    # Creating a Listbox
    listbox = Listbox(labelFrame, yscrollcommand=scrollbar.set, width=300, selectmode=SINGLE, bg='black',fg='white')


    # search by isbn
    try:

        if not search_pattern.isdigit():
            print("Skipping search by isbn because given search pattern is not an integer")
        else:
            print("Searching by isbn value")
            # search_query = f"SELECT * FROM {LOANS_TABLE} WHERE CAST(Isbn AS CHAR) LIKE '%{search_pattern}%' AND Date_in IS NULL"
            search_query = f"SELECT * FROM {LOANS_TABLE} AS L,{BORROWERS_TABLE} AS B WHERE L.Card_id = B.Card_id AND CAST(L.Isbn AS CHAR) LIKE '%{search_pattern}%' AND Date_in IS NULL"
            search_loans_by_attribute(search_query)
    except Exception as e:
        print(f"Search by Isbn failed with exception {e}")

    # search by card number
    try:
        if not search_pattern.isdigit():
            print("Skipping search by card number because given search pattern is not an integer")
        else:
            print("Searching by Card Number")
            # search_query = f"SELECT * FROM {LOANS_TABLE} WHERE CAST(Card_id AS CHAR) LIKE '%{search_pattern}%' AND Date_in IS NULL"
            search_query = f"SELECT * FROM {LOANS_TABLE} AS L,{BORROWERS_TABLE} AS B WHERE L.Card_id = B.Card_id AND CAST(L.Card_id AS CHAR) LIKE '%{search_pattern}%' AND Date_in IS NULL"
            search_loans_by_attribute(search_query)
    except Exception as e:
        print(f"Search by Card Number with exception {e}")

    # search by Borrower Name
    try:
        print("Searching by Borrower Name")
        search_query = f"SELECT * FROM {LOANS_TABLE} AS L,{BORROWERS_TABLE} AS B WHERE L.Card_id = B.Card_id AND B.Bname LIKE '%{search_pattern}%' AND Date_in IS NULL"
        search_loans_by_attribute(search_query)
    except Exception as e:
        print(f"Search by Borrower Name failed with exception {e}")


    for entry in result_list:
        print(entry)
    print(f"No. of book entries matching the given search: {len(result_list)}")

    if not listbox.size():
        messagebox.showinfo("INFO", "No book loans with matching Isbn/Card Number/Borrower Name Pattern")
        return

    issueBtn.destroy()
    quitBtn.destroy()
    lb1.destroy()
    en1.destroy()

    # Display -> Loan_id Isbn Card_id Bname Date_out Due_date Date_in
    Label(root, text=f"{'Loan_id':<5}  {'ISBN':<10}  {'Card_id':<5} {'Bname':<50} {'Date_out':<10} {'Due_date':<10} {'Date_in':<10}", anchor='w', bg='black',
          fg='white').place(relx=0.1, rely=0.28)

    labelFrame.place(relx=0.1, rely=0.3, relwidth=0.8, relheight=0.5)


    listbox.place(relx=0.05, rely=0.3)
    listbox.pack(side=LEFT, fill=Y)
    # listbox.pack(side=LEFT)

    # Configure Scroll Bar
    scrollbar.pack(side=RIGHT, fill=Y)
    scrollbar.config(command=listbox.yview)


    checkBtn = Button(root,text="Confirm",bg='#d1ccc0', fg='black',command=check)
    checkBtn.place(relx=0.28,rely=0.85, relwidth=0.18,relheight=0.08)
    
    quitBtn = Button(root,text="< Back",bg='#455A64', fg='black', command=checkinBook)
    quitBtn.place(relx=0.53,rely=0.85, relwidth=0.18,relheight=0.08)

    
def checkinBook(): 
    
    global en1,issueBtn,lb1,labelFrame,quitBtn,Canvas1,root
    root = Tk()
    root.title("Library")
    root.minsize(width=400,height=400)
    root.geometry("600x500")
    
    Canvas1 = Canvas(root)
    
    Canvas1.config(bg="#706fd3",width = 500, height = 500)
    Canvas1.pack(expand=True,fill=BOTH)
    
    labelFrame = Frame(root,bg='black')
    labelFrame.place(relx=0.1,rely=0.3,relwidth=0.8,relheight=0.3)
        
    headingFrame1 = Frame(root,bg="#333945",bd=5)
    headingFrame1.place(relx=0.25,rely=0.1,relwidth=0.5,relheight=0.13)
        
    headingFrame2 = Frame(headingFrame1,bg="#EAF0F1")
    headingFrame2.place(relx=0.01,rely=0.05,relwidth=0.98,relheight=0.9)
        
    headingLabel = Label(headingFrame2, text="Checkin BOOK", fg='black')
    headingLabel.place(relx=0.25,rely=0.15, relwidth=0.5, relheight=0.5)   
        
    lb1 = Label(labelFrame,text="Enter Here : ", bg='black', fg='white')
    lb1.place(relx=0.05,rely=0.2)
        
    en1 = Entry(labelFrame)
    en1.place(relx=0.3,rely=0.2, relwidth=0.62)
    

    #checkin Button
    issueBtn = Button(root,text="Checkin",bg='#d1ccc0', fg='black',command=bookCheckin)
    issueBtn.place(relx=0.28,rely=0.75, relwidth=0.18,relheight=0.08)
    
    quitBtn = Button(root,text="Quit",bg='#aaa69d', fg='black', command=root.quit)
    quitBtn.place(relx=0.53,rely=0.75, relwidth=0.18,relheight=0.08)
    
    root.mainloop()
