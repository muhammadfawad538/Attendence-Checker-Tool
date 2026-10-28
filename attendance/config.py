# Default thresholds for flag rules.

OVERWORK_HOURS = 11.0       # hours_worked >= this counts as an overwork day
OVERWORK_MIN_DAYS = 3       # need this many overwork days in a window
OVERWORK_WINDOW_DAYS = 7    # rolling window size in days

SHORT_HOURS = 4.0           # hours_worked < this counts as a short day
SHORT_MIN_DAYS = 3          # consecutive short working days needed

LEAVE_PATTERN_MIN_COUNT = 3 # Monday/Friday leaves needed to flag
LEAVE_PATTERN_WEEKS = 8     # lookback window in weeks

# Weekend work
WEEKEND_WORK_ENABLED = True # flag hours worked on Saturday/Sunday