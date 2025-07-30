from datetime import datetime, timedelta

# Get the current date
current_date = datetime.now()

# Subtract one day
previous_date = current_date - timedelta(days=1)

# Format the date as YYYYMMDD
date_string = previous_date.strftime('%Y%m%d')

print(date_string)