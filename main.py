from menu import *

master = create_master()


main_canvas = create_canvas(master)

title_label = create_label(master, text="LIBRARY SYSTEM", foreground='tan4', x_pos=0.25, y_pos=0.2, rel_width=0.5, rel_height=0.5, background="burlywood3", font=("Helvetica", 40, "bold"))

continue_button = create_button(master, text="CONTINUE", background='tan4', foreground='burlywood3', command=lambda: employee_menu(master, main_canvas),x_pos=0.4, y_pos=0.8, rel_width=0.2, rel_height=0.1)

master.mainloop()
