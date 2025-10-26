# README

```bash
CLI/
├── cli
│   ├── __init__.py
│   └── main.py
├── pyproject.toml
├── README.md
├── requirements.txt
└── setup.py
```

This is a CLI time management tool. It is implemented in the terminal.

## Features

- Overdue Tasks Highlighted: Tasks that are overdue and uncompleted will be marked with `*`.
- Clear display format: A visually appealing and streamlined table layout that displays deadlines and supports Chinese characters.
- Flexible command-line arguments: Supports specifying both status and sorting method simultaneously in the list command.

## Set up

```bash
git clone https://github.com/scp020/CLI.git
cd CLI
pip install -e .
```

If you want, you can do this before `pip install`:

```bash
python -m venv env
source env/bin/activate
```

Check if the installation was successful: `pip list | grep cli`.

## Usage

```bash
# Overview

cli add "Task description" [due_date]
cli update <task_id> "New description" [due_date]
cli delete <task_id>
cli mark-in-progress <task_id>
cli mark-done <task_id>
cli list [status] [sort_by]

# Examples

# Add a new task
cli add "Buy groceries"
cli add "Buy groceries" 2025-10-27
cli add "Write report" +1w  # due in 1 week

# List all tasks (sorted by due date by default)
cli list

# List tasks by status with different sorting
cli list done
cli list todo status  # sort by status
cli list created      # sort by creation date

# Mark task as in progress or done
cli mark-in-progress 1
cli mark-done 1

# Update a task and its due date
cli update 1 "Buy groceries and cook dinner" 2025-10-27
cli update 2 "Write final report" ""  # remove due date

# Delete a task
cli delete 1
```

## List options

```bash
Status options: todo, in-progress, done
Sort options: due (default), created, updated, status, id
```

- `due` (default): Sort by due date
- `created`: Sort by creation date (newest first)
- `updated`: Sort by last update date (newest first)
- `status`: Sort by status (todo → in-progress → done)
- `id`: Sort by task ID

## Due Date formats

```bash
Absolute: 2025-10-27, 2025-10-27 14:30, 2025/10/27
Relative: +1d (1 day), +2w (2 weeks), +3m (3 months)
```
