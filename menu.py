from search_book_new import *
from check_in import *
from pay_fines import *
from borrower_management import *
from utils import *


def employee_menu(master, canvas):

    global main_canvas
    canvas.destroy()

    refresh()
    main_canvas = create_canvas(master, background="burlywood3")

    create_label(master, text="EMPLOYEE MENU", foreground='tan4', x_pos=0.25,y_pos=0.15, rel_width=0.5, rel_height=0.1, font=("Helvetica", 40, "bold"))

    # Register Button
    create_button(master, text="ADD BORROWER", background='snow', foreground='black',
                  command=get_borrower_data, x_pos=0.28, y_pos=0.3, rel_width=0.45, rel_height=0.1)

    create_button(master, text="SEARCH BOOK", background='snow', foreground='black',
                  command=load_search_page, x_pos=0.28, y_pos=0.4, rel_width=0.45, rel_height=0.1)

    create_button(master, text="CHECK-IN BOOK", background='snow', foreground='black',
                  command=loans_search_page, x_pos=0.28, y_pos=0.5, rel_width=0.45, rel_height=0.1)

    create_button(master, text="REFRESH FINES", background='snow', foreground='black',
                  command=display_fines, x_pos=0.28, y_pos=0.6, rel_width=0.45, rel_height=0.1)

    create_button(master, text="PAY FINE", background='snow', foreground='black',
                  command=load_card_number_page, x_pos=0.28, y_pos=0.7, rel_width=0.45, rel_height=0.1)
