from dbmanager import Database
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog


class ToDoManagerGUI:
    def __init__(self, root: Tk) -> None:
        # root (main) application window is created outside of the class
        # and commited as an attribute
        self.root = root
        self.root.title("ToDo List Manager")
        # define the size of the root window
        self.root.geometry("800x500")
        # configure behaviour root frame columns and rows
        # must be defined, or notebook widget inside root wouldn't change when
        # scale of window changes
        self.root.columnconfigure(0, weight=1)
        # self.root.rowconfigure(0, weight=1)  # row of "Add User" and
        # "Delete User" Button
        self.root.rowconfigure(1, weight=1)  # row of user tabs

        # connect to database
        self.db = Database()

        # get all existing users in the users tables of the db
        self.existing_users = self.db.get_existing_users()

        # define styles for different displays
        self.style = ttk.Style()
        # styles for the display_frame
        self.style.configure("OpenList.TFrame", background="white")
        self.style.configure("ListboxFrame.TFrame", background="#d9d9d9")
        # styles for the todo task checkbuttons
        self.style.configure("ToDoCheck.TCheckbutton", background="white")

        # create Frame for "Add User" and "Delete User" buttons
        self.add_delete_user_buttons_frame = ttk.Frame(self.root)
        self.add_delete_user_buttons_frame.grid(row=0, column=0, sticky=(N, E))

        # create buttons for "Add User" and "Delete User" outside the Tabs
        self.add_user_button = Button(
            self.add_delete_user_buttons_frame,
            text="Add User",
            width=10,
            command=self.add_user,
        )
        self.add_user_button.grid(row=0, column=0, pady=(20, 0), padx=(2, 1))

        self.delete_user_button = Button(
            self.add_delete_user_buttons_frame,
            text="Delete User",
            width=10,
            command=self.delete_user,
        )
        self.delete_user_button.grid(
            row=0, column=1, pady=(20, 0), padx=(1, 2)
        )

        # create a Notebook object to create tabs for each user in it
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(
            row=1, column=0, sticky=(N, E, S, W), padx=5, pady=(5, 0)
        )
        self.notebook.bind("<<NotebookTabChanged>>", self.get_curr_user_name)

        # create a dictionary to store the distplay_listbox of every user
        # to make every tab independent of the others
        self.user_tabs = {}

        # define a variable for the text of the currently selected tab, which
        # is the user_name. The default is the general_user
        self.curr_sele_user_name = "general_user"

        # create tab for general_user, if no other users exist
        if not "general_user" in self.existing_users:
            print("Error! general_user is missing. Please check the database")
        elif len(self.existing_users) == 1:
            self.create_general_user_tab()
            self.root.update_idletasks()
        else:
            for user_name in self.existing_users[1:]:
                self.create_normal_user_tabs(user_name)

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

    # define a  method to get the text of the currently selected tab, which is
    # the current user_name
    def get_curr_user_name(self, event):
        curr_sele_tab = event.widget.select()
        if curr_sele_tab:
            tab_text = event.widget.tab(curr_sele_tab, "text")
            self.curr_sele_user_name = tab_text

    # define method to create the normal user tabs
    def create_normal_user_tabs(self, user_name):
        user_tab = ttk.Frame(self.notebook)
        self.notebook.add(user_tab, text=user_name)

        # Configure the user_tab to expand properly
        user_tab.columnconfigure(1, weight=1)
        user_tab.rowconfigure(0, weight=1)

        # Create a frame to hold all buttons for managing todo lists and tasks
        button_frame = ttk.Frame(user_tab, padding=10, width=150)
        button_frame.grid(column=0, row=0, sticky=(N, E, S, W))
        button_frame.columnconfigure(0, weight=1)
        for i in range(6):
            button_frame.rowconfigure(i, weight=1)

        # Create display frames for different functionalities
        open_list_frame = ttk.Frame(user_tab, padding=10)
        create_list_frame = ttk.Frame(user_tab, padding=10)
        modify_list_frame = ttk.Frame(user_tab, padding=10)
        show_tasks_frame = ttk.Frame(user_tab, padding=10)

        # Add frames to the user_data dictionary
        self.user_tabs[user_name] = {
            "open_list_frame": open_list_frame,
            "create_list_frame": create_list_frame,
            "modify_list_frame": modify_list_frame,
            "show_tasks_frame": show_tasks_frame,
        }

        # Configure all frames initially to be hidden
        for frame in self.user_tabs[user_name].values():
            frame.grid(column=1, row=0, sticky=(N, S, E, W))
            frame.grid_remove()

        # Create dual-listbox in the "create_list_frame"
        self.create_task_selection_window(
            self.user_tabs[user_name]["create_list_frame"]
        )

        # Create Listbox in the "show_tasks_frame"
        self.create_tasks_listbox(
            self.user_tabs[user_name]["show_tasks_frame"]
        )

        # Add buttons to the button_frame
        self.add_buttons(button_frame, user_name)

    def add_buttons(self, button_frame, user_name):
        Button(
            button_frame,
            text="Open ToDo List",
            width=22,
            command=lambda: self.list_selection_window(
                "open", self.curr_sele_user_name
            ),
        ).grid(pady=(40, 5), padx=5)

        Button(
            button_frame,
            text="Create new ToDo List",
            width=22,
            command=lambda: self.show_frame(user_name, "create_list_frame"),
        ).grid(pady=5, padx=5)

        ########## muss nochmal angepasst werden, weil command einfach bloß
        # das löschen einer todo list wäre. Da muss kein Frame angezeigt werden
        Button(
            button_frame,
            text="Remove ToDo List",
            width=22,
            command=lambda: self.list_selection_window(
                "remove", self.curr_sele_user_name
            ),
        ).grid(pady=5, padx=5)

        Button(
            button_frame,
            text="Modify ToDo List",
            width=22,
            command=lambda: self.show_frame(user_name, "modify_list_frame"),
        ).grid(pady=5, padx=5)

        Button(
            button_frame,
            text="Show all ToDo Tasks",
            width=22,
            command=lambda: self.show_frame(user_name, "show_tasks_frame"),
        ).grid(pady=(5, 20), padx=5)

    def create_tasks_listbox(self, frame):
        """Create a Listbox with a scrollbar."""
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        listbox = Listbox(frame)
        listbox.grid(row=0, column=0, sticky=(N, E, S, W))
        scrollbar = Scrollbar(frame, orient=VERTICAL, command=listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(N, S))
        listbox.configure(yscrollcommand=scrollbar.set)
        if listbox:
            all_tasks = self.db.get_tasks(self.curr_sele_user_name)
            listbox.delete(0, END)
            for task in all_tasks:
                listbox.insert(END, task)
        return listbox

    def create_task_selection_window(self, frame):
        """Create a Dual-Listbox with Buttons to move entries back and forth."""
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)
        frame.rowconfigure(0, weight=1)

        frame_left = Frame(frame)
        frame_left.grid(row=0, column=0, padx=2, pady=2, sticky=(N, S, W))
        frame_left.rowconfigure(0, weight=1)

        buttons_frame = Frame(frame)
        buttons_frame.grid(row=0, column=1, padx=2, pady=2)

        frame_right = Frame(frame)
        frame_right.grid(row=0, column=2, padx=2, pady=2, sticky=(N, S, E))
        frame_right.rowconfigure(0, weight=1)

        # left listbox with available tasks
        available_tasks = self.db.get_tasks(self.curr_sele_user_name)
        listbox_left = Listbox(frame_left, selectmode=MULTIPLE, width=30)
        listbox_left.grid(row=0, column=0, sticky=(N, S, E, W))
        for task in available_tasks:
            listbox_left.insert(END, task)

        # right listbox for selected tasks
        listbox_right = Listbox(frame_right, selectmode=MULTIPLE, width=30)
        listbox_right.grid(row=0, column=0, sticky=(N, S, E, W))

        def move_to_right():
            """Verschiebe ausgewählte Aufgaben zur rechten Listbox."""
            selected_tasks = listbox_left.curselection()
            for index in selected_tasks[::-1]:
                task = listbox_left.get(index)
                listbox_right.insert(END, task)
                listbox_left.delete(index)

        def move_to_left():
            """Verschiebe ausgewählte Aufgaben zur linken Listbox."""
            selected_tasks = listbox_right.curselection()
            for index in selected_tasks[::-1]:
                task = listbox_right.get(index)
                listbox_left.insert(END, task)
                listbox_right.delete(index)

        def save_todo_list():
            """Save the new todo list."""
            list_name = simpledialog.askstring(
                title="Create new ToDo List",
                prompt="Please enter a Name for your new ToDo List:",
                parent=self.notebook,
            )
            tasks = [listbox_right.get(i) for i in range(listbox_right.size())]
            if tasks:
                self.db.create_new_todo_list(
                    list_name, tasks, self.curr_sele_user_name
                )
                messagebox.showinfo(
                    "Success", f"ToDo list '{list_name}' created successfully!"
                )
            else:
                messagebox.showwarning(
                    "No Tasks", "Please select at least one task."
                )

        # Speichern-Button
        save_list_button = Button(
            frame,
            text="Save List",
            command=save_todo_list,
        )
        save_list_button.grid(row=1, column=1, pady=2)

        # Buttons zum Verschieben der Aufgaben
        add_task_button = Button(
            buttons_frame, text="→", command=move_to_right
        )
        add_task_button.grid(row=0, column=0, pady=2)

        remove_task_button = Button(
            buttons_frame, text="←", command=move_to_left
        )
        remove_task_button.grid(row=1, column=0, pady=2)

    def list_selection_window(self, action_command: str, current_user: str):
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

        user_todo_lists = self.db.get_available_todo_lists(current_user)

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
                    self.open_todo_list(selected_list_name)
                elif action_command == "remove":
                    print(selected_list_name)
                    self.remove_todo_list(selected_list_name)
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

    def open_todo_list(self, list_name):
        if not self.curr_sele_user_name:
            return

        user_data = self.user_tabs.get(self.curr_sele_user_name)
        if not user_data:
            return

        # Hide all frames
        for frame in user_data.values():
            frame.grid_remove()

        frame = user_data["open_list_frame"]
        frame.grid()
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        checkbutton_frame = Frame(frame, background="white")
        checkbutton_frame.grid(
            row=0, column=0, sticky=(N, S, E, W), padx=5, pady=5
        )

        # Store the checkbutton_frame in user_data for later access
        user_data["checkbutton_frame"] = checkbutton_frame

        # create checkbuttons for each task
        # get tasks
        tasks_list = self.db.get_specific_todo_list(
            self.curr_sele_user_name, list_name
        )
        self.check_vars = {}  # create dictionary to track status of tasks

        row = 0
        for task in tasks_list:
            task_name = task[2]
            is_finished = task[3]
            var = BooleanVar(value=is_finished)
            self.check_vars[task_name] = var

            # Create a Checkbutton for each task
            checkbutton = ttk.Checkbutton(
                checkbutton_frame,
                text=(
                    self.strike(task_name)
                    if is_finished == True
                    else task_name
                ),
                variable=var,
                command=lambda t=task_name, v=var: self.toggle_task(
                    t, v, list_name
                ),
            )
            checkbutton.configure(style="ToDoCheck.TCheckbutton")
            checkbutton.grid(row=row, column=0, sticky="W", padx=5, pady=5)
            row += 1

    def strike(self, text):
        """Adds stike through to every character in the text."""
        return "".join(c + "\u0336" for c in text)

    def toggle_task(self, task, var, list_name):
        """Toggle the task status and update the database."""
        # to toggle = hin- und herschalten
        is_finished = var.get()  # Get the current status from the BooleanVar
        if is_finished == True:
            # update text of checkbutton to strik it through
            self.update_checkbutton_text(task, is_finished)

            # Update the task status in the database
            self.db.update_task_status(
                is_finished, self.curr_sele_user_name, task, list_name
            )
        else:
            self.update_checkbutton_text(task, is_finished)
            self.db.update_task_status(
                is_finished, self.curr_sele_user_name, task, list_name
            )

    def update_checkbutton_text(self, task, completed):
        """Update task text upon checking."""
        user_data = self.user_tabs.get(self.curr_sele_user_name)
        checkbutton_frame = user_data.get("checkbutton_frame")

        for widget in checkbutton_frame.winfo_children():
            if (
                isinstance(widget, ttk.Checkbutton)
                and widget.cget("text").replace("\u0336", "") == task
            ):
                new_text = self.strike(task) if completed == True else task
                widget.config(text=new_text)

    def remove_todo_list(self, list_name):
        self.db.remove_todo_list(list_name, self.curr_sele_user_name)

    def show_frame(self, user_name, frame_name, list_name=None):
        """Show a specific frame and hide all others for the given user."""
        user_data = self.user_tabs.get(user_name)
        if not user_data:
            return

        # Hide all frames
        for frame in user_data.values():
            frame.grid_remove()

        # Show the selected frame
        # if list_name:
        #     pass
        # else:
        user_data[frame_name].grid()


if __name__ == "__main__":
    root = Tk()
    ToDoManagerGUI(root)
    root.mainloop()
