
```
                                                                                                         
888888888888                    88          ,ad8888ba,   88                                   88         
     88                         88         d8"'    `"8b  88                                   88         
     88                         88        d8'            88                                   88         
     88  ,adPPYYba,  ,adPPYba,  88   ,d8  88             88,dPPYba,    ,adPPYba,   ,adPPYba,  88   ,d8   
     88  ""     `Y8  I8[    ""  88 ,a8"   88             88P'    "8a  a8P_____88  a8"     ""  88 ,a8"    
     88  ,adPPPPP88   `"Y8ba,   8888[     Y8,            88       88  8PP"""""""  8b          8888[      
     88  88,    ,88  aa    ]8I  88`"Yba,   Y8a.    .a8P  88       88  "8b,   ,aa  "8a,   ,aa  88`"Yba,   
     88  `"8bbdP"Y8  `"YbbdP"'  88   `Y8a   `"Y8888Y"'   88       88   `"Ybbd8"'   `"Ybbd8"'  88   `Y8a  
                                                                                                         

```

> _A non-AI automatic scheduler for taskwarrior (i.e. alternative to skedpal / timehero / flowsavvy / reclaim / trevor / motion)_

This is a taskwarrior extension that automatically schedule your tasks based on your working hours,
estimated time, and calendar events, finding an optimal time to work on each task and match all your
deadlines.

## Features

- [x] **Use arbitrarily complex time maps for working hours**
- [x] Block scheduling time using iCal calendars (meetings, vacations, holidays, etc.)
- [x] **Parallel scheduling algorithm for multiple tasks, considering urgency and dependencies**
- [x] Dry-run mode: preview scheduling without modifying your Taskwarrior database
- [x] Custom urgency weighting for scheduling (via CLI or config)
- [x] **Auto-fix scheduling to mach due dates**
- [x] Force update of iCal calendars, bypassing cache
- [x] Simple, customizable reports for planned and unplanned tasks
- [x] Emoji and attribute customization in reports
- [ ] Use Google API to access calendars
- [ ] Export tasks to iCal calendar and API calendars

## Install

1. `pipx install taskcheck`
2. `taskcheck --install`

## How does it work

This extension parses your pending and waiting tasks sorted decreasingly by urgency and tries to schedule them in the future.
It considers their estimated time to schedule all tasks starting from the most urgent one.

#### UDAs

Taskcheck leverages two UDAs, `estimated` and `time_map`. The `estimated` attribute is
the expected time to complete the task in hours. The `time_map` is a comma-separated list of strings
that indicates the hours per day in which you will work on a task (e.g. `work`, `weekend`, etc.).
The exact correspondence between the `time_map` and the hours of the day is defined in the configuration
file of taskcheck. For instance:

```toml
[time_maps]
# get an error)
[time_maps.work]
monday = [[9, 12.30], [14, 17]]
tuesday = [[9, 12.30], [14, 17]]
# ...
```

#### They say it's an "AI"

Taskcheck will also parse online iCal calendars (Google, Apple, etc.) and will match them with your time maps.
It will then modify the Taskwarrior tasks by adding the `completion_date` attribute with the expected
date of completion and the `scheduled` attribute with the date in which the task is expected to
start.

It will also print a red line for every task whose `completion_date` is after its `due_date`.

In general, it is recommended to run taskcheck rather frequently and at least once at the beginning
of your working day.

#### Reports

You can also print simple reports that exploit the `scheduling` UDA filled by Taskcheck to grasp
how much time you have to work on which task in which day. For
instance:

- `taskcheck -r today` will show the tasks planned for today
- `taskcheck -r 1w` will show the tasks planned for the next week

## Configuration

`taskcheck --install` allows you to create required and recommended configurations for
Taskwarrior. It will also generate a default configuration file for taskcheck.

Below is an example of a taskcheck configuration file, with all relevant options:

```toml
[time_maps]
# Define your working hours for each named time map (in 24h format, e.g. 9.5 = 9:30)
[time_maps.work]
monday = [[9, 12.30], [14, 17]]
tuesday = [[9, 12.30], [14, 17]]
wednesday = [[9, 12.30], [14, 17]]
thursday = [[9, 12.30], [14, 17]]
friday = [[9, 12.30], [14, 17]]

[time_maps.weekend]
saturday = [[9, 12.30]]
sunday = [[9, 12.30]]

[scheduler]
days_ahead = 1000         # How far to go with the schedule (lower values = faster computation)
weight_urgency = 1.0      # Default weight for urgency in scheduling (overridable via CLI)
# if weight_urgency is set to 0, only due urgency is considered
# by default, this factor is automatically reduced if some task cannot be scheduled in time,
# leading to tasks with due dates being prioritized (see --no-auto-adjust-urgency)

[calendars]
# iCal calendars can be used to block your time and make the scheduling more precise
[calendars.1]
url = "https://your/url/to/calendar.ics"
expiration = 0.08         # In hours (0.08 hours ≈ 5 minutes)
timezone = "Europe/Rome"  # If set, force timezone for this calendar (see TZ database)

[calendars.holidays]
url = "https://www.officeholidays.com/ics-clean/italy/milan"
event_all_day_is_blocking = true
expiration = 720          # In hours (720 hours = 30 days)

[report]
include_unplanned = true
additional_attributes = ["estimated", "due", "urgency"]           # Extra attributes to show in the report
additional_attributes_unplanned = ["due", "urgency"]               # Extra attributes for unplanned tasks
emoji_keywords = {"meet"=":busts_in_silhouette:", "review"=":mag_right:"} # Map keywords to emoji
```

### Configuration Options

- **[scheduler]**
  - `days_ahead`: How many days ahead to schedule tasks.
  - `weight_urgency`: Default weight for urgency in scheduling (0.0 to 1.0). Can be overridden with `--urgency-weight`.
- **[calendars]**
  - `url`: iCal URL to block time.
  - `expiration`: Cache expiration in hours.
  - `timezone`: (Optional) Force a timezone for this calendar.
  - `event_all_day_is_blocking`: (Optional, bool) Treat all-day events as blocking.
- **[report]**
  - `include_unplanned`: Show unplanned tasks in a separate section.
  - `additional_attributes`: Extra columns to show in the report.
  - `additional_attributes_unplanned`: Extra columns for unplanned tasks.
  - `emoji_keywords`: Map keywords in task descriptions to emoji.

## Algorithm

The algorithm simulates what happens if you work on a task for a certain time on a given day.

For each day X starting from today, it sorts the tasks by decreasing urgency.
It start from the most urgent tasks that can be allocated on day X depending on the task's
`time_map` and on your calendars. It allocates a few number of hours to the task,
then recomputes the urgencies exactly as Taskwarrior would do
if it was running on day X. Having recomputed the urgencies, it restarts.

If after 2 hours a long task has decreased its urgency, it will be noticed and the newer most urgent
task will get scheduled in its place.

For `today`, taskcheck will skip the hours in the past -- i.e. if you're running at 12 pm, it will
skip all the available slots until 12 pm.

The maximum time that is allocated at each attempt is by default 2 hours
(or less if the task is shorter), but you can change it by tuning the Taskwarrior UDA `min_block`.

After the scheduling is done, if any task has a `completion_date` after its `due_date`, the
`weight_urgency` factor is reduced by 0.1 and the scheduling is repeated, until all tasks
are scheduled before their due dates or the `weight_urgency` factor reaches 0.

## Tips and Tricks

- You can exclude a task from being scheduled by removing the `time_map` or `estimated` attributes.
- You can see tasks that you can execute now with the `task ready` report.

## CLI Options

```
-v, --verbose                Increase output verbosity
-i, --install                Install taskcheck configuration
-r, --report CONSTRAINT      Show tasks planned until a certain time (e.g. 'today', '1w', 'eow')
-s, --schedule               Perform the scheduling algorithm and update tasks
-f, --force-update           Force update of all iCal calendars, ignoring cache expiration
    --taskrc PATH            Set custom TASKRC directory (and TASKDATA) for debugging or alternate environments
    --urgency-weight FLOAT   Weight for urgency in scheduling (0.0 to 1.0), overrides config value. When 0, only due urgency is considered.
    --dry-run                Perform scheduling without modifying the Taskwarrior database (useful for testing)
    --no-auto-adjust-urgency Disable auto-adjustment of urgency weight (default: enabled)
```

### Examples

- `taskcheck --schedule`  
  Run the scheduler and update your Taskwarrior tasks.
- `taskcheck --schedule --dry-run`  
  Preview the schedule without modifying your database.
- `taskcheck --schedule --urgency-weight 0.5`  
  Use a custom urgency weighting for this run.
- `taskcheck --schedule --no-auto-adjust-urgency`  
  Avoid the automatically reduction of urgency weight if tasks can't be scheduled before their due dates.
- `taskcheck --report today`  
  Show the schedule for today.
- `taskcheck --report 1w`  
  Show the schedule for the next week.
- `taskcheck --force-update`  
  Force refresh of all iCal calendars, ignoring cache.
