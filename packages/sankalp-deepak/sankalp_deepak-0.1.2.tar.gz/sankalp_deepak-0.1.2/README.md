# Sankalp
A simple cli tool for organizing your daily tasks.

## Requirements
- PostgreSQL Database

## Configurations
- Set environment variables
- `SANKALP_DATABASE_URI`: PostgreSQL connection string
- `SANKALP_REMINDER_POLICY`: Reminder policy for scheduler

### Sample reminder policy

```json
{
  "CRITICAL": [
    "half",
    {"hours": 1},
    {"minutes":  30},
    {"minutes":  10},
    {"minutes":  5},
    {"minutes":  1}
  ],
  "HIGH": [
    "half",
    {"hours": 1},
    {"minutes":  5},
    {"minutes":  1}
  ],
  "MEDIUM": [
    {"hours": 1},
    {"minutes":  5}
  ]
}
```

## Usage
```bash
sankalp --help
```

## Starting the scheduler for reminders
```bash
nohup python -m sankalp.scheduler_manager & 
```