import os
from datetime import datetime, date

DATETIME_STRING_FORMAT = "%Y-%m-%d"

# Define admin usernames
ADMIN_USERNAMES = {"admin", "superuser"}

# Create tasks.txt if it doesn't exist
if not os.path.exists("tasks.txt"):
    with open("tasks.txt", "w"):
        pass

# Create user.txt if it doesn't exist
if not os.path.exists("user.txt"):
    with open("user.txt", "w") as default_file:
        default_file.write("admin;password")

# Load tasks from tasks.txt
with open("tasks.txt", 'r') as task_file:
    task_data = task_file.read().split("\n")
    task_data = [t for t in task_data if t != ""]

task_list = []
for t_str in task_data:
    curr_t = {}
    task_components = t_str.split(";")
    curr_t['username'] = task_components[0]
    curr_t['title'] = task_components[1]
    curr_t['description'] = task_components[2]
    curr_t['due_date'] = datetime.strptime(task_components[3], DATETIME_STRING_FORMAT)
    curr_t['assigned_date'] = datetime.strptime(task_components[4], DATETIME_STRING_FORMAT)
    curr_t['completed'] = True if task_components[5] == "Yes" else False
    task_list.append(curr_t)
# Load users from user.txt
with open("user.txt", 'r') as user_file:
    user_data = user_file.read().split("\n")

username_password = {}
for user in user_data:
    username, password = user.split(';')
    username_password[username] = password

while True:
    print("LOGIN")
    curr_user = input("Username: ")
    curr_pass = input("Password: ")
    if curr_user not in username_password.keys():
        print("User does not exist")
        continue
    elif username_password[curr_user] != curr_pass:
        print("Wrong password")
        continue
    else:
        print("Login Successful!")
        break  # Exit the loop when login is successful



def reg_user():
    """
    Register a new user by entering a new username and password.
    """
    new_username = input("New Username: ")
    if new_username in username_password:
        print("Username already exists, please try a different username.")
        return
    new_password = input("New Password: ")
    confirm_password = input("Confirm Password: ")
    if new_password == confirm_password:
        print("New user added")
        username_password[new_username] = new_password
        with open("user.txt", "a") as out_file:
            out_file.write(f"\n{new_username};{new_password}")
    else:
        print("Passwords do not match")
        return


def add_task():
    """
    Add a new task by entering the assigned username, task title, description, and due date.
    """
    task_username = input("Name of person assigned to task: ")
    if task_username not in username_password.keys():
        print("User does not exist. Please enter a valid username")
        return
    task_title = input("Title of Task: ")
    task_description = input("Description of Task: ")
    while True:
        try:
            task_due_date = input("Due date of task (YYYY-MM-DD): ")
            due_date_time = datetime.strptime(task_due_date, DATETIME_STRING_FORMAT)
            break
        except ValueError:
            print("Invalid datetime format. Please use the format specified")
    curr_date = date.today()
    new_task = {
        "username": task_username,
        "title": task_title,
        "description": task_description,
        "due_date": due_date_time,
        "assigned_date": curr_date,
        "completed": False
    }
    task_list.append(new_task)
    with open("tasks.txt", "a") as task_file:
        task_file.write(
            f"\n{task_username};{task_title};{task_description};{due_date_time.strftime(DATETIME_STRING_FORMAT)};{curr_date.strftime(DATETIME_STRING_FORMAT)};No"
        )
    print("Task added successfully!")
    generate_reports()


def list_tasks(username=None):
    """
    List all tasks or tasks assigned to a specific username.
    """
    filtered_tasks = task_list if username is None else [task for task in task_list if task['username'] == username]
    if not filtered_tasks:
        print("No tasks found.")
    else:
        for idx, task in enumerate(filtered_tasks):
            print(
                f"{idx}: {task['title']} - {task['description']} - Due: {task['due_date'].strftime(DATETIME_STRING_FORMAT)} - Completed: {'Yes' if task['completed'] else 'No'}"
            )
    return filtered_tasks


def mark_complete(task_title):
    """
    Mark a task as complete based on the provided task title.
    """
    found = False
    for task in task_list:
        if task["title"] == task_title:
            task["completed"] = True
            found = True
            break
    if not found:
        print("No task found with that title")
        return
    with open("tasks.txt", "w") as task_file:
        task_data = []
        for task in task_list:
            task_data.append(
                f"{task['username']};{task['title']};{task['description']};{task['due_date'].strftime(DATETIME_STRING_FORMAT)};{task['assigned_date'].strftime(DATETIME_STRING_FORMAT)};{'Yes' if task['completed'] else 'No'}"
            )
        task_file.write("\n".join(task_data))
    print("Task marked as complete")


def edit_task(task_title):
    """
    Edit the description, due date, and assigned username of a task based on the task title.
    """
    found = False
    for task in task_list:
        if task["title"] == task_title:
            print(f"Editing Task: {task['title']}")
            task_description = input("Enter new description for the task: ")
            task_due_date = input("Enter the new due date (YYYY-MM-DD): ")
            new_due_date = validate_date(task_due_date)
            if new_due_date is None:
                print("Invalid date format. Please use the format specified.")
                return

            task_username = input("Enter the new username for the task: ")
            if task_username not in username_password.keys():
                print("User does not exist. Please enter a valid username")
                return

            task['description'] = task_description
            task['due_date'] = new_due_date
            task['username'] = task_username

            found = True
            break

    if not found:
        print("No task found with that title")
        return  # Early return if the task is not found

    with open("tasks.txt", "w") as task_file:
        task_data = []
        for t in task_list:
            task_data.append(
                f"{t['username']};{t['title']};{t['description']};{t['due_date'].strftime(DATETIME_STRING_FORMAT)};"
                f"{t['assigned_date'].strftime(DATETIME_STRING_FORMAT)};{'Yes' if t['completed'] else 'No'}"
            )
        task_file.write("\n".join(task_data))

    print("Task modified successfully!")
    generate_reports()


def generate_reports():
    """
    Generate task_overview.txt and user_overview.txt reports with task and user statistics.
    """
    task_overview = {
        "total": len(task_list),
        "completed": sum(1 for task in task_list if task["completed"]),
        "incomplete": sum(1 for task in task_list if not task["completed"]),
        "incomplete_overdue": sum(1 for task in task_list if not task["completed"] and task["due_date"].date() < date.today()),
    }

    user_overview = {
        "total_users": len(username_password),
        "user_tasks": {},
    }

    for task in task_list:
        if task["username"] not in user_overview["user_tasks"]:
            user_overview["user_tasks"][task["username"]] = {
                "total_assigned": 0,
                "completed": 0,
                "incomplete": 0,
                "overdue": 0,
            }
        user_overview["user_tasks"][task["username"]]["total_assigned"] += 1
        if task["completed"]:
            user_overview["user_tasks"][task["username"]]["completed"] += 1
        elif task["due_date"].date() < date.today():
            user_overview["user_tasks"][task["username"]]["overdue"] += 1
        else:
            user_overview["user_tasks"][task["username"]]["incomplete"] += 1

    with open("task_overview.txt", "w") as task_file:
        task_file.write("Task Overview\n")
        task_file.write(f"Number of tasks generated: {task_overview['total']}\n")
        task_file.write(f"Completed: {task_overview['completed']}\n")
        task_file.write(f"Incomplete: {task_overview['incomplete']}\n")
        task_file.write(f"Incomplete + Overdue: {task_overview['incomplete_overdue']}\n")
        if task_overview['total'] != 0:
            task_file.write(f"Percentage Incomplete: {task_overview['incomplete'] / task_overview['total'] * 100:.2f}%\n")
        else:
            task_file.write("Percentage Incomplete: 0%\n")

    with open("user_overview.txt", "w") as user_file:
        user_file.write("User Overview\n")
        user_file.write(f"Total number of users generated: {user_overview['total_users']}\n")
        for username, tasks in user_overview['user_tasks'].items():
            total_assigned = tasks['total_assigned']
            completed = tasks['completed']
            incomplete = tasks['incomplete']
            overdue = tasks['overdue']
            user_file.write(f"\nUser: {username}\n")
            user_file.write(f"Number of tasks assigned: {total_assigned}\n")
            if total_assigned != 0:
                user_file.write(f"Percentage of total assigned: {total_assigned / task_overview['total'] * 100:.2f}%\n")
                user_file.write(f"Percentage of assigned tasks completed: {completed / total_assigned * 100:.2f}%\n")
                user_file.write(f"Percentage of assigned tasks incomplete: {incomplete / total_assigned * 100:.2f}%\n")
                user_file.write(f"Percentage of assigned tasks overdue: {overdue / total_assigned * 100:.2f}%\n")
            else:
                user_file.write("Percentage of total assigned: 0%\n")
                user_file.write("Percentage of assigned tasks completed: 0%\n")
                user_file.write("Percentage of assigned tasks incomplete: 0%\n")
                user_file.write("Percentage of assigned tasks overdue: 0%\n")


def add_task():
    """
    Add a new task by entering the assigned username, task title, description, and due date.
    """
    task_username = input("Name of person assigned to task: ")
    if task_username not in username_password.keys():
        print("User does not exist. Please enter a valid username")
        return
    task_title = input("Title of Task: ")
    task_description = input("Description of Task: ")
    while True:
        try:
            task_due_date = input("Due date of task (YYYY-MM-DD): ")
            due_date_time = datetime.strptime(task_due_date, DATETIME_STRING_FORMAT)
            break
        except ValueError:
            print("Invalid datetime format. Please use the format specified")
    curr_date = date.today()
    new_task = {
        "username": task_username,
        "title": task_title,
        "description": task_description,
        "due_date": due_date_time,
        "assigned_date": curr_date,
        "completed": False
    }
    task_list.append(new_task)
    with open("tasks.txt", "a") as task_file:
        task_file.write(
            f"\n{task_username};{task_title};{task_description};{due_date_time.strftime(DATETIME_STRING_FORMAT)};{curr_date.strftime(DATETIME_STRING_FORMAT)};No"
        )
    print("Task added successfully!")


def display_statistics():
    """
    Read and display the contents of user_overview.txt and task_overview.txt reports.
    Only accessible to admin users.
    """
    if curr_user not in ADMIN_USERNAMES:
        print("You need to log in as an admin to display statistics.")
        return

    if not os.path.exists("user_overview.txt") or not os.path.exists("task_overview.txt"):
        generate_reports()

    with open("user_overview.txt", "r") as user_file:
        print(user_file.read())

    with open("task_overview.txt", "r") as task_file:
        print(task_file.read())


def validate_date(date_string):
    """
    Validate a date string and return a datetime.date object if the format is valid, else return None.
    """
    try:
        date_obj = datetime.strptime(date_string, DATETIME_STRING_FORMAT).date()
        return date_obj
    except ValueError:
        return None


def view_mine():
    """
    View and modify tasks assigned to the current user.
    """
    username = curr_user
    tasks = list_tasks(username)
    if not tasks:
        print("No tasks found.")
        return  # Early return if no tasks are found

    task_number = input("Enter the number of the task you want to modify: ")
    if not task_number.isdigit() or int(task_number) >= len(tasks):
        print("Invalid task number.")
        return  # Early return if the task number is invalid

    task = tasks[int(task_number)]
    print(f"Editing Task: {task['title']}")
    task_description = input("Enter new description for the task: ")
    task_due_date = input("Enter the new due date (YYYY-MM-DD): ")
    new_due_date = validate_date(task_due_date)
    if new_due_date is None:
        print("Invalid date format. Please use the format specified.")
        return  # Early return if the date format is invalid

    task['description'] = task_description
    task['due_date'] = new_due_date

    with open("tasks.txt", "w") as task_file:
        task_data = []
        for t in task_list:
            task_data.append(
                f"{t['username']};{t['title']};{t['description']};{t['due_date'].strftime(DATETIME_STRING_FORMAT)};"
                f"{t['assigned_date'].strftime(DATETIME_STRING_FORMAT)};{'Yes' if t['completed'] else 'No'}"
            )
        task_file.write("\n".join(task_data))

    print("Task modified successfully!")
    generate_reports()
# Prompt the user for actions
while True:
    print("\nMENU")
    print("1. Register User")
    print("2. Add Task")
    print("3. List All Tasks")
    print("4. Mark Task as Complete")
    print("5. Edit Task Details")
    print("6. Generate Reports")
    print("7. View Task by Name (View and Modify My Tasks)")
    print("8. Display Statistics")
    print("9. Quit")

    choice = input("Enter your choice (1-9): ")

    if choice == "1":
        reg_user()
    elif choice == "2":
        add_task()
    elif choice == "3":
        list_tasks()
    elif choice == "4":
        task_title = input("Enter the title of the task to mark as complete: ")
        mark_complete(task_title)
    elif choice == "5":
        edit_task()
    elif choice == "6":
        if curr_user in ADMIN_USERNAMES:
            generate_reports()
            print("Reports generated successfully!")
        else:
            print("You need to log in as an admin to generate reports.")
    elif choice == "7":
        view_task_by_name()
    elif choice == "8":
        if curr_user in ADMIN_USERNAMES:
            display_statistics()
        else:
            print("You need to log in as an admin to display statistics.")
    elif choice == "9":
        break
    else:
        print("Invalid choice. Please select a valid option.")