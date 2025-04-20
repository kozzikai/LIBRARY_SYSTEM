from search_book import *
from check_in import *
from pay_fines import *
from borrower_management import *
from display_borowers import *
from utils import *


def employee_menu(master, canvas):

    global main_canvas
    canvas.destroy()

    refresh()
    main_canvas = create_canvas(master, background="burlywood3")

    # Employee Menu Label
    label = Label(master, text="EMPLOYEE MENU", fg='tan4', bg="burlywood3")
    label.config(font=("Helvetica", 40, "bold"))
    label.place(relx=0.25, rely=0.10, relwidth=0.5, relheight=0.1)

    # Add Borrowers
    add_borrower_btn = Button(master,
                              text="ADD BORROWER",
                              bg='snow',
                              fg='black',
                              command=get_borrower_data)
    add_borrower_btn.config(borderwidth=0, relief="flat", highlightthickness=0)
    add_borrower_btn.place(relx=0.28, rely=0.25, relwidth=0.45, relheight=0.1)

    # Display Borrowers
    add_borrower_btn = Button(master,
                              text="DISPLAY BORROWER DETAILS",
                              bg='snow',
                              fg='black',
                              command=borrowers_search_page)
    add_borrower_btn.config(borderwidth=0, relief="flat", highlightthickness=0)
    add_borrower_btn.place(relx=0.28, rely=0.35, relwidth=0.45, relheight=0.1)

    # Search Book Button
    search_book_btn = Button(master,
                             text="CHECK-OUT BOOK",
                             bg='snow',
                             fg='black',
                             command=load_search_page)
    search_book_btn.config(borderwidth=0, relief="flat", highlightthickness=0)
    search_book_btn.place(relx=0.28, rely=0.45, relwidth=0.45, relheight=0.1)

    # Check-In Book Button
    checkin_book_btn = Button(master,
                              text="CHECK-IN BOOK",
                              bg='snow',
                              fg='black',
                              command=loans_search_page)
    checkin_book_btn.config(borderwidth=0, relief="flat", highlightthickness=0)
    checkin_book_btn.place(relx=0.28, rely=0.55, relwidth=0.45, relheight=0.1)

    # Refresh Fines Button
    refresh_fines_btn = Button(master,
                               text="REFRESH FINES",
                               bg='snow',
                               fg='black',
                               command=display_fines)
    refresh_fines_btn.config(borderwidth=0,
                             relief="flat",
                             highlightthickness=0)
    refresh_fines_btn.place(relx=0.28, rely=0.65, relwidth=0.45, relheight=0.1)

    # Pay Fine Button
    pay_fine_btn = Button(master,
                          text="PAY FINE",
                          bg='snow',
                          fg='black',
                          command=load_card_number_page)
    pay_fine_btn.config(borderwidth=0, relief="flat", highlightthickness=0)
    pay_fine_btn.place(relx=0.28, rely=0.75, relwidth=0.45, relheight=0.1)
