"""This module creates the initial database for the ToDo task list manager project."""

# load packages
import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import find_dotenv, load_dotenv

# load the environment variables from the .env file
# the default datatype of the loaded content is str
load_dotenv(find_dotenv())


class Database:
    def __init__(self) -> None:
        try:
            self.connection = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USERNAME"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=int(os.getenv("DB_PORT")),
            )
            self.cursor = self.connection.cursor()
        except psycopg2.Error as e:
            print(f"An error occured while connecting to the database: {e}")
            self.connection = None
        except Exception as exc:
            print(f"An unexpected error occured: {exc}")
            self.connection = None

    def get_existing_users(self):
        if self.connection:
            try:
                input_query = "SELECT name FROM users"
                self.cursor.execute(input_query)
                user_names = self.cursor.fetchall()
                return [user_name[0] for user_name in user_names]
            except psycopg2.Error as e:
                print(f"Error fetching all user names_ {e}")
        else:
            print("No activae database connection.")

    def get_current_user_id(self, user_name):
        if self.connection:
            try:
                input_query = "SELECT user_id FROM users WHERE name=%s"
                self.cursor.execute(input_query, (user_name,))
                result = self.cursor.fetchone()
                if result:
                    return result[0]
            except psycopg2.Error as e:
                print(f"Error fetching id of user '{user_name}': {e}")
        else:
            print("No activae database connection.")

    def create_new_user(self, name: str) -> None:
        if self.connection:
            try:
                input_query = "INSERT INTO users (name) VALUES (%s);"  # parameterized query as protection against SQL-injections
                self.cursor.execute(
                    input_query, (name,)
                )  # value has to be a tuple, therefore '(name,)' and not '(name)'
                self.connection.commit()
            except psycopg2.Error as e:
                print(f"Error creating new user: {e}")
                self.connection.rollback()
        else:
            print("No activae database connection.")

    def delete_user(self, name: str) -> None:
        if self.connection:
            try:
                input_query = "DELETE FROM users WHERE name=%s;"
                self.cursor.execute(input_query, (name,))
                self.connection.commit()
            except psycopg2.Error as e:
                print(f"Error deleting user '{name}': {e}")
                self.connection.rollback()
        else:
            print("No active database connection.")

    def create_new_todo_list(
        self, list_name: str, task_names: list, user_name: str
    ):
        if self.connection:
            try:
                new_list_id = self.manage_list_ids(user_name)[1]
                current_user_id = self.get_current_user_id(user_name)

                values = [
                    (
                        list_name,
                        new_list_id,
                        self.get_task_id_from_task_name(task),
                        current_user_id,
                    )
                    for task in task_names
                ]
                input_query = """
                    INSERT INTO todo_lists (list_name, list_id, task_id, user_id)
                    VALUES %s;
                """
                execute_values(self.cursor, input_query, values)
                self.connection.commit()
            except psycopg2.Error as e:
                print(f"Error creating new ToDo list: {e}")
                self.connection.rollback()
        else:
            print("No active database connection.")

    def remove_todo_list(self, list_name, user_name):
        if self.connection:
            try:
                current_user_id = self.get_current_user_id(user_name)
                input_query = """
                    DELETE FROM ONLY todo_lists 
                    WHERE user_id=%s 
                        AND list_name=%s;
                """
                self.cursor.execute(input_query, (current_user_id, list_name))
                self.connection.commit()
            except psycopg2.Error as e:
                print(f"Error deleting ToDo list '{list_name}': {e}")
                self.connection.rollback()
        else:
            print("No active database connection.")

    def manage_list_ids(self, user_name: str):
        if self.connection:
            try:
                current_user_id = self.get_current_user_id(user_name)
                input_query = """
                    SELECT MAX(list_id) 
                    FROM todo_lists 
                    WHERE user_id=%s;
                """
                self.cursor.execute(input_query, (current_user_id,))
                currently_highest_list_id = self.cursor.fetchone()[0]
                if currently_highest_list_id:
                    return currently_highest_list_id, (
                        currently_highest_list_id + 1
                    )
                else:
                    return (0, 1)
            except psycopg2.Error as e:
                print(
                    f"Error fetching the currently highest ToDo list ID for '{user_name}': {e}"
                )
        else:
            print("No active database connection.")

    def get_available_todo_lists(self, user_name, user_ids=[1]):
        if self.connection:
            try:
                current_user_id = self.get_current_user_id(user_name)
                user_ids.append(current_user_id)
                user_ids = tuple(user_ids)
                input_query = """
                    SELECT DISTINCT list_id, list_name
                    FROM todo_lists
                    WHERE user_id IN %s
                    ORDER by list_id;
                """
                self.cursor.execute(input_query, (user_ids,))
                list_items_tuple = self.cursor.fetchall()
                return [list_item for list_item in list_items_tuple]
            except psycopg2.Error as e:
                print(
                    f"Error fetching available ToDo lists for '{user_name}': {e}"
                )
        else:
            print("No active database connection.")

    def get_specific_todo_list(self, user_name, list_name, user_ids=[1]):
        if self.connection:
            try:
                current_user_id = self.get_current_user_id(user_name)
                user_ids.append(current_user_id)
                user_ids = tuple(user_ids)
                input_query = """
                    SELECT 
                        todo_lists.list_name, 
                        todo_lists.task_id, 
                        todo_tasks.task_name, 
                        todo_lists.is_finished
                    FROM todo_lists
                        JOIN todo_tasks 
                            ON todo_lists.task_id = todo_tasks.task_id
                    WHERE
                        todo_lists.user_id IN %s
                        AND todo_lists.list_name = %s;
                """
                self.cursor.execute(input_query, (user_ids, list_name))
                list_tasks = self.cursor.fetchall()
                return list_tasks
            except psycopg2.Error as e:
                print(f"Error fetching ToDo list '{list_name}': {e}")
        else:
            print("No active database connection.")

    def update_task_status(self, is_finished, user_name, task_name, list_name):
        if self.connection:
            try:
                current_user_id = self.get_current_user_id(user_name)
                task_id = self.get_task_id_from_task_name(task_name)
                input_query = """
                        UPDATE todo_lists
                        SET is_finished = %s
                        WHERE 
                            user_id=%s 
                            AND task_id=%s 
                            AND list_name=%s;
                    """
                self.cursor.execute(
                    input_query,
                    (is_finished, current_user_id, task_id, list_name),
                )
                self.connection.commit()
            except psycopg2.Error as e:
                print(f"Error updating task status: {e}")
                self.connection.rollback()
        else:
            print("No active database connection.")

    def get_task_id_from_task_name(self, task_name):
        if self.connection:
            try:
                input_query = """
                        SELECT task_id FROM todo_tasks
                        WHERE task_name=%s;
                    """
                self.cursor.execute(input_query, (task_name,))
                task_id_tuple = self.cursor.fetchall()
                return task_id_tuple[0]
            except psycopg2.Error as e:
                print(f"Error fetching Task ID of '{task_name}': {e}")
        else:
            print("No active database connection.")

    def get_task_names_specific_todo_list(self, user_name, list_name, list_id):
        if self.connection:
            try:
                task_ids = [
                    task[0]
                    for task in self.get_specific_todo_list(
                        user_name, list_name, list_id
                    )
                ]
                task_ids = tuple(task_ids)
                input_query = """
                    SELECT task_name FROM todo_tasks
                    WHERE task_id IN %s
                """
                self.cursor.execute(input_query, (task_ids,))
                task_names_tuple = self.cursor.fetchall()
                task_names_list = [
                    task_name[0] for task_name in task_names_tuple
                ]
                return task_names_list
            except psycopg2.Error as e:
                print(f"Error fetching Tasks of list '{list_name}': {e}")
        else:
            print("No active database connection.")

    def add_task(self, task_name, user_id):
        if self.connection:
            try:
                input_query = """
                    INSERT INTO todo_lists (task_name, user_id) 
                    VALUES (%s);
                """
                self.cursor.execute(input_query, (task_name, user_id))
                self.connection.commit()
            except psycopg2.Error as e:
                print(f"Error adding a new todo task: {e}")
                self.connection.rollback()
        else:
            print("No active database connection.")

    def get_tasks(self, current_user_name, user_ids=[1]):
        if self.connection:
            try:
                current_user_id = self.get_current_user_id(current_user_name)
                user_ids.append(current_user_id)
                user_ids = tuple(user_ids)
                input_query = """
                    SELECT task_name 
                    FROM todo_tasks
                    WHERE user_id IN %s;
                """
                self.cursor.execute(input_query, (tuple(user_ids),))
                tasks = self.cursor.fetchall()
                tasks_list = [task[0] for task in tasks]
                tasks_list.sort()
                return tasks_list
            except psycopg2.Error as e:
                print(f"Error receiving todo tasks: {e}")
        else:
            print("No active database connection.")

    def delete_task_from_todo_list(self, list_name, task_id, user_id):
        if self.connection:
            try:
                input_query = """
                    DELETE FROM todo_lists 
                    WHERE list_name=%s 
                        AND task_id=%s
                        AND user_id=%s;
                """
                self.cursor.execute(input_query, (list_name, task_id, user_id))
                self.connection.commit()
            except psycopg2.Error as e:
                print(f"Error deleting a task from '{list_name}': {e}")
                self.connection.rollback()
        else:
            print("No active database connection.")

    def close(self):
        self.cursor.close()
        self.connection.close()


if __name__ == "__main__":
    todo_db = Database()
    todo_db.remove_todo_list("list_3", "Friedi")
    # task_id=todo_db.get_task_id_from_task_name("do laundry")
    # print(task_id)
    # todo_db.create_new_todo_list(
    #     "list_3", ["do laundry", "hang laundry", "do dishes"], "Friedi"
    # )
    # list_id = todo_db.manage_list_ids("Friedi")
    # print(list_id)
    # todo_lists = todo_db.get_available_todo_lists("Friedi")
    # print(todo_lists)
    # spec_todo_list = todo_db.get_specific_todo_list("Friedi", "list_1", 1)
    # print(spec_todo_list)
    # task_names = todo_db.get_task_names_specific_todo_list(
    #     "Friedi", "list_1", 1
    # )
    # print(task_names)
    # user_id = todo_db.get_current_user_id("Friedi")
    # print(user_id)
    # tasks = todo_db.get_tasks("Friedi")
    # print(tasks)
    # all_tasks = todo_db.get_tasks()
    # print(all_tasks)
