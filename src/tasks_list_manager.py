import json
import pathlib
from stringcolor import *
from tasks_creator import TasksCreator


class TasksListManager:
    """
    A class to manage a collection of tasks in a To-Do list.

    The TasksListManager class manages tasks in a To-Do list, allowing the user to add, remove, update, and retrieve tasks.
    It also provides functionality to load the list from a file and save it back to a file.

    Attributes:
    -----------
    list_file_name : str
        The name of the JSON file where the To-Do list is saved.
    todo_list : dict
        A dictionary containing all tasks in the To-Do list, where each task is stored by its task name.

    Methods:
    --------
    ensure_list_file_exists():
        Ensures that the To-Do list file exists, creating it if necessary.

    load_list_file():
        Loads the To-Do list from the specified file.

    save_list_file():
        Saves the current To-Do list to the specified file.

    add_task(new_task):
        Adds a new task to the To-Do list and saves the list.

    remove_task(task_name):
        Removes a task from the To-Do list and saves the list.

    get_task(task_name):
        Retrieves a task from the To-Do list and returns it as a TasksCreator object.

    update_task(updated_task):
        Updates the details of a task in the To-Do list and saves the changes.
    """

    def __init__(self, list_file_name: str) -> None:
        self.list_file_name = list_file_name
        self.todo_list = {}
        self.ensure_list_file_exists()  # JSON file is checked and created upon initialisation

    def ensure_list_file_exists(self) -> None:
        list_file_path = pathlib.Path(self.list_file_name)
        if not list_file_path.exists():
            print(
                cs(
                    f"File '{self.list_file_name}' does not exist. Creating a new To-Do list.",
                    "PaleVioletRed",
                )
            )
            with open(self.list_file_name, "w") as file:
                json.dump(
                    self.todo_list, file, indent=4
                )  # create an empty dictionary
        else:
            self.load_list_file()  # if the file exists, load it

    def load_list_file(self) -> None:
        list_file_path = pathlib.Path(self.list_file_name)
        if list_file_path.exists():
            try:
                with open(self.list_file_name, "r") as file:
                    self.todo_list = json.load(file)
                print(
                    cs(
                        f"Loaded To-Do list from '{self.list_file_name}'.",
                        "LightSeaGreen",
                    )
                )
            except json.JSONDecodeError as e:
                print(
                    cs(
                        f"Error loading the To-Do list file: {e}",
                        "MediumVioletRed",
                    )
                )
                self.todo_list = (
                    {}
                )  # set to an empty dict., if something went wrong

    def save_list_file(self) -> None:
        with open(self.list_file_name, "w") as file:
            json.dump(self.todo_list, file, indent=4)
        print(
            cs(
                f"Your To-Do list has been saved as '{self.list_file_name}'",
                "LightSeaGreen",
            )
        )

    def add_task(self, new_task: TasksCreator) -> str:
        if new_task.task_name not in self.todo_list:
            self.todo_list[new_task.task_name] = {
                "Priority": new_task.priority,
                "Due Date": new_task.due_date,
                "Status": "open",
            }
            self.save_list_file()  # save the modifications
            print(
                cs(
                    f"The task '{new_task.task_name}' has been added to your To-Do list.",
                    "LightSeaGreen",
                )
            )
        else:
            print(
                cs(
                    f"The task '{new_task.task_name}' is already on your To-Do list.",
                    "PaleVioletRed",
                )
            )

    def remove_task(self, task_name: str) -> str:
        if task_name in self.todo_list:
            del self.todo_list[task_name]
            self.save_list_file() 
            print(
                cs(
                    f"The task '{task_name}' has been removed from your To-Do list.",
                    "LightSeaGreen",
                )
            )
        else:
            print(
                cs(
                    f"The task '{task_name}' can't be found on your To-Do list.",
                    "MediumVioletRed",
                )
            )

    def get_task(self, task_name: str) -> TasksCreator:
        if task_name in self.todo_list:
            task_info = self.todo_list[task_name]

            task = TasksCreator(
                task_name, task_info["Priority"], task_info["Due Date"]
            )
            task.status = task_info["Status"]
            return task
        else:
            raise ValueError(
                cs(
                    f"Task '{task_name}' not found in the To-Do list.",
                    "MediumVioletRed",
                )
            )

    def __str__(self) -> str:
        colored_output = cs(f"To-Do list: {self.todo_list}", "DarkSlateGray3")
        return str(colored_output)


if __name__ == "__main__":

    some_task = TasksCreator("new_one", "Low", "tomorrow")
    print(some_task)

    my_todo_list = TasksListManager("some_todo_list.json")
    print(my_todo_list)

    my_todo_list.add_task(some_task)

    my_task = my_todo_list.get_task("new_one")
    print(my_task)
