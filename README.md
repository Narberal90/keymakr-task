
# Python Scripts

This repository contains a collection of Python scripts for various tasks including API data fetching, file processing, log analysis, and task management.

## Before we start - please make the necessary preparations:
**Make sure you have Python installed on your machine.**

You can check if Python is installed by running the following command:
```bash
python --version
```
or
```bash
python3 --version
```

**Clone the repository to your local machine:**

```bash
git clone https://github.com/Narberal90/keymakr-task.git   
```
**Navigate to the project directory**
```bash
cd keymakr_task
```

**Create a virtual environment**
```bash
python -m venv venv
```

**Activate the virtual environment**

*Linux/macOS:*
```bash
source venv/bin/activate
```

*On Windows:*
```bash
venv\Scripts\activate
```

**Install dependencies**
```bash
pip install -r requirements.txt
```


## Task 1: Working with APIs and Multithreading

This script fetches data from an API (JSONPlaceholder) asynchronously and saves it to an SQLite database.

### Features:
- Fetches data asynchronously using `aiohttp`.
- Handles errors.
- Stores the data in a CSV file named `posts.csv` with columns: `id`, `user_id`, `title`, `body`.
- Implements logging for the API requests.

### Usage:
```bash
cd script_fetch_data
```

```bash
python fetch_posts.py --start 1 --end 20 
```
or to see test bad requests

```bash
python fetch_posts.py --test
```

## Task 2: File Processing and XML/JSON Conversion

This script converts XML files containing data into JSON format and saves them in a directory.

### Features:
- Parses XML files with product data.
- Validates the data.
- Converts XML to JSON and saves it in the specified output directory.
- Supports command-line arguments for input and output directories.

### Usage:
```bash
cd file_processing_xml_json
```
```bash
python convert_xml_to_json.py --input-dir /path/to/xml --output-dir /path/to/json
```

## Task 3: CLI Tool for Log Analysis

This script analyzes web server logs in Nginx format and generates a report on the most frequent IPs, errors, and average response size.

### Features:
- Identifies the top 5 IP addresses with the most requests.
- Finds the most frequent errors (4xx and 5xx status codes).
- Calculates the average response size.

### Usage:
```bash
cd log_analysis_cli
```

```bash
python log_analyzer.py /path/to/log/file.log
```
or for testing
```bash
python log_analyzer.py access.log
```

## Task 4: Task Manager with SQLite

This task management system uses SQLite to manage tasks, and a command-line interface (CLI) to interact with the system.

## Features

- Add tasks with title, description, due date, and status (pending, in_progress, completed).
- Update task status.
- Delete tasks.
- List all tasks sorted by their due date.
- Interactive mode for easy task management.
- Built-in logging for tracking operations.

### Usage:
### First:
```bash
cd script_task_manager
```
### 1. Interactive Mode
Simply run the script without any arguments:
```bash
python task_manager.py
```
You will be prompted to enter commands like:

- `add` - Add a new task.
- `update` - Update a task's status.
- `delete` - Delete a task.
- `list` - List all tasks.
- `exit` - Exit the application.
- `help` - Show available commands.

### 2. CLI Mode

You can also perform tasks through the command line by using the following options:

- `--add`: Add a new task.
  - `--title`: Title of the task.
  - `--description`: Description of the task (optional).
  - `--due_date`: Due date of the task in `YYYY-MM-DD` format.
  - `--status`: Status of the task (optional, default is `pending`).

- `--update`: Update a task's status.
  - `--status`: New status (`pending`, `in_progress`, or `completed`).
  - `task_id`: Task ID to update (directly specify the task ID as a number).
- `--delete`: Delete a task.
  - `task_id`: Task ID to delete (directly specify the task ID as a number).
- `--list`: List all tasks sorted by due date.

### Example Commands

- Add a task:
```bash
  python task_manager.py --add --title "Buy milk" --due_date 2025-02-10 --status "pending"
```
- Update a task's status:
```bash
python task_manager.py --update 1 --status "completed"
```
- Delete a task:
```bash
python task_manager.py --delete 1
```
- List all tasks:
```bash
python task_manager.py --list
```

## Logging
The application logs all operations (such as adding, updating, and deleting tasks) to the console. You can see detailed logs of the script’s activity, including errors and successful operations.