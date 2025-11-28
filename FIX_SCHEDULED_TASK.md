# Fix PythonAnywhere Scheduled Task

## Problem
Your scheduled task is failing because it's looking for `manage.py` in the wrong directory.

**Error**: `python: can't open file '/home/horridhunk254/manage.py': [Errno 2] No such file or directory`

**Reason**: The task is running from `/home/horridhunk254/` but your project is in `/home/horridhunk254/carmannagement/`

## Solution

### Step 1: Go to PythonAnywhere Schedule Tab
1. Log in to PythonAnywhere
2. Click on the **Tasks** tab
3. Find your scheduled task

### Step 2: Update the Command

**Current (Wrong) Command:**
```bash
python manage.py create_time_slots
```
or
```bash
python manage.py create_timeslots
```

**Correct Command (Option 1 - Change Directory First):**
```bash
cd /home/horridhunk254/carmannagement && python manage.py create_time_slots
```

**Correct Command (Option 2 - Use Full Path):**
```bash
python /home/horridhunk254/carmannagement/manage.py create_time_slots
```

**Correct Command (Option 3 - Use ~ shortcut):**
```bash
cd ~/carmannagement && python manage.py create_time_slots
```

### Step 3: Set the Correct Working Directory

If PythonAnywhere allows setting a working directory for scheduled tasks:
- **Working Directory**: `/home/horridhunk254/carmannagement`
- **Command**: `python manage.py create_time_slots`

## Recommended Setup

### For Daily Time Slot Creation:

**Command:**
```bash
cd ~/carmannagement && python manage.py create_time_slots
```

**Frequency:** Daily at 12:00 AM (00:00)

**Description:** Creates time slots for appointments

## Verify It Works

After updating the scheduled task:

1. **Test it manually** in a Bash console:
```bash
cd ~/carmannagement
python manage.py create_time_slots
```

2. **Check the output**:
```
Successfully created X time slots. Skipped Y existing slots.
```

3. **Wait for the next scheduled run** and check the task log

## Current Status

Based on your logs:
- ✅ **2025-11-26**: Task succeeded - "Successfully created 10 time slots. Skipped 890 existing slots."
- ❌ **2025-11-25**: Task failed - Wrong directory

It looks like you may have already fixed it! The November 26th run was successful.

## Additional Tips

### Check Task Logs
- Go to **Tasks** tab on PythonAnywhere
- Click on the task to see detailed logs
- Look for error messages or success confirmations

### Test Before Scheduling
Always test management commands manually first:
```bash
cd ~/carmannagement
python manage.py create_time_slots --help
python manage.py create_time_slots
```

### Common Scheduled Tasks for Your System

1. **Create Time Slots** (Daily):
```bash
cd ~/carmannagement && python manage.py create_time_slots
```

2. **Clean Up Old Appointments** (Weekly):
```bash
cd ~/carmannagement && python manage.py cleanup_old_appointments
```

3. **Send Reminder Emails** (Daily):
```bash
cd ~/carmannagement && python manage.py send_appointment_reminders
```

## Troubleshooting

### If Task Still Fails:

1. **Check Python version**:
```bash
which python
python --version
```

2. **Use python3 explicitly**:
```bash
cd ~/carmannagement && python3 manage.py create_time_slots
```

3. **Check file permissions**:
```bash
ls -la ~/carmannagement/manage.py
```

4. **Verify virtual environment** (if using one):
```bash
cd ~/carmannagement && source venv/bin/activate && python manage.py create_time_slots
```

### Check Error Logs

If the task fails, check:
```bash
tail -f /var/www/horridhunk254_pythonanywhere_com_error.log
```

## Summary

✅ **Correct Command Format:**
```bash
cd ~/carmannagement && python manage.py create_time_slots
```

❌ **Wrong Command Format:**
```bash
python manage.py create_time_slots
```

The key is to **change to the project directory first** or **use the full path** to manage.py.
