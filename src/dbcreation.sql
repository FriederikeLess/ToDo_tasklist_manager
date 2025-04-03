-- This script contains all the terminal input used to create the database
-- initial databse creation
CREATE DATABASE todo_list_manager_db;

-- connect to db
\c todo_list_manager_db 
-- create Table for all users
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(30) UNIQUE NOT NULL
);

-- create Table for tasks that can be added to a todo-list
CREATE TABLE todo_tasks (
    task_id SERIAL PRIMARY KEY,
    task_name VARCHAR(50) UNIQUE NOT NULL,
    is_general BOOLEAN DEFAULT true,
    user_id INT REFERENCES users (user_id)
);

-- create Table for todo_lists
CREATE TABLE todo_lists (
    todo_id SERIAL PRIMARY KEY,
    list_name VARCHAR(50) NOT NULL,
    list_id INT UNIQUE NOT NULL,
    is_finished BOOLEAN DEFAULT false,
    task_id INT REFERENCES todo_tasks (task_id),
    user_id INT REFERENCES users (user_id)
);

-- add a general user to the users table to be able to to add default general
-- tasks to the todo_tasks table
INSERT INTO users (name) VALUES ('general_user');
-- add default general, recurring tasks to the todo_taks table
INSERT INTO
    todo_tasks (task_name, user_id)
VALUES ('do laundry', 1),
    ('hang laundry', 1),
    (
        'fold up laundry and put away',
        1
    ),
    ('do dishes', 1),
    ('change bed sheets', 1),
    ('vacuum-clean', 1),
    ('clean kitchen', 1),
    ('clean bathroom', 1),
    ('clean windows', 1),
    ('mop the floor', 1),
    ('take out trash', 1),
    ('grocery shopping', 1),
    ('call grandma', 1),
    ('call mother', 1),
    ('vaccum dog bed', 1),
    ('wash dog bed', 1),
    ('dusting', 1);

-- add ON DELETE CASCADE constraint for user_id in todo_tasks and todo_lists
-- tables
\d todo_tasks
ALTER TABLE todo_tasks DROP CONSTRAINT todo_tasks_user_id_fkey;

ALTER TABLE todo_tasks
ADD CONSTRAINT "todo_tasks_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE;

-- create VIEW for distinct todo lists per user
CREATE OR REPLACE VIEW view_todo_lists_per_user AS
SELECT DISTINCT
    list_id,
    list_name
FROM todo_lists
WHERE
    user_id IN (1, 3)
ORDER by list_id;

-- remove constraints that defined list_id to be unique
ALTER Table todo_lists DROP CONSTRAINT todo_lists_list_id_key;

-- add test-data to todo_lists table
INSERT INTO
    todo_lists (
        list_name,
        list_id,
        task_id,
        user_id
    )
VALUES ('list_1', 1, 18, 3),
    ('list_1', 1, 19, 3),
    ('list_1', 1, 20, 3),
    ('list_1', 1, 25, 3),
    ('list_2', 2, 18, 3),
    ('list_2', 2, 19, 3),
    ('list_2', 2, 20, 3),
    ('list_2', 2, 25, 3),
    ('list_2', 2, 21, 3),
    ('list_2', 2, 22, 3);

-- create a VIEW with a JOIN to get task_id, task_name and is_finished
-- in one table
CREATE OR REPLACE VIEW current_todo_list_view AS
SELECT 
    todo_lists.list_name, 
    todo_lists.task_id, 
    todo_tasks.task_name, 
    todo_lists.is_finished
FROM todo_lists
    JOIN todo_tasks 
        ON todo_lists.task_id = todo_tasks.task_id
WHERE
    todo_lists.user_id IN (1, 3)
    AND todo_lists.list_name = 'list_1';

-- get the currently highest list_id of todo lists of a specific user
SELECT MAX(list_id) FROM todo_lists WHERE user_id=3;

-- remove values from todo_lists table
DELETE FROM ONLY todo_lists WHERE user_id=3 AND list_name='list_4';

-- change Foreign-key constraint for user_id in todo_lists table
ALTER TABLE todo_lists
DROP CONSTRAINT todo_lists_user_id_fkey;

ALTER TABLE todo_lists
ADD CONSTRAINT todo_lists_user_id_fkey
FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE;
