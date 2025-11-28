# PythonAnywhere Scheduled Tasks Guide

## Your Time Slot Management Commands

You have two management commands for creating time slots:

### 1. `create_time_slots` (Recommended)
- Creates 8 time slots per day (8 AM - 5 PM, skipping 12-1 PM lunch)
- Automatically skips Sundays
- Default: 30 days ahead
- Max capacity: 3 appointments per slot

### 2. `create_timeslots` (Alternative)
- Creates hourly slots from 8 AM - 6 PM
- Includes all 7 days of the week
- More flexible with custom intervals
- Default: 30 days ahead

## Current Scheduled Task Status

Based on your logs:
- ✅ **Nov 26, 2025**: Success - "Successfully created 10 time slots. Skipped 890 existing slots."
- ❌ **Nov 25, 2025**: Failed - Wrong directory path

**Good news**: Your task is now working! It created 10 new slots and skipped 890 existing ones.

## Fix the Scheduled Task Path

### On PythonAnywhere Tasks Tab:

**Current (Wrong) Command:**
```bash
python manage.py create_time_slots
```

**Correct Command:**
```bash
cd ~/carmannagement && python manage.py create_time_slots
```

## Recommended Scheduled Task Setup

### Daily Time Slot Creation

**Task Name:** Create Daily Time Slots

**Command:**
```bash
cd ~/carmannagement && python manage.py create_time_slots --days 30
```

**Schedule:** Daily at 12:00 AM (00:00)

**Purpose:** Ensures there are always 30 days of available time slots

**Expected Output:**
```
Successfully created X time slots for the next 30 days
```

## Alternative: Weekly Time Slot Creation

If you don't need daily updates:

**Command:**
```bash
cd ~/carmannagement && python manage.py create_time_slots --days 60
```

**Schedule:** Weekly on Monday at 12:00 AM

**Purpose:** Creates 60 days of slots once per week

## Testing Your Commands

### Test Locally (Windows):
```bash
python manage.py create_time_slots
python manage.py create_time_slots --days 7
python manage.py create_timeslots --days 14 --interval 30
```

### Test on PythonAnywhere:
```bash
cd ~/carmannagement
python manage.py create_time_slots
```

## Understanding the Output

### "Successfully created 10 time slots. Skipped 890 existing slots."

This means:
- ✅ 10 new time slots were created (for new dates)
- ✅ 890 slots already existed (no duplicates created)
- ✅ System is working correctly!

### Why Only 10 New Slots?

If you run daily with `--days 30`:
- Day 1: Creates 30 days of slots (240 slots)
- Day 2: Creates 1 new day (8-10 slots), skips 29 existing days
- Day 3: Creates 1 new day (8-10 slots), skips 29 existing days

This is **correct behavior** - it's maintaining a rolling 30-day window.

## Command Options

### create_time_slots

```bash
# Default: 30 days
python manage.py create_time_slots

# Custom days
python manage.py create_time_slots --days 60

# Help
python manage.py create_time_slots --help
```

**Features:**
- 8 slots per day (8 AM - 5 PM)
- Skips Sundays automatically
- Skips 12-1 PM lunch hour
- 3 appointments per slot

### create_timeslots

```bash
# Default: 30 days, 60-minute slots
python manage.py create_timeslots

# Custom interval (30-minute slots)
python manage.py create_timeslots --days 30 --interval 30

# 2-hour slots
python manage.py create_timeslots --days 30 --interval 120
```

**Features:**
- Flexible time intervals
- 8 AM - 6 PM coverage
- Includes all 7 days
- 3 appointments per slot

## Monitoring Your Scheduled Task

### Check Task Logs on PythonAnywhere:

1. Go to **Tasks** tab
2. Click on your scheduled task
3. View the log output
4. Look for success/error messages

### Check Time Slots in Database:

```bash
cd ~/carmannagement
python manage.py shell
```

```python
from clients.models import TimeSlot
from datetime import date, timedelta

# Count total slots
print(f"Total slots: {TimeSlot.objects.count()}")

# Count future slots
today = date.today()
future_slots = TimeSlot.objects.filter(date__gte=today).count()
print(f"Future slots: {future_slots}")

# Check next 7 days
next_week = today + timedelta(days=7)
week_slots = TimeSlot.objects.filter(date__gte=today, date__lte=next_week).count()
print(f"Next 7 days: {week_slots} slots")

# Check available slots
available = TimeSlot.objects.filter(date__gte=today, is_active=True).count()
print(f"Available slots: {available}")
```

## Troubleshooting

### Task Fails with "No such file or directory"

**Problem:** Wrong working directory

**Solution:**
```bash
cd ~/carmannagement && python manage.py create_time_slots
```

### Task Creates No New Slots

**Problem:** Slots already exist for the date range

**Solution:** This is normal! The command skips existing slots.

To verify:
```bash
cd ~/carmannagement
python manage.py create_time_slots --days 60
```

### Task Takes Too Long (>3 minutes)

**Problem:** Creating too many slots at once

**Solution:** Reduce the days parameter:
```bash
cd ~/carmannagement && python manage.py create_time_slots --days 30
```

### Want to Reset All Time Slots

**Warning:** This deletes all time slots including booked ones!

```bash
cd ~/carmannagement
python manage.py shell
```

```python
from clients.models import TimeSlot
TimeSlot.objects.all().delete()
exit()
```

Then recreate:
```bash
python manage.py create_time_slots --days 30
```

## Best Practices

1. ✅ **Run daily** to maintain rolling availability
2. ✅ **Use 30-60 days** for the days parameter
3. ✅ **Monitor task logs** weekly
4. ✅ **Test commands** before scheduling
5. ✅ **Keep lunch breaks** (12-1 PM) for staff

## Summary

Your scheduled task is **working correctly**! 

**Current Setup:**
- ✅ Command runs daily at 12:00
- ✅ Creates new time slots as needed
- ✅ Skips existing slots (no duplicates)
- ✅ Maintains 30-day rolling window

**Just make sure the command includes the directory change:**
```bash
cd ~/carmannagement && python manage.py create_time_slots
```

If you see "Skipped X existing slots" - that's **good**! It means the system is working and not creating duplicates.
