import sys
import json
import os
from datetime import datetime


class TaskTracker:
    def __init__(self, db_file="tasks.json"):
        self.db_file = db_file
        self.tasks = self.load_tasks()

    def load_tasks(self):
        """Load tasks from the database file"""
        if not os.path.exists(self.db_file):
            return {}

        try:
            with open(self.db_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def save_tasks(self):
        """Save tasks to the database file"""
        with open(self.db_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)

    def add_task(self, description):
        """Add a new task"""
        if not description:
            print("Error: Task description cannot be empty")
            return False

        task_id = str(max([int(k) for k in self.tasks.keys()] + [0]) + 1)

        self.tasks[task_id] = {
            'description': description,
            'status': 'todo',
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat(),
        }

        self.save_tasks()
        print(f"Task added successfully (ID: {task_id})")
        return True

    def update_task(self, task_id, new_description):
        """Update an existing task"""
        if task_id not in self.tasks:
            print(f"Error: Task with ID {task_id} not found")
            return False

        if not new_description:
            print("Error: Task description cannot be empty")
            return False

        self.tasks[task_id]['description'] = new_description
        self.tasks[task_id]['updatedAt'] = datetime.now().isoformat()

        self.save_tasks()
        print(f"Task {task_id} updated successfully")
        return True

    def delete_task(self, task_id):
        """Delete a task"""
        if task_id not in self.tasks:
            print(f"Error: Task with ID {task_id} not found")
            return False

        del self.tasks[task_id]
        self.save_tasks()
        print(f"Task {task_id} deleted successfully")
        return True

    def mark_in_progress(self, task_id):
        """Mark a task as in progress"""
        return self._update_status(task_id, 'in-progress')

    def mark_done(self, task_id):
        """Mark a task as done"""
        return self._update_status(task_id, 'done')

    def _update_status(self, task_id, status):
        """Internal method to update task status"""
        if task_id not in self.tasks:
            print(f"Error: Task with ID {task_id} not found")
            return False

        self.tasks[task_id]['status'] = status
        self.tasks[task_id]['updatedAt'] = datetime.now().isoformat()

        self.save_tasks()
        print(f"Task {task_id} marked as {status}")
        return True

    def list_tasks(self, status_filter=None):
        """List tasks, optionally filtered by status"""
        if not self.tasks:
            print("No tasks found")
            return

        headers = ["ID", "Description", "Status", "Created", "Updated"]
        print(f"{headers[0]:<4} {headers[1]:<30} {headers[2]:<12} {headers[3]:<20} {headers[4]:<20}")
        print("-" * 90)

        for task_id, task in sorted(self.tasks.items(), key=lambda x: int(x[0])):
            if status_filter and task['status'] != status_filter:
                continue

            # Format dates for better display
            created = datetime.fromisoformat(task['createdAt']).strftime('%Y-%m-%d %H:%M')
            updated = datetime.fromisoformat(task['updatedAt']).strftime('%Y-%m-%d %H:%M')

            # Truncate description if too long
            desc = task['description']
            if len(desc) > 28:
                desc = desc[:25] + "..."

            print(f"{task_id:<4} {desc:<30} {task['status']:<12} {created:<20} {updated:<20}")

    def list_by_status(self, status):
        """List tasks by specific status"""
        valid_statuses = ['todo', 'in-progress', 'done']
        if status not in valid_statuses:
            print(f"Error: Invalid status. Use one of: {', '.join(valid_statuses)}")
            return False

        self.list_tasks(status_filter=status)
        return True


def print_usage():
    """Print usage instructions"""
    print(
        """
Task Tracker - CLI Task Management System

Usage:
  python3 task_tracker.py add "Task description"
  python3 task_tracker.py update <task_id> "New description"
  python3 task_tracker.py delete <task_id>
  python3 task_tracker.py mark-in-progress <task_id>
  python3 task_tracker.py mark-done <task_id>
  python3 task_tracker.py list
  python3 task_tracker.py list <status>

Status options: todo, in-progress, done

Examples:
  python3 task_tracker.py add "Buy groceries"
  python3 task_tracker.py update 1 "Buy groceries and cook dinner"
  python3 task_tracker.py list done
    """
    )


def main():
    if len(sys.argv) < 2:
        print_usage()
        return

    tracker = TaskTracker()
    command = sys.argv[1].lower()

    try:
        if command == 'add':
            if len(sys.argv) < 3:
                print("Error: Task description required")
                return
            tracker.add_task(sys.argv[2])

        elif command == 'update':
            if len(sys.argv) < 4:
                print("Error: Task ID and new description required")
                return
            tracker.update_task(sys.argv[2], sys.argv[3])

        elif command == 'delete':
            if len(sys.argv) < 3:
                print("Error: Task ID required")
                return
            tracker.delete_task(sys.argv[2])

        elif command == 'mark-in-progress':
            if len(sys.argv) < 3:
                print("Error: Task ID required")
                return
            tracker.mark_in_progress(sys.argv[2])

        elif command == 'mark-done':
            if len(sys.argv) < 3:
                print("Error: Task ID required")
                return
            tracker.mark_done(sys.argv[2])

        elif command == 'list':
            if len(sys.argv) > 2:
                tracker.list_by_status(sys.argv[2])
            else:
                tracker.list_tasks()

        else:
            print(f"Error: Unknown command '{command}'")
            print_usage()

    except Exception as e:
        print(f"Error: {str(e)}")
        print_usage()


if __name__ == "__main__":
    main()
