"""Configuration constants for the Price Intelligence Solution"""

# Country selection constants
COUNTRY_LIST = ["US", "UK", "DE", "FR", "IT"]

# Validation constants
REQUIRED_COLUMNS = ['ProductID', 'ItemID', 'ActualPrice', 'PromoPrice', 'StartDate', 'EndDate']

# File size limits (in MB)
LARGE_FILE_THRESHOLD = 10
MEMORY_EFFICIENT_THRESHOLD = 5

# Display limits
DEFAULT_ROW_LIMITS = [10, 25, 50, 100, "All"]
PREVIEW_LIMITS = [5, 10, 20]

# Log settings
MAX_LOG_ENTRIES = 50
