import sys
import json
import os
from datetime import datetime, timedelta


def get_display_width(text):
    """
    Calculate the display width of a string in the terminal
    """
    width = 0
    for char in text:
        # Unicode Range for Chinese Characters
        if (
            '\u4e00' <= char <= '\u9fff'
            or '\u3400' <= char <= '\u4dbf'
            or '\uf900' <= char <= '\ufaff'
            or '\u3000' <= char <= '\u303f'
        ):
            width += 2
        else:
            width += 1
    return width


def pad_text(text, width, align='left'):
    """
    Fill text to specified display width
    """
    text_width = get_display_width(text)
    if text_width >= width:
        return text

    padding = width - text_width
    if align == 'left':
        return text + ' ' * padding
    elif align == 'right':
        return ' ' * padding + text
    else:  # center
        left_padding = padding // 2
        right_padding = padding - left_padding
        return ' ' * left_padding + text + ' ' * right_padding


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

    def add_task(self, description, due_date=None):
        """Add a new task with optional due date"""
        if not description:
            print("Error: Task description cannot be empty")
            return False

        task_id = str(max([int(k) for k in self.tasks.keys()] + [0]) + 1)

        # Parse due date if provided
        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = self.parse_due_date(due_date)
                if not parsed_due_date:
                    return False
            except ValueError as e:
                print(f"Error: {str(e)}")
                return False

        self.tasks[task_id] = {
            'description': description,
            'status': 'todo',
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat(),
            'dueDate': parsed_due_date.isoformat() if parsed_due_date else None,
        }

        self.save_tasks()
        print(f"Task added successfully (ID: {task_id})")
        return True

    def update_task(self, task_id, new_description, due_date=None):
        """Update an existing task"""
        if task_id not in self.tasks:
            print(f"Error: Task with ID {task_id} not found")
            return False

        if not new_description:
            print("Error: Task description cannot be empty")
            return False

        # Parse due date if provided
        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = self.parse_due_date(due_date)
                if not parsed_due_date:
                    return False
            except ValueError as e:
                print(f"Error: {str(e)}")
                return False
        elif due_date == "":  # Empty string means remove due date
            parsed_due_date = None

        self.tasks[task_id]['description'] = new_description
        self.tasks[task_id]['updatedAt'] = datetime.now().isoformat()

        # Update due date if provided
        if due_date is not None:  # Note: empty string is handled above
            self.tasks[task_id]['dueDate'] = parsed_due_date.isoformat() if parsed_due_date else None

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

    def parse_due_date(self, due_date_str):
        """Parse due date string into datetime object"""
        # Try different date formats
        formats = [
            '%Y-%m-%d',  # 2025-10-27
            '%Y-%m-%d %H:%M',  # 2025-10-27 14:30
            '%Y/%m/%d',  # 2025/10/27
            '%Y/%m/%d %H:%M',  # 2025/10/27 14:30
            '%d-%m-%Y',  # 27-10-2025
            '%d/%m/%Y',  # 27/10/2025
        ]

        for fmt in formats:
            try:
                return datetime.strptime(due_date_str, fmt)
            except ValueError:
                continue

        # Try relative dates (e.g., +1d, +2w, +3m)
        if due_date_str.startswith('+'):
            return self.parse_relative_date(due_date_str)

        raise ValueError(
            f"Invalid due date format: {due_date_str}. Use formats like: 2025-10-27, 2025-10-27 14:30, +1d, +2w, +3m"
        )

    def parse_relative_date(self, relative_str):
        """Parse relative date strings like +1d, +2w, +3m"""
        try:
            # Remove the + sign
            value_str = relative_str[1:-1]
            unit = relative_str[-1].lower()

            value = int(value_str)
            today = datetime.now()

            if unit == 'd':  # days
                return today + timedelta(days=value)
            elif unit == 'w':  # weeks
                return today + timedelta(weeks=value)
            elif unit == 'm':  # months (approximate)
                # This is a simplification - doesn't handle month boundaries perfectly
                return today + timedelta(days=value * 30)
            else:
                raise ValueError(f"Unknown time unit: {unit}. Use d (days), w (weeks), or m (months)")
        except (ValueError, IndexError):
            raise ValueError(f"Invalid relative date format: {relative_str}. Use formats like: +1d, +2w, +3m")

    def sort_tasks(self, tasks_dict, sort_by='due'):
        """Sort tasks by specified criteria"""
        tasks_list = [(task_id, task) for task_id, task in tasks_dict.items()]

        if sort_by == 'due':
            # Sort by due date (tasks without due date go to the end)
            tasks_list.sort(
                key=lambda x: (
                    datetime.max if not x[1].get('dueDate') else datetime.fromisoformat(x[1]['dueDate']),
                    int(x[0]),
                )
            )
        elif sort_by == 'created':
            # Sort by creation date (newest first)
            tasks_list.sort(key=lambda x: (datetime.fromisoformat(x[1]['createdAt']), int(x[0])), reverse=True)
        elif sort_by == 'updated':
            # Sort by update date (newest first)
            tasks_list.sort(key=lambda x: (datetime.fromisoformat(x[1]['updatedAt']), int(x[0])), reverse=True)
        elif sort_by == 'status':
            # Sort by status (todo -> in-progress -> done)
            status_order = {'todo': 0, 'in-progress': 1, 'done': 2}
            tasks_list.sort(
                key=lambda x: (
                    status_order[x[1]['status']],
                    datetime.max if not x[1].get('dueDate') else datetime.fromisoformat(x[1]['dueDate']),
                    int(x[0]),
                )
            )
        elif sort_by == 'id':
            # Sort by ID
            tasks_list.sort(key=lambda x: int(x[0]))
        else:
            # Default: sort by due date
            tasks_list.sort(
                key=lambda x: (
                    datetime.max if not x[1].get('dueDate') else datetime.fromisoformat(x[1]['dueDate']),
                    int(x[0]),
                )
            )

        return dict(tasks_list)

    def list_tasks(self, status_filter=None, sort_by='due'):
        """List tasks, optionally filtered by status and sorted"""
        if not self.tasks:
            print("No tasks found")
            return

        # Filter and sort tasks
        filtered_tasks = {}
        for task_id, task in self.tasks.items():
            if status_filter and task['status'] != status_filter:
                continue
            filtered_tasks[task_id] = task

        sorted_tasks = self.sort_tasks(filtered_tasks, sort_by)

        # 定义列宽（显示宽度）
        col_widths = {
            'id': 6,  # ID列宽
            'description': 30,  # 描述列宽
            'status': 12,  # 状态列宽
            'due_date': 18,  # 截止日期列宽
            'created': 16,  # 创建时间列宽
            'updated': 16,  # 更新时间列宽
        }

        # 表头
        headers = {
            'id': "ID",
            'description': "Description",
            'status': "Status",
            'due_date': "Due Date",
            'created': "Created",
            'updated': "Updated",
        }

        # 打印表头
        header_line = (
            pad_text(headers['id'], col_widths['id'])
            + " "
            + pad_text(headers['description'], col_widths['description'])
            + " "
            + pad_text(headers['status'], col_widths['status'])
            + " "
            + pad_text(headers['due_date'], col_widths['due_date'])
            + " "
            + pad_text(headers['created'], col_widths['created'])
            + " "
            + pad_text(headers['updated'], col_widths['updated'])
        )
        print(header_line)

        # 打印分隔线
        separator = "-" * (
            col_widths['id']
            + col_widths['description']
            + col_widths['status']
            + col_widths['due_date']
            + col_widths['created']
            + col_widths['updated']
            + 5
        )
        print(separator)

        for task_id, task in sorted_tasks.items():
            # 格式化日期
            created = datetime.fromisoformat(task['createdAt']).strftime('%m/%d %H:%M')
            updated = datetime.fromisoformat(task['updatedAt']).strftime('%m/%d %H:%M')

            # 格式化截止日期
            due_date = "No due date"
            if task.get('dueDate'):
                due_datetime = datetime.fromisoformat(task['dueDate'])
                due_date = due_datetime.strftime('%m/%d %H:%M')

                # 高亮过期任务
                if due_datetime < datetime.now() and task['status'] != 'done':
                    due_date = f"*{due_date}*"

            # 处理描述文本，确保不超过列宽
            desc = task['description']
            desc_width = get_display_width(desc)
            if desc_width > col_widths['description']:
                # 如果描述太长，需要截断
                truncated = ""
                current_width = 0
                for char in desc:
                    char_width = get_display_width(char)
                    if current_width + char_width <= col_widths['description'] - 3:  # 保留3个位置给"..."
                        truncated += char
                        current_width += char_width
                    else:
                        break
                desc = truncated + "..."

            # 打印任务行，使用pad_text确保对齐
            task_line = (
                pad_text(task_id, col_widths['id'], 'right')
                + " "
                + pad_text(desc, col_widths['description'])
                + " "
                + pad_text(task['status'], col_widths['status'])
                + " "
                + pad_text(due_date, col_widths['due_date'])
                + " "
                + pad_text(created, col_widths['created'])
                + " "
                + pad_text(updated, col_widths['updated'])
            )
            print(task_line)

    def list_by_status(self, status, sort_by='due'):
        """List tasks by specific status"""
        valid_statuses = ['todo', 'in-progress', 'done']
        if status not in valid_statuses:
            print(f"Error: Invalid status. Use one of: {', '.join(valid_statuses)}")
            return False

        self.list_tasks(status_filter=status, sort_by=sort_by)
        return True


def print_usage():
    """Print usage instructions"""
    print(
        """
Task Tracker - CLI Task Management System

Usage:
  cli add "Task description" [due_date]
  cli update <task_id> "New description" [due_date]
  cli delete <task_id>
  cli mark-in-progress <task_id>
  cli mark-done <task_id>
  cli list [status] [sort_by]

Status options: todo, in-progress, done
Sort options: due (default), created, updated, status, id

Due Date formats:
  Absolute: 2025-10-27, 2025-10-27 14:30, 2025/10/27
  Relative: +1d (1 day), +2w (2 weeks), +3m (3 months)

Examples:
  cli add "Buy groceries" 2025-10-27
  cli add "Write report" +1w
  cli update 1 "Buy groceries and cook dinner" 2025-10-27
  cli update 2 "Write final report" ""  # Remove due date
  cli list
  cli list done
  cli list todo status  # Sort by status
  cli list created      # Sort by creation date
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

            due_date = sys.argv[3] if len(sys.argv) > 3 else None
            tracker.add_task(sys.argv[2], due_date)

        elif command == 'update':
            if len(sys.argv) < 4:
                print("Error: Task ID and new description required")
                return

            due_date = sys.argv[4] if len(sys.argv) > 4 else None
            tracker.update_task(sys.argv[2], sys.argv[3], due_date)

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
            status = None
            sort_by = 'due'

            # Parse optional status and sort parameters
            if len(sys.argv) > 2:
                for arg in sys.argv[2:]:
                    if arg in ['todo', 'in-progress', 'done']:
                        status = arg
                    elif arg in ['due', 'created', 'updated', 'status', 'id']:
                        sort_by = arg

            if status:
                tracker.list_by_status(status, sort_by)
            else:
                tracker.list_tasks(sort_by=sort_by)

        else:
            print(f"Error: Unknown command '{command}'")
            print_usage()

    except Exception as e:
        print(f"Error: {str(e)}")
        print_usage()


if __name__ == "__main__":
    main()
