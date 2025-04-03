from stringcolor import *


class TasksCreator:
    """
    A class to represent a task in a To-Do list.

    The TasksCreator class defines a task with its name, priority, due date, and status.
    It provides methods to modify the task's priority and status.

    Attributes:
    -----------
    task_name : str
        The name of the task.
    priority : str
        The priority of the task (e.g., "High", "Medium", "Low").
    due_date : str
        The due date for the task.
    status : str
        The current status of the task (default is "open").

    Methods:
    --------
    mark_as_done(task_name):
        Marks the task as done if the task name matches.

    change_priority(task_name, new_prio):
        Changes the priority of the task if the task name matches and the new priority is valid.

    __str__():
        Returns a string representation of the task, including its name, priority, due date, and status.
    """

    def __init__(self, task_name, priority, due_date) -> None:
        self.task_name = task_name
        self.priority = priority
        self.due_date = due_date
        self.status = "open"

    def mark_as_done(self, task_name):
        if self.task_name == task_name:
            if self.status == "open":
                self.status = "done"
                return cs(
                    f"The task '{task_name}' has been marked as 'done'",
                    "LightSeaGreen",
                )
            else:
                return "You have already finsihed this task."
        else:
            return "Task not found."

    def change_priority(self, task_name, new_prio):
        priority_options = ["High", "Medium", "Low"]
        if (
            self.task_name == task_name
            and new_prio.title() in priority_options
        ):
            if new_prio != self.priority:
                self.priority = new_prio
                colored_output = cs(
                    f"The priority for the task '{task_name}' has been changed to {new_prio.title()}.",
                    "LightSeaGreen",
                )
                return str(colored_output)
            else:
                return f"The priority for the task '{task_name}' is already set to '{new_prio.title()}'."
        else:
            return f"{new_prio.title()} is not a valid priority option."

    def __str__(self) -> str:
        colored_output = cs(
            f"Task: '{self.task_name}'\nPriority: {self.priority}\nDue: {self.due_date}\nStatus: {self.status}.",
            "DarkSlateGray3",
        )

        return str(colored_output)
