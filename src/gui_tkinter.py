from dbmanager import Database
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog


class ToDoManagerGUI:
    def __init__(self, root: Tk) -> None:
        self.root = root

        # connect to database
        self.db = Database()

        # get all existing users in the users tables of the db
        self.existing_users = self.db.get_existing_users()

        # root (main) application window is created outside of the class
        # and commited as an attribute
        self.root.title("ToDo List Manager")

        # define the size of the root window
        self.root.geometry("800x400")

        # configure behaviour root frame columns and rows
        # must be defined, or notebook widget inside root wouldn't change when
        # scale of window changes
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)  # rows of "Add User" and
        # "Delete User" Button

        # creater Frame for "Add User" and "Delete User" buttons
        self.add_delete_user_buttons_frame = ttk.Frame(self.root)
        self.add_delete_user_buttons_frame.grid(row=0, column=0, sticky=E)

        # create buttons for "Add User" and "Delete User" outside the Tabs
        self.add_user_button = Button(
            self.add_delete_user_buttons_frame,
            text="Add User",
            width=10,
            command=self.add_user,
        )
        self.add_user_button.grid(row=0, column=0, pady=2.5, padx=(2, 1))

        self.delete_user_button = Button(
            self.add_delete_user_buttons_frame,
            text="Delete User",
            width=10,
            command=self.delete_user,
        )
        self.delete_user_button.grid(row=0, column=1, pady=2.5, padx=(1, 2))

        # create a Notebook object to create tabs for each user in it
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=1, column=0, sticky=(N, E, S, W), padx=5)
        self.notebook.bind("<<NotebookTabChanged>>", self.get_curr_user_name)

        # create a dictionary to store the distplay_listbox of every user
        # to make every tab independent of the others
        self.user_tabs = {}

        # define a variable for the text of the currently selected tab, which
        # is the user_name. The default is the general_user
        self.curr_sele_user_name = "general_user"

        # define styles for different displays
        self.style = ttk.Style()
        # styles for the display_frame
        self.style.configure("OpenList.TFrame", background="white")
        self.style.configure("ListboxFrame.TFrame", background="#d9d9d9")
        # styles for the todo task checkbuttons
        self.style.configure("ToDoCheck.TCheckbutton", background="white")

        # create tab for general_user, if no other users exist
        if not "general_user" in self.existing_users:
            print("Error! general_user is missing. Please check the database")
        elif len(self.existing_users) == 1:
            self.create_general_user_tab()
            self.root.update_idletasks()
        else:
            for user_name in self.existing_users[1:]:
                self.create_normal_user_tabs(user_name)

        # print(self.user_tabs)

    # define method for creating the inital general_user_tab
    def create_general_user_tab(self):
        general_user_tab = ttk.Frame(self.notebook)
        self.notebook.add(general_user_tab, text="Create first user")

        # configure rows and columns of general_user_tab to define their
        # behaviour
        general_user_tab.rowconfigure(0, weight=1)
        general_user_tab.columnconfigure(0, weight=1)

        # create a single button to create the first user
        create_first_user_button = Button(
            general_user_tab,
            text="Welcome to the ToDo Tasks List Manager!\nPlease click on this text field to create a first user to start managing your ToDo tasks.",
            command=self.add_first_user,
        )

        create_first_user_button.grid(row=0, column=0, padx=5, pady=5)

    # define method for adding the first user
    def add_first_user(self):
        temp_root = Toplevel(self.root)
        temp_root.withdraw()

        user_name = simpledialog.askstring(
            title="Add new User",
            prompt="Please enter a user name",
            parent=temp_root,
        )

        if user_name:
            self.db.create_new_user(user_name)
            temp_root.destroy()
            self.refresh_tabs()

    # define method for adding additional users, if the first user was already
    # created
    def add_user(self):
        user_name = simpledialog.askstring(
            title="Add new User",
            prompt="Please enter a unique user name",
            parent=self.root,
        )

        if user_name:
            self.db.create_new_user(user_name)
            self.refresh_tabs()  # Aktualisiere die Tabs

    def delete_user(self):
        user_name = simpledialog.askstring(
            title="Delete User",
            prompt="Please enter the name of the user you like to delete.",
            parent=self.root,
        )

        if user_name in self.existing_users:
            if not user_name == "general_user":
                self.db.delete_user(user_name)
                self.refresh_tabs()
            else:
                messagebox.showinfo(
                    title="Illegal Operation",
                    message="This user can not be deleted.",
                )

        else:
            messagebox.showinfo(
                title="Invalid User Name",
                message="The user name you entered does not exist.",
            )

    # define method for creating all user tabs
    def create_normal_user_tabs(self, user_name):
        user_tab = ttk.Frame(self.notebook)
        self.notebook.add(user_tab, text=user_name)

        # configure the user_tab to expand properly
        user_tab.columnconfigure(1, weight=1)
        user_tab.rowconfigure(0, weight=1)

        # set up a button frame widget with ttk to hold the button widgets
        # ttk has a newer, more modern look than tk
        button_frame = ttk.Frame(
            user_tab, padding=10, width=150
        )  # creates a frame with 'user_tab' as parent

        button_frame.grid(column=0, row=0, sticky=(N, E, S, W))

        # configure the buttonframe to expand properly
        button_frame.columnconfigure(0, weight=1)

        # create buttons
        open_list_button = Button(
            button_frame,
            text="Open ToDo List",
            width=22,
            command=lambda: self.list_selection_window(
                "open", self.curr_sele_user_name
            ),
        )
        open_list_button.grid(pady=5, padx=5)

        create_new_list_button = Button(
            button_frame,
            text="Create new ToDo List",
            width=22,
            command=self.create_new_todo_list,
        )
        create_new_list_button.grid(pady=5, padx=5)

        remove_list_button = Button(
            button_frame,
            text="Remove ToDo List",
            width=22,
            command=lambda: self.list_selection_window(
                "remove", self.curr_sele_user_name
            ),
        )
        remove_list_button.grid(pady=5, padx=5)

        modify_existing_list_button = Button(
            button_frame,
            text="Modify ToDo List",
            width=22,
            command=lambda: self.list_selection_window(
                "modify", self.curr_sele_user_name
            ),
        )
        modify_existing_list_button.grid(pady=5, padx=5)

        show_all_tasks_button = Button(
            button_frame,
            text="Show all ToDo Tasks",
            width=22,
            command=self.show_all_tasks,
        )
        show_all_tasks_button.grid(pady=5, padx=5)

        add_task_button = Button(button_frame, text="Add new Task", width=22)
        add_task_button.grid(pady=5, padx=5)

        remove_task_button = Button(button_frame, text="Remove Task", width=22)
        remove_task_button.grid(pady=5, padx=5)

        # set up a frame widget to hold a display widget
        display_frame = ttk.Frame(user_tab, padding=10)
        display_frame.grid(column=1, row=0, sticky=(N, S, E, W))

        # configure the displayframe to expand properly
        display_frame.columnconfigure(0, weight=1)
        # display_frame.rowconfigure(0, weight=1)

        # create display
        display_listbox = Listbox(display_frame, height=15)
        display_listbox.grid(row=0, column=0, sticky=(N, E, S, W))

        # create and configure scrollbar
        scrollbar = Scrollbar(
            display_frame,
            orient=VERTICAL,
            command=display_listbox.yview,
        )
        scrollbar.grid(row=0, column=1, sticky=(N, S))

        # link scrollbar to the listbox
        display_listbox.configure(yscrollcommand=scrollbar.set)

        # save display_frame and listbox in a dictionary to make each user_tab
        # independent
        self.user_tabs[user_name] = {
            "listbox": display_listbox,
            "frame": display_frame,
        }

    def refresh_tabs(self):
        # remove all existing tabs
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)

        # refresh the list of users from the database
        self.existing_users = self.db.get_existing_users()

        # renew tabs based on the refreshed list of users
        if (
            len(self.existing_users) == 1
            and "general_user" in self.existing_users
        ):
            self.create_general_user_tab()
        else:
            for user_name in self.existing_users[1:]:
                self.create_normal_user_tabs(user_name)

    # define a  method to get the text of the currently selected tab, which is
    # the current user_name
    def get_curr_user_name(self, event):
        curr_sele_tab = event.widget.select()
        if curr_sele_tab:
            tab_text = event.widget.tab(curr_sele_tab, "text")
            self.curr_sele_user_name = tab_text

    def open_todo_list(self, list_name, list_id):
        if not self.curr_sele_user_name:
            return
        selected_list = self.db.get_specific_todo_list(
            self.curr_sele_user_name, list_name, list_id
        )
        # get display_frame of currently selected user tab
        user_data = self.user_tabs.get(self.curr_sele_user_name)
        if not user_data:
            return
        display_frame = user_data["frame"]

        # get the initial listbox and hide it
        listbox=user_data["listbox"]
        listbox.grid_remove()

        # remove remaining visible widgets of display_frame
        # for widget in display_frame.winfo_children():
        #     widget.destroy()

        # set background color of display_frame to white
        display_frame.configure(style="OpenList.TFrame")

        # create checkbuttons for each task
        # get tasks
        tasks = self.db.get_task_names_specific_todo_list(
            self.curr_sele_user_name, list_name, list_id
        )
        self.check_vars = {}  # create dictionary to track status of tasks

        row = 0
        for task in tasks:
            var = BooleanVar()
            self.check_vars[task] = var

            # Erstelle einen Checkbutton für jede Aufgabe
            checkbutton = ttk.Checkbutton(
                display_frame,
                text=task,
                variable=var,
                command=lambda t=task: self.toggle_task(t),
            )
            checkbutton.configure(style="ToDoCheck.TCheckbutton")
            checkbutton.grid(row=row, column=0, sticky="W", padx=5, pady=5)
            row += 1

    def strike(self, text):
        """Adds stike through to every character in the text."""
        return "".join(c + "\u0336" for c in text)

    def toggle_task(self, task):
        """Mark task as finished and strike it through."""
        var = self.check_vars.get(task)
        if var and var.get():
            print(f"Task '{task}' completed")
            # Aktualisiere den Text des Checkbuttons, um ihn durchzustreichen
            self.update_checkbutton_text(task, True)
        else:
            print(f"Task '{task}' not completed")
            self.update_checkbutton_text(task, False)

    def update_checkbutton_text(self, task, completed):
        """Update task text upon checking."""
        user_data = self.user_tabs.get(self.curr_sele_user_name)
        display_frame = user_data["frame"]

        for widget in display_frame.winfo_children():
            if (
                isinstance(widget, ttk.Checkbutton)
                and widget.cget("text").replace("\u0336", "") == task
            ):
                new_text = self.strike(task) if completed else task
                widget.config(text=new_text)

    def list_selection_window(self, action_command: str, currend_user: str):
        """Creates a pop-up window to let the user select a specific todo list.

        Args:
            action_command (str): determines further assginment of selected list
        """
        temp_selection_window = Toplevel(self.root)
        temp_selection_window.title("Select ToDo List")
        temp_selection_window.geometry("250x200")
        temp_selection_window.resizable(False, False)  # fixed window size

        explanation_label = Label(
            temp_selection_window,
            text=f"Please select the list\nyou like to {action_command}",
        )
        explanation_label.pack(pady=6)

        selection_listbox_frame = Frame(temp_selection_window)
        selection_listbox_frame.pack(padx=2, pady=3)

        selection_listbox = Listbox(
            selection_listbox_frame, selectmode="single", height=5
        )
        selection_listbox.pack(side=LEFT)

        selection_listbox_scrollbar = Scrollbar(
            selection_listbox_frame, command=selection_listbox.yview
        )
        selection_listbox_scrollbar.pack(side=RIGHT)

        user_todo_lists = self.db.get_available_todo_lists(currend_user)

        for list in user_todo_lists:
            selection_listbox.insert(END, list[1])

        def get_list_id_of_selected_list(selected_list_name):
            for list in user_todo_lists:
                if list[1] == selected_list_name:
                    return list[0]

        def perform_action():
            selected_list_index = selection_listbox.curselection()
            if selected_list_index:
                selected_list_name = selection_listbox.get(selected_list_index)
                selected_list_id = get_list_id_of_selected_list(
                    selected_list_name
                )
                if action_command == "open":
                    self.open_todo_list(selected_list_name, selected_list_id)
                elif action_command == "remove":
                    self.remove_todo_list()
                elif action_command == "modify":
                    self.modify_todo_list()
                temp_selection_window.destroy()

        # button must be defined after perform_action method, or it will throw
        # an Error (UnboundLocalError: local variable 'perform_action'
        # referenced before assignment)
        ok_button = Button(
            temp_selection_window, text="OK", command=perform_action
        )

        ok_button.pack(pady=6)

    def remove_todo_list(self):
        pass

    def modify_todo_list(self):
        pass

    def create_new_todo_list(self):
        list_name = simpledialog.askstring(
            title="Create new ToDo List",
            prompt="Please enter a Name for your new ToDo List:",
            parent=self.notebook,
        )

        if list_name:
            self.create_task_selection_window(list_name)

    def create_task_selection_window(self, list_name):
        """Replace listbox in display_frame with a dual-listbox."""
        if not self.curr_sele_user_name:
            return

        # get the display_frame of the currently selected user_tab
        user_data = self.user_tabs.get(self.curr_sele_user_name)
        if not user_data:
            return

        display_frame = user_data["frame"]

        display_frame.configure(style="ListboxFrame.TFrame")

        # get the initial listbox and hide it
        listbox=user_data["listbox"]
        listbox.grid_remove()
        
        # remove widgets in display_frame and restore the display_listbox
        for widget in display_frame.winfo_children():
            if isinstance(widget, ttk.Checkbutton):
                widget.destroy()        


        display_frame.columnconfigure(0, weight=1)
        display_frame.columnconfigure(1, weight=1)
        display_frame.columnconfigure(2, weight=1)

        # add the dual-listbox interface to the display_frame
        frame_left = Frame(display_frame)
        frame_left.grid(row=0, column=0, padx=2, pady=2, sticky=(N, S, W))

        frame_buttons = Frame(display_frame)
        frame_buttons.grid(row=0, column=1, padx=2, pady=2)

        frame_right = Frame(display_frame)
        frame_right.grid(row=0, column=2, padx=2, pady=2, sticky=(N, S, E))

        # left listbox with available tasks
        available_tasks = self.db.get_tasks(self.curr_sele_user_name)
        self.listbox_left = Listbox(
            frame_left, selectmode=MULTIPLE, width=30, height=15
        )
        self.listbox_left.grid(row=0, column=0)
        for task in available_tasks:
            self.listbox_left.insert(END, task)

        # right listbox for selected tasks
        self.listbox_right = Listbox(
            frame_right, selectmode=MULTIPLE, width=30, height=15
        )
        self.listbox_right.grid(row=0, column=0)

        # Buttons zum Verschieben der Aufgaben
        add_task_button = Button(
            frame_buttons, text="→", command=self.move_to_right
        )
        add_task_button.grid(row=0, column=0, pady=2)

        remove_task_button = Button(
            frame_buttons, text="←", command=self.move_to_left
        )
        remove_task_button.grid(row=1, column=0, pady=2)

        # Speichern-Button
        save_list_button = Button(
            display_frame,
            text="Save List",
            command=lambda: self.save_todo_list(list_name, display_frame),
        )
        save_list_button.grid(row=1, column=1, pady=2)

    def move_to_right(self):
        """Verschiebe ausgewählte Aufgaben zur rechten Listbox."""
        selected_tasks = self.listbox_left.curselection()
        for index in selected_tasks[::-1]:
            task = self.listbox_left.get(index)
            self.listbox_right.insert(END, task)
            self.listbox_left.delete(index)

    def move_to_left(self):
        """Verschiebe ausgewählte Aufgaben zur linken Listbox."""
        selected_tasks = self.listbox_right.curselection()
        for index in selected_tasks[::-1]:
            task = self.listbox_right.get(index)
            self.listbox_left.insert(END, task)
            self.listbox_right.delete(index)

    def save_todo_list(self, list_name, display_frame):
        """Speichere die neue ToDo-Liste und zeige die ursprüngliche Listbox wieder an."""
        tasks = [
            self.listbox_right.get(i) for i in range(self.listbox_right.size())
        ]
        if tasks:
            self.db.create_new_todo_list(list_name, tasks)
            messagebox.showinfo(
                "Success", f"ToDo list '{list_name}' created successfully!"
            )
        else:
            messagebox.showwarning(
                "No Tasks", "Please select at least one task."
            )

        # Nach dem Speichern die ursprüngliche Listbox wiederherstellen
        self.create_normal_user_tabs(self.curr_sele_user_name)

    def get_tasks_for_new_list(self):
        pass

    # define the show_all_tasks method to show all available tasks for the
    # current user
    def show_all_tasks(self):
        # get all tasks from the database
        if not self.curr_sele_user_name:
            return

        user_data = self.user_tabs.get(self.curr_sele_user_name)
        if not user_data:
            return

        display_frame = user_data['frame']
        display_frame.configure(style='ListboxFrame.TFrame')

        listbox = user_data['listbox']

        # remove widgets in display_frame and restore the display_listbox
        for widget in display_frame.winfo_children():
            if isinstance(widget, ttk.Checkbutton):
                widget.destroy()        

        listbox.grid()

        if listbox:
            all_tasks = self.db.get_tasks(self.curr_sele_user_name)
            listbox.delete(0, END)
            for task in all_tasks:
                listbox.insert(END, task)


if __name__ == "__main__":
    root = Tk()
    ToDoManagerGUI(root)
    root.mainloop()
