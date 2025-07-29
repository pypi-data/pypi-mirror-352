# Copyright (c) 2024 espehon
# MIT License

#region: Inports
import os
import sys
import argparse
import json
import datetime
import copy
from configparser import ConfigParser
import importlib.metadata
import calendar

import questionary
from dateutil.rrule import *

try:
    from tasky_cli import defaults
except ModuleNotFoundError:
    import defaults

from colorama import Fore, Back, Style, init
init(autoreset=True)

try:
    __version__ = f"tasky {importlib.metadata.version('tasky_cli')} from tasky_cli"
except importlib.metadata.PackageNotFoundError:
    __version__ = "Package not installed..."



#endregion
#region: Arguments



# Set user paths
# home = os.path.expanduser("~") # not needed?
config_path = os.path.expanduser("~/.config/tasky/").replace('\\', '/')
config_file = f"{config_path}tasky.ini"

# Set argument parsing
parser = argparse.ArgumentParser(
    description="Tasky: A to-do list program!\nBased off of klaudiosinani's Taskbook for JavaScript.",
    epilog="Examples: 'ts --task this is a new task', 'ts --switch 1', 'ts --complete 1'\nHomepage: https://github.com/espehon/tasky-cli",
    allow_abbrev=False,
    add_help=False,
    usage="ts [option] <arguments>    'try: ts --help'",
    formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument('-?', '--help', action='help', help='Show this help message and exit.')
parser.add_argument('-v', '--version', action='version', version=__version__, help="Show package version and exit.")
parser.add_argument('-t', '--task', action='store_true', help='Add a new task.')
parser.add_argument('-c', '--complete', nargs='+', metavar='T', action='store', type=int, help='Mark task(s) complete.')
parser.add_argument('-s', '--switch', nargs='+', metavar='T', action='store', type=int, help='Toggle task(s) as started/stopped.')
parser.add_argument('-f', '--flag', nargs='+', metavar='T', action='store', type=int, help='Flag task(s) with astrict (*).')
parser.add_argument('-p', '--priority', nargs=2, metavar=('T', 'P'), action='store', type=int, help='Set the priority of task [T] to [P]. Priorities: 0, 1, 2, or 3.')
parser.add_argument('-l', '--later', nargs=1, metavar='D' ,action='store', help='Buffer a task for later. Enter [D] as YYYY-MM-DD or days from today. Prompts for task description after.')
parser.add_argument('--peek', action='store_true', help='Preview scheduled tasks.')
parser.add_argument('-e', '--edit', nargs=1, metavar='T', action='store', type=int, help='Enter edit mode on a task.')
parser.add_argument('-d', '--delete', nargs='+', metavar='T', action='store', type=int, help='Mark task [T] for deletion.')
parser.add_argument('--clean', action='store_true', help='Remove complete/deleted tasks and reset indices.')
parser.add_argument('--configs', action='store_true', help='Check/reset configs.')
parser.add_argument('text', nargs=argparse.REMAINDER, help='Task description that is used with --task.')

config = ConfigParser()


# Set Variables / Constants
PRIORITIES = (0, 1, 2, 3)
DEFAULT_PRIORITY = 0

# Color name mapping for colorama
COLORS = {
    'red': {'norm': Fore.RED, 'alt': Fore.LIGHTRED_EX},
    'yellow': {'norm': Fore.YELLOW, 'alt': Fore.LIGHTYELLOW_EX},
    'green': {'norm': Fore.GREEN, 'alt': Fore.LIGHTGREEN_EX},
    'cyan': {'norm': Fore.CYAN, 'alt': Fore.LIGHTCYAN_EX},
    'blue': {'norm': Fore.BLUE, 'alt': Fore.LIGHTBLUE_EX},
    'magenta': {'norm': Fore.MAGENTA, 'alt': Fore.LIGHTMAGENTA_EX},
    'black': {'norm': Fore.BLACK, 'alt': Fore.LIGHTBLACK_EX},
    'white': {'norm': Fore.WHITE, 'alt': Fore.LIGHTWHITE_EX},

    'bright_red': {'norm': Fore.LIGHTRED_EX, 'alt': Fore.RED},
    'bright_yellow': {'norm': Fore.LIGHTYELLOW_EX, 'alt': Fore.YELLOW},
    'bright_green': {'norm': Fore.LIGHTGREEN_EX, 'alt': Fore.GREEN},
    'bright_cyan': {'norm': Fore.LIGHTCYAN_EX, 'alt': Fore.CYAN},
    'bright_blue': {'norm': Fore.LIGHTBLUE_EX, 'alt': Fore.BLUE},
    'bright_magenta': {'norm': Fore.LIGHTMAGENTA_EX, 'alt': Fore.MAGENTA},
    'bright_black': {'norm': Fore.LIGHTBLACK_EX, 'alt': Fore.BLACK},
    'bright_white': {'norm': Fore.LIGHTWHITE_EX, 'alt': Fore.WHITE}
}


# Check if config folder exists, create it if missing.
if os.path.exists(config_path) == False:
    os.makedirs(config_path)

# Check if config file exists, create it if missing.
if os.path.exists(config_file) == False:
    with open(config_file, 'w', encoding='utf-8') as settingsFile:
        settingsFile.write(defaults.default_configs)

# Read-in configs
try:
    config.read(config_file, encoding='utf-8')
except:
    print(f"{Fore.RED}FATAL: Reading config file failed!")
    sys.exit(1)



#endregion
#region: Configs



# Unpack configs dict
# variable_name = config["Settings"]["VarInFile"]
config_errors = []

try:
    data_path = config["Settings"]["taskPath"].replace('\"', '')
except:
    data_path = defaults.DEFAULT_VALUES['dataFolder']
    config_errors.append('dataFolder')

try:
    data_file = config["Settings"]["taskFile"].replace('\"', '')
except:
    data_file = defaults.DEFAULT_VALUES['dataFile']
    config_errors.append('dataFile')

try:
    schedule_file = config["Settings"]["scheduleFile"].replace('\"', '')
except:
    schedule_file = defaults.DEFAULT_VALUES['scheduleFile']
    config_errors.append('scheduleFile')

try:
    newTaskSymbol = config["Settings"]["newTaskSymbol"].replace('\"', '')
except:
    newTaskSymbol = defaults.DEFAULT_VALUES['newTaskSymbol']['plain']
    config_errors.append('newTaskSymbol')

try:
    startedTaskSymbol = config["Settings"]["startedTaskSymbol"].replace('\"', '')
except:
    startedTaskSymbol = defaults.DEFAULT_VALUES['startedTaskSymbol']['plain']
    config_errors.append('startedTaskSymbol')

try:
    stoppedTaskSymbol = config["Settings"]["stoppedTaskSymbol"].replace('\"', '')
except:
    stoppedTaskSymbol = defaults.DEFAULT_VALUES['stoppedTaskSymbol']['plain']
    config_errors.append('stoppedTaskSymbol')

try:
    completeTaskSymbol = config["Settings"]["completeTaskSymbol"].replace('\"', '')
except:
    completeTaskSymbol = defaults.DEFAULT_VALUES['completeTaskSymbol']['plain']
    config_errors.append('completeTaskSymbol')

try:
    flagSymbol = config["Settings"]["flagSymbol"].replace('\"', '')
except:
    flagSymbol = defaults.DEFAULT_VALUES['flagSymbol']['plain']
    config_errors.append('flagSymbol')

try:
    flagSymbolAlt = config["Settings"]["flagSymbolAlt"].replace('\"', '')
except:
    flagSymbolAlt = defaults.DEFAULT_VALUES['flagSymbolAlt']['plain']
    config_errors.append('flagSymbolAlt')

try:
    boarderColor = config['Settings']['boarderColor'].replace('\"', '')
except:
    boarderColor = defaults.DEFAULT_VALUES['boarderColor']
    config_errors.append('boarderColor')

try:
    newTaskColor = config["Settings"]["newTaskColor"].replace('\"', '')
except:
    newTaskColor = defaults.DEFAULT_VALUES['newTaskColor']
    config_errors.append('newTaskColor')

try:
    startedTaskColor = config["Settings"]["startedTaskColor"].replace('\"', '')
except:
    startedTaskColor = defaults.DEFAULT_VALUES['startedTaskColor']
    config_errors.append('startedTaskColor')

try:
    stoppedTaskColor = config["Settings"]["stoppedTaskColor"].replace('\"', '')
except:
    stoppedTaskColor = defaults.DEFAULT_VALUES['stoppedTaskColor']
    config_errors.append('stoppedTaskColor')

try:
    completeTaskColor = config["Settings"]["completeTaskColor"].replace('\"', '')
except:
    completeTaskColor = defaults.DEFAULT_VALUES['completeTaskColor']
    config_errors.append('completeTaskColor')

try:
    priorityColor0 = config["Settings"]["priorityColor0"].replace('\"', '')
except:
    priorityColor0 = defaults.DEFAULT_VALUES['priorityColor0']
    config_errors.append('priorityColor0')

try:
    priorityColor1 = config["Settings"]["priorityColor1"].replace('\"', '')
except:
    priorityColor1 = defaults.DEFAULT_VALUES['priorityColor1']
    config_errors.append('priorityColor1')

try:
    priorityColor2 = config["Settings"]["priorityColor2"].replace('\"', '')
except:
    priorityColor2 = defaults.DEFAULT_VALUES['priorityColor2']
    config_errors.append('priorityColor2')

try:
    priorityColor3 = config["Settings"]["priorityColor3"].replace('\"', '')
except:
    priorityColor3 = defaults.DEFAULT_VALUES['priorityColor3']
    config_errors.append('priorityColor3')

try:
    prioritySymbol0 = config["Settings"]["prioritySymbol0"].replace('\"', '')
except:
    prioritySymbol0 = defaults.DEFAULT_VALUES['prioritySymbol0']['plain']
    config_errors.append('prioritySymbol0')

try:
    prioritySymbol1 = config["Settings"]["prioritySymbol1"].replace('\"', '')
except:
    prioritySymbol1 = defaults.DEFAULT_VALUES['prioritySymbol1']['plain']
    config_errors.append('prioritySymbol1')

try:
    prioritySymbol2 = config["Settings"]["prioritySymbol2"].replace('\"', '')
except:
    prioritySymbol2 = defaults.DEFAULT_VALUES['prioritySymbol2']['plain']
    config_errors.append('prioritySymbol2')

try:
    prioritySymbol3 = config["Settings"]["prioritySymbol3"].replace('\"', '')
except:
    prioritySymbol3 = defaults.DEFAULT_VALUES['prioritySymbol3']['plain']
    config_errors.append('prioritySymbol3')

if config_errors:
    print(f"Missing the following {len(config_errors)} settings from {config_file}")
    for e in config_errors:
        print(f"\t{e}")



#endregion
#region: Setup



# Priority tables
priority_color = {
    0: priorityColor0,
    1: priorityColor1,
    2: priorityColor2,
    3: priorityColor3,
}

priority_symbol = {
    0: prioritySymbol0,
    1: prioritySymbol1,
    2: prioritySymbol2,
    3: prioritySymbol3,
}


# Prepare for data read-in
data_path = os.path.expanduser(data_path)
task_data_file = data_path + data_file
data = {}
schedule_file_path = data_path + schedule_file
schedule = {}

# Check if data folder exists, create it if missing.
if os.path.exists(data_path) == False:
    os.makedirs(data_path)


# Check if file exists, create it if missing.
if os.path.exists(task_data_file) is False:
    with open(task_data_file, 'w') as json_file:
        json.dump(data, json_file, indent=4)
if os.path.exists(schedule_file_path) is False:
    with open(schedule_file_path, 'w') as json_file:
        json.dump(schedule, json_file, indent=4)

# Read-in data
with open(task_data_file, 'r') as json_file:
    data = json.load(json_file)
with open(schedule_file_path, 'r') as json_file:
    schedule = json.load(json_file)



#endregion
#region: Functions



def add_new_task(task: dict):
    """Adds a new task dict to the data dict"""
    data.update(task)


def print_calendar(date: str) -> None:
    '''print the a calendar for the month of the given date with the date highlighted.
    date should be in the format YYYY-MM-DD'''
    try:
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        print(f"'{date}' is not a valid date.")
        sys.exit(1)

    def highlight_date(date_obj):
        year = date_obj.year
        month = date_obj.month
        day = date_obj.day

        # Set the first day of the week to Sunday
        calendar.setfirstweekday(calendar.SUNDAY)

        cal = calendar.monthcalendar(year, month)
        highlighted_cal = ""
        for week in cal:
            for i, date in enumerate(week):
                if date == 0:  # Empty day (padding)
                    highlighted_cal += "   "
                elif date == day:
                    highlighted_cal += f"{Fore.LIGHTCYAN_EX}{date:2}{Style.RESET_ALL} "
                else:
                    highlighted_cal += f"{date:2} "
            highlighted_cal += "\n"
        return highlighted_cal
    print()
    print(f"{calendar.month_name[date_obj.month]} {date_obj.year}".center(20))
    print("Su Mo Tu We Th Fr Sa")
    print(highlight_date(date_obj))
    print()


def preview_schedule():
    """Preview scheduled tasks sorted by date."""
    if not schedule:
        print("No tasks are currently scheduled.")
        return

    # Sort the schedule by date
    sorted_schedule = sorted(schedule.items(), key=lambda x: datetime.datetime.strptime(x[1]['scheduled_date'], "%Y-%m-%d"))

    # Calculate the maximum description length
    max_desc_length = max(max((len(task['task_description']) for _, task in sorted_schedule), default=0), 28)

    # Print the sorted schedule
    print(f"\n{len(sorted_schedule)} Scheduled Tasks:")
    # print(f"{'─' * 12}┬─{'─' * max_desc_length}")
    print(f"{Back.WHITE}{Fore.BLACK}{' Date':<12}{'   Description':<{max_desc_length}}▕")
    # print(f"{'─' * 12}┼─{'─' * max_desc_length}")
    for _, task in sorted_schedule:
        print(f" {task['scheduled_date']:<12}│ {task['task_description']}")
    print()


def interactive_get_rrule_string() -> str:
    """Build a string for the rrule field in the schedule file."""
    # [x] FEATURE: Add the ability to schedule recurring tasks.
    rrule_parts = []

    # [x] TODO: ask for frequency
    freq = questionary.select(
        "How often should the task recur?",
        choices=["Daily", "Weekly", "Monthly", "Yearly"]
    ).ask()
    rrule_parts.append(f"FREQ={freq.upper()}")

    # [x] TODO: ask for interval
    interval = questionary.text("Enter the interval (default is 1):", default="1").ask().strip()
    if not interval.isdigit():
        print(f"{interval} is not a valid interval. Aborting...")
        sys.exit(1)
    interval = int(interval)
    rrule_parts.append(f"INTERVAL={interval}")

    # [x] TODO: if yearly logic; months; then go to monthly logic
    if freq == "Yearly":
        months = questionary.checkbox(
            "Select the month for the yearly recurrence:",
            choices=list(calendar.month_name[1:])  # Exclude the empty first element
        ).ask()
        month_indices = [str(list(calendar.month_name).index(m)) for m in months]
        rrule_parts.append(f"BYMONTH={','.join(month_indices)}")

    # [x] TODO: if monthly logic; days of month or Nth weekday of month
    if freq == "Monthly" or freq == "Yearly":
        user = questionary.select("Select monthly method:", choices=["Nth day(s) of the month", "Nth weekday of the month"]).ask()
        if user == "Nth day(s) of the month":
            user = questionary.text("Enter days of the month as integers separated by spaces:").ask().split(' ')
            bymonthday = []
            for d in user:
                if not d.isdigit() or int(d) < 1 or int(d) > 31:
                    continue
                bymonthday.append(str(int(d)))
            rrule_parts.append(f"BYMONTHDAY={','.join(bymonthday)}")
        elif user == "Nth weekday of the month":
            byday = questionary.select(
                "Select the weekday:",
                choices=["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
            ).ask()
            nweekday = questionary.checkbox(f"Select the indices for {byday}:", choices=['1', '2', '3', '4', '5']).ask()
            rrule_parts.append(f"BYWEEKDAY={byday}({','.join(nweekday)})")

    # [x] TODO: if weekly logic; days of week
    elif freq == "Weekly":
        byday = questionary.checkbox(
            "Select the weekdays for recurrence:",
            choices=["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
        ).ask()
        rrule_parts.append(f"BYDAY={','.join(byday)}")

    # [x] TODO: ask for end date
    tries = 3
    while tries:
        edate = questionary.text("Enter the end date for this reoccurring task (YYYY-MM-DD):").ask()
        # [x] TODO: validate user input
        try:
            datetime.datetime.strptime(edate, "%Y-%m-%d").date()
            rrule_parts.append(f"UNTIL={edate}")
            break
        except ValueError:
            tries -= 1
            print(f"'{edate}' is not a valid date. You have {tries} tries left.")
            if tries == 0:
                print("Aborting...")
                sys.exit(1)
        

    rrule_string = ';'.join(rrule_parts)
    return rrule_string

def schedule_task(date: str):
    """Schedule a task for a given date. Date can be in the format YYYY-MM-DD or as a number of days from today."""
    new_entry = {}
    schedule_copy = copy.deepcopy(schedule)
    schedule_keys = index_data(schedule_copy)
    if len(schedule_keys) == 0:
        next_key = 1
    else:
        next_key = max(schedule_keys) + 1

    try:
        days_out = int(date)
        scheduled_date = datetime.datetime.today() + datetime.timedelta(days=days_out)
        scheduled_date = scheduled_date.strftime("%Y-%m-%d") # Date to str
    except ValueError:
        try:
            user_input_as_datetime = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            scheduled_date = user_input_as_datetime.strftime("%Y-%m-%d")  # Date to str so that the format is consistent
        except ValueError:
            print(f"'{date}' is not a valid date.")
            sys.exit(1)
    print_calendar(scheduled_date)
    try:
        task_description = questionary.text(f"Enter task description for {scheduled_date}:").ask().strip()
    except KeyboardInterrupt:
        print("\nTask scheduling cancelled.")
        sys.exit(1)
    # [x] TODO: ask if reoccurring task and call build_rrule_string() to save to schedule file.
    user = questionary.confirm("Is this a reoccurring task?", default=False).ask()
    if user:
        rrule_string = interactive_get_rrule_string()
    else:
        rrule_string = None
    new_entry = {
        "scheduled_date": scheduled_date,
        "task_description": task_description,
        "rrule": rrule_string
    }
    schedule[str(next_key)] = new_entry
    with open(schedule_file_path, 'w') as json_file:
        json.dump(schedule, json_file, indent=4)


def process_scheduled_tasks():
    found_priority = check_for_priority(task_description[-3:])

    if found_priority[0]:
        task_description = task_description[:-3].strip()


def update_tasks(override_data=None):
    """Write data dict to json. Allows for an optional override_data to use in place of the global data"""
    if override_data is None:
        with open(task_data_file, 'w') as json_file:
            json.dump(data, json_file, indent=4)
    else:
        with open(task_data_file, 'w') as json_file:
            json.dump(override_data, json_file, indent=4)


def color(color_name: str, alternate_style: bool=False) -> str:
    """Takes a color name like 'red' and returns its colorama formatter string.
    alternate_style switches the bright status of the given color."""
    key1 = color_name
    key2 = 'norm' if not alternate_style else 'alt'
    return COLORS[key1][key2]


def color_gradient(scale: int) -> str:
    """Takes a float between 0 and 100 inclusive and returns a colorama color"""
    if scale >= 100:
        return Fore.LIGHTWHITE_EX
    elif scale >= 87:
        return Fore.LIGHTCYAN_EX
    elif scale >= 75:
        return Fore.CYAN
    elif scale >= 62:
        return Fore.LIGHTGREEN_EX
    elif scale >= 50:
        return Fore.GREEN
    elif scale >= 37:
        return Fore.LIGHTYELLOW_EX
    elif scale >= 25:
        return Fore.YELLOW
    elif scale >= 12:
        return Fore.LIGHTRED_EX
    else:
        return Fore.RED


def index_data(current_dict: dict) -> list:
    """
    Return list of keys as int from data dict.
    This is to get around the JavaScript limitation of keys being strings
    """
    output = []
    for k in current_dict.keys():
        output.append(int(k))
    return output


def format_new_task(index: int, task_desc: str, priority: int, flagged: bool) -> dict:
    "Return new task as a dict for storage"
    output = {str(index): {
        "desc": task_desc,
        "status": 0,
        "created": str(datetime.datetime.now().date()),
        "switched": "None",
        "priority": priority,
        "flag": flagged
    }}
    return output


def check_for_priority(text: str) -> tuple:
    """
    Returns a tuple containing bool and int.
    Bool represents if the priority was passed in the task description.
    Int represents the priority.
    """
    # This could be done with a match/case block, but I want to keep the Python requirements low.
    if len(text) == 3:
        a, b, c = text
        if str.lower(a) == 'p':
            if b == ':':
                try:
                    if int(c) in PRIORITIES:
                        return (True, int(c))
                except:
                    pass
    return (False, DEFAULT_PRIORITY)


def add_scheduled_tasks():
    """Check the schedule file for any tasks that are due today and move them to the data dict."""
    today = datetime.datetime.today().date()
    tasks_to_add = {}
    schedule_copy = copy.deepcopy(schedule)

    # move due tasks from schedule to tasks_to_add
    for key, task in schedule_copy.items():
        if datetime.datetime.strptime(task['scheduled_date'], "%Y-%m-%d").date() <= today:
            tasks_to_add[key] = task
            if task.get('rrule') is None:
                schedule.pop(key)
            else:
                # Parse the rrule
                rule = rrulestr(task['rrule'], dtstart=datetime.datetime.now())

                # Get the next occurrence
                next_occurrence = rule.after(datetime.datetime.now())
                if next_occurrence is None:
                    schedule.pop(key)
                    continue

                # Format as YYYY-MM-DD
                next_date = next_occurrence.strftime("%Y-%m-%d")
                if datetime.datetime.strptime(next_date, "%Y-%m-%d").date() > today:
                    schedule[key]['scheduled_date'] = next_date
                else:
                    schedule.pop(key) # this should not happen, but just in case 
    
    if len(tasks_to_add) > 0:
        # re-order schedule due to removed tasks and overwrite json file
        new_schedule = {}
        for index, task in enumerate(schedule.values()):
            new_schedule[str(index + 1)] = task
        with open(schedule_file_path, 'w') as file:
            json.dump(new_schedule, file, indent=4)

        # Get a fresh copy of data from file ()
        fresh_data = {}
        with open(task_data_file, 'r') as json_file: #TODO: #3 This function should take an optional passed dict for printing if it is not going to use the global data.
            fresh_data = json.load(json_file)
        data_copy = copy.deepcopy(fresh_data)

        # actually add the due tasks
        added_tasks = 0
        tasks_keys = index_data(data_copy)
        if len(tasks_keys) == 0:
            next_key = 1
        else:
            next_key = max(tasks_index) + 1
        
        for key, task in tasks_to_add.items():
            desc = task['task_description']
            found_priority = check_for_priority(desc[-3:])
            if found_priority[0]:
                desc = desc[:-3].strip()
            new_task = format_new_task(next_key, desc, found_priority[1], False)
            data_copy.update(new_task)
            added_tasks += 1
            next_key += 1
        update_tasks(data_copy)
        return added_tasks
    return 0


def render_tasks(prolog: str="") -> None:
    """Print the tasks in all their glory"""

    # check for and add scheduled tasks
    num_scheduled_tasks =  add_scheduled_tasks()
    if num_scheduled_tasks > 0:
        prolog = f"{prolog}\n{num_scheduled_tasks} scheduled tasks added."

    # Get a fresh copy of data from file ()
    fresh_data = {}
    with open(task_data_file, 'r') as json_file: #TODO: #3 This function should take an optional passed dict for printing if it is not going to use the global data.
        fresh_data = json.load(json_file)
    data_copy = copy.deepcopy(fresh_data)

    # Count up the tasks and their status
    done, working, pending = 0, 0, 0
    for key, task in fresh_data.items():
        status = task['status']
        if status in [0, 2]:
            pending += 1
        elif status in [1]:
            working += 1
        elif status in [3]:
            done += 1
        elif status in [4]:
            data_copy.pop(key)
    total = done + working + pending

    # Calculate percent complete
    if total == 0:
        rate = 100
    else:
        rate = int((done / total) * 100)
    
    # Calculate the width of printout (length of longest description and a buffer)
    buffer = 20
    desc_lens = []
    for task in data_copy.values():
        desc_lens.append(len(task['desc']))
    if len(desc_lens) == 0:
        width = buffer
    else:
        width = max(desc_lens) + buffer

    # Format and prep line elements for printout
    boarder = [color(boarderColor) + "┍" + ("━"*width),
                " " + (color(boarderColor) + "─"*width) + "┚"]
    title = f"{color(boarderColor)}│{Style.RESET_ALL}  Tasky {color(boarderColor)}[{done}/{total}]"
    complete_stat = f"{color_gradient(rate)}{str(rate).rjust(3)}%{color(boarderColor)} of all tasks complete.{Style.RESET_ALL}"
    breakdown_stat = f"{color(completeTaskColor)}{str(done).rjust(3)}{color(boarderColor)} done · {color(startedTaskColor)}{working}{color(boarderColor)} in-progress · {color(stoppedTaskColor)}{pending}{color(boarderColor)} pending"
    
    def get_task_lines():
        """Prints a formatted line for each task"""
        for key, task in data_copy.items():
            if task['priority'] not in PRIORITIES:
                task['priority'] = 0
            if task['flag']:
                if task['status'] == 3:
                    flag = f"{color(boarderColor)}{flagSymbolAlt}{Style.RESET_ALL}"
                else:
                    flag = f"{color(priority_color[0],alternate_style=True)}{flagSymbol}{Style.RESET_ALL}"
            else:
                flag = "  "
            id = f"{flag}{color(boarderColor) + key.rjust(3) + '. ' + Style.RESET_ALL}"
            if task['status'] == 0:
                symbol = color(newTaskColor) + newTaskSymbol + Style.RESET_ALL + "  "
            elif task['status'] == 1:
                symbol = color(startedTaskColor) + startedTaskSymbol + Style.RESET_ALL + "  "
            elif task['status'] == 2:
                symbol = color(stoppedTaskColor) + stoppedTaskSymbol + Style.RESET_ALL + "  "
            elif task['status'] == 3:
                symbol = color(completeTaskColor) + completeTaskSymbol + Style.RESET_ALL + "  "
            
            if task['status'] == 3:
                desc = color(boarderColor) + task['desc'] + " " + priority_symbol[task['priority']] + Style.RESET_ALL + " "
            else:
                desc = color(priority_color[task['priority']], task['flag']) + task['desc'] + " " + priority_symbol[task['priority']] + Style.RESET_ALL + " "
            
            if task['status'] in [3]:
                start_date = datetime.datetime.strptime(task['created'], "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(task['switched'], "%Y-%m-%d").date()
            else:
                start_date = datetime.datetime.strptime(task['created'], "%Y-%m-%d").date()
                end_date = datetime.datetime.now().date()
            delta = end_date - start_date
            days = f"{color(boarderColor)}{str(delta.days)}d{Style.RESET_ALL}"
            
            print(id + symbol + desc + days)

    print() # print a blank line to help breakup the clutter
    if config_errors:
        print(f"{len(config_errors)} config(s) missing. try 'ts --configs' for details")
    if prolog != "":
        print(f"{prolog}")
    print(boarder[0])
    print(title)
    get_task_lines()
    print(boarder[1])
    print(complete_stat)
    print(breakdown_stat)


def switch_task_status(task_keys):
    updates = 0
    for task_key in task_keys:
        working_task = data[task_key]
        new_status = None
        if working_task['status'] in [0, 2]:
            new_status = 1
        elif working_task['status'] in [1]:
            new_status = 2
        if new_status is not None:
            working_task['status'] = new_status
            working_task['switched'] = str(datetime.datetime.now().date())
            data[task_key] = working_task
            updates += 1
    if updates > 0:
        update_tasks()
        render_tasks(f"{updates} task{'' if updates == 1 else 's'} updated.")


def mark_tasks_complete(task_keys):
    updates = 0
    for task_key in task_keys:
        working_task = data[task_key]
        new_status = None
        if working_task['status'] in [0, 1, 2]:
            new_status = 3
        elif working_task['status'] in [3]:
            new_status = 1
        if new_status is not None:
            working_task['status'] = new_status
            working_task['switched'] = str(datetime.datetime.now().date())
            data[task_key] = working_task
            updates += 1
    if updates > 0:
        update_tasks()
        render_tasks(f"{updates} task{'' if updates == 1 else 's'} updated.")


def mark_tasks_deleted(task_keys):
    updates = 0
    for task_key in task_keys:
        working_task = data[task_key]
        new_status = None
        if working_task['status'] != 4:
            new_status = 4
        if new_status is not None:
            working_task['status'] = new_status
            working_task['switched'] = str(datetime.datetime.now().date())
            data[task_key] = working_task
            updates += 1
    if updates > 0:
        update_tasks()
        render_tasks(f"{updates} task{'' if updates == 1 else 's'} marked for deletion.")


def clean_task_list(task_keys, old_data):
    updates = 0
    for key in task_keys:
        if old_data[key]['status'] in [3, 4]:
            old_data.pop(key)
            updates += 1
    new_data = {}
    for index, task in enumerate(old_data.values()):
        new_data[str(index + 1)] = task
    if updates > 0:
        update_tasks(new_data)
        render_tasks("Tasks cleaned.")
    else:
        print("Nothing to clean.")


def change_task_priority(task_id, new_priority):
    updates = 0
    if new_priority in PRIORITIES:
        if data[str(task_id)]['priority'] != new_priority:
            data[str(task_id)]['priority'] = new_priority
            updates += 1
        if updates > 0:
            update_tasks()
            render_tasks(f"Task #{task_id} set to priority level {new_priority}.")
    else:
        print(f"{new_priority} is not an available priority level.")


def flag_tasks(task_keys):
    updates = 0
    for task_key in task_keys:
        try:
            working_task = data[task_key]
            working_task['flag'] = not working_task['flag']
            updates += 1
        except:
            print(f"'{task_key}' is an invalid task id.")
    if updates > 0:
        update_tasks()
        render_tasks(f"{updates} task{'' if updates == 1 else 's'} updated.")


def edit_task(task_key):
    if task_key in data:
        new_desc = input(f"Enter new task description for #{task_key}...\n>>> ").strip()
        data[task_key]['desc'] = new_desc
        update_tasks()
        render_tasks(f"Task #{task_key} has been edited.")
    else:
        print(f"'{task_key}' is an invalid task id.")


def check_configs(reset_keyword: str=""):
    if reset_keyword == "reset":
        repair_configs(warn=True)
    elif config_errors:
        print('Missing configurations:')
        for error in config_errors:
            print(f"\t{error}")
        print("\nUse 'ts --configs reset' to reset the config file")
    else:
        print("No config errors found.")


def repair_configs(warn: bool=True):
    if warn:
        user = input("Overwrite configuration file with defaults? [y/N] > ").lower()
        if user == "y":
            with open(config_file, 'w', encoding='utf-8') as settingsFile:
                settingsFile.write(defaults.default_configs)
            print(f"{config_file} reset.")



#endregion
#region: MAIN



tasks_index = index_data(data)

if len(tasks_index) == 0:
    next_index = 1
else:
    next_index = max(tasks_index) + 1

def tasky(argv=None):
    args = parser.parse_args(argv) #Execute parse_args()

    passed_string = (" ".join(args.text)).strip()
    passed_priority = check_for_priority(passed_string[-3:])

    if passed_priority[0]:
        passed_string = passed_string[:-3].strip()


    # --task
    if args.task:    
        new_task = format_new_task(next_index, passed_string, passed_priority[1], False)
        add_new_task(new_task)
        update_tasks()
        render_tasks("New task added.")
    
    # --later
    elif args.later:
        date = args.later[0]
        schedule_task(date)
        render_tasks("Task scheduled.")

    # --switch
    elif args.switch:
        keys = [str(i) for i in args.switch]
        switch_task_status(keys)

    # --complete
    elif args.complete:
        keys = [str(i) for i in args.complete]
        mark_tasks_complete(keys)


    # --delete
    elif args.delete:
        keys = [str(i) for i in args.delete]
        mark_tasks_deleted(keys)


    # --clean
    elif args.clean:
        keys = [str(i) for i in tasks_index]
        clean_task_list(keys, data)


    # --priority
    elif args.priority:
        T, P = args.priority
        change_task_priority(T, P)


    # --flag
    elif args.flag:
        keys = [str(i) for i in args.flag]
        flag_tasks(keys)
    

    # --peek
    elif args.peek:
        preview_schedule()


    # --edit
    elif args.edit:
        key = str(args.edit[0])
        edit_task(key)
    

    # --configs
    elif args.configs:
        check_configs(passed_string.lower())


    # no args
    else:
        render_tasks()
    



