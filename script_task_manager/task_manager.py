import argparse
from contextlib import contextmanager
from datetime import datetime
import sqlite3
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

DB_PATH = "tasks.db"

VALID_STATUSES = {"pending", "in_progress", "completed"}


class TaskManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._initialize_db()

    @contextmanager
    def get_db_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.commit()
            conn.close()

    def _is_valid_integer(self, value):
        try:
            int_value = int(value)
            return str(int_value) == value and "." not in value
        except ValueError:
            return False

    def _initialize_db(self):
        db_file = Path(self.db_path)
        db_exists = db_file.exists()
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    due_date TEXT NOT NULL,
                    status TEXT CHECK(status IN ('pending', 'in_progress', 'completed')) NOT NULL DEFAULT 'pending'
                )"""
            )
        if not db_exists:
            logger.info("Database initialized.")

    def add_task(self, title, description, due_date, status=None):
        if not title:
            logger.error("Title is required.")
        if status is None:
            status = "pending"
            logger.info("No status provided. Defaulting to 'pending'.")

        elif status not in VALID_STATUSES:
            logger.error(
                f"Invalid status: '{status}'. Choose from {VALID_STATUSES}."
            )
            return

        try:
            datetime.strptime(due_date, "%Y-%m-%d")
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO tasks (title, description, due_date, status) VALUES (?, ?, ?, ?)",
                    (title, description, due_date, status),
                )
            logger.info(f"Task '{title}' added successfully.")

        except (TypeError, ValueError):
            logger.error("Invalid date format! Use YYYY-MM-DD.")
        except sqlite3.IntegrityError as e:
            logger.error(f"Integrity error: {e}")
        except sqlite3.DatabaseError as e:
            logger.error(f"Database error: {e}")

    def update_task_status(self, task_id, status):
        if not self._is_valid_integer(task_id):
            logger.error(
                f"Invalid task ID: {task_id}. It must be a valid integer."
            )
            return

        if status not in VALID_STATUSES:
            logger.error(
                f"Invalid status: '{status}'. Choose from {VALID_STATUSES}."
            )
            return

        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM tasks WHERE id = ?", (task_id,)
                )
                if cursor.fetchone()[0] == 0:
                    logger.error(f"Task with ID {task_id} does not exist.")
                    return

                cursor.execute(
                    "UPDATE tasks SET status = ? WHERE id = ?",
                    (status, task_id),
                )
            logger.info(f"Task {task_id} updated to status '{status}'.")

        except sqlite3.IntegrityError as e:
            logger.error(f"Integrity error: {e}")
        except sqlite3.DatabaseError as e:
            logger.error(f"Database error: {e}")

    def list_tasks(self):
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, title, description, due_date, status FROM tasks ORDER BY due_date"
                )
                tasks = cursor.fetchall()

            if tasks:
                logger.info("Listing tasks:")
                for task in tasks:
                    logger.info(
                        f"[{task[0]}] {task[1]} (Due: {task[3]}, "
                        f"Status: {task[4]}) - {task[2] or 'No description'}"
                    )
            else:
                logger.info("No tasks found.")

        except sqlite3.DatabaseError as e:
            logger.error(f"Database error while listing tasks: {e}")

    def delete_task(self, task_id):
        if not self._is_valid_integer(task_id):
            logger.error(
                f"Invalid task ID: {task_id}. It must be a valid integer."
            )
            return
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM tasks WHERE id = ?", (task_id,)
                )
                if cursor.fetchone()[0] == 0:
                    logger.error(f"Task with ID {task_id} doesn't exist.")
                    return

                cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            logger.info(f"Task {task_id} deleted.")

        except sqlite3.DatabaseError as e:
            logger.error(f"Database error while deleting task {task_id}: {e}")


def interactive_mode():
    manager = TaskManager()
    print("\nWelcome to Task Manager CLI!")
    print("Type 'help' to see available commands. Type 'exit' to quit.")

    while True:
        command = (
            input(
                "\nEnter command (add, update, delete, list, exit, or help): "
            )
            .strip()
            .lower()
        )

        if command == "exit":
            print("Exiting Task Manager. Goodbye!")
            break
        elif command == "help":
            print("\nCommands:")
            print("  add     - Add a new task")
            print("  update  - Update task status")
            print("  delete  - Delete a task")
            print("  list    - List all tasks")
            print("  exit    - Exit the Task Manager")
        elif command == "add":
            while True:
                title = input(
                    "Enter task title (or type 'back' to return): "
                ).strip()
                if title.lower() == "back":
                    break
                due_date = input("Enter due date (YYYY-MM-DD): ").strip()
                description = input("Enter description (optional): ").strip()
                status_input = input(
                    "Enter status (pending, in_progress, completed): "
                ).strip()
                status = status_input if status_input else None

                manager.add_task(
                    title,
                    description if description else None,
                    due_date,
                    status,
                )

        elif command == "update":
            while True:
                task_id = input(
                    "Enter task ID to update (or 'back' to return): "
                ).strip()
                if task_id.lower() == "back":
                    break
                status = input(
                    "Enter new status (pending, in_progress, completed): "
                ).strip()

                manager.update_task_status(task_id, status)

        elif command == "delete":
            while True:
                task_id = input(
                    "Enter task ID to delete (or 'back' to return): "
                ).strip()
                if task_id.lower() == "back":
                    break

                manager.delete_task(task_id)

        elif command == "list":
            manager.list_tasks()
        else:
            print("Invalid command. Type 'help' for available commands.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Task Manager CLI",
        epilog=(
            "Example: python task_manager.py --add --title 'Buy milk' "
            "--due_date 2025-02-10"
        ),
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--add", action="store_true", help="Add a new task")
    group.add_argument(
        "--update", help="Update a task's status (provide task ID)"
    )
    group.add_argument("--delete", help="Delete a task (provide task ID)")
    group.add_argument("--list", action="store_true", help="List all tasks")
    parser.add_argument("--title", help="Title of the task")
    parser.add_argument(
        "--description", help="Description of the task (optional)"
    )
    parser.add_argument("--due_date", help="Due date of the task (YYYY-MM-DD)")
    parser.add_argument(
        "--status",
        choices=["pending", "in_progress", "completed"],
        help="If nothing is selected - 'pending' default",
    )

    args = parser.parse_args()
    manager = TaskManager()

    if args.add:
        manager.add_task(
            args.title,
            args.description or None,
            args.due_date,
            args.status or None,
        )
    elif args.update:
        if not args.status:
            logger.error("Please specify a status to update.")
        else:
            manager.update_task_status(args.update, args.status)
    elif args.delete:
        manager.delete_task(args.delete)
    elif args.list:
        manager.list_tasks()
    else:
        interactive_mode()
