from datetime import datetime, timezone


def hex_to_number(hex_str: str) -> int:
    """Convert hexadecimal string to number."""
    return int(hex_str, 16)


def number_to_hex(n: int) -> str:
    """Convert number to hexadecimal string, padded to 2 characters and uppercase."""
    return f"{n:02X}"


def date_to_day_of_year(date: datetime, add_year_prefix: bool = False) -> str:
    """Convert date to day of year string format."""
    # Calculate day of year (1-based)
    day_of_year = date.timetuple().tm_yday
    
    year_prefix = ""
    if add_year_prefix:
        year_prefix = str(date.year)[-1]  # Last digit of year
    
    return f"{year_prefix}{day_of_year:03d}"


def day_of_year_to_date(day_of_year: str, has_year_prefix: bool, reference_year: int = None) -> datetime:
    """Convert day of year string to datetime."""
    current_year = reference_year if reference_year is not None else datetime.now().year
    year = str(current_year)
    days_to_add = day_of_year
    
    if has_year_prefix:
        # Extract year prefix and remaining days
        year = year[:-1] + days_to_add[0]  # Replace last digit with prefix
        days_to_add = days_to_add[1:]
        
        # Handle year wrap-around logic
        if int(year) - current_year > 2:
            year = str(int(year) - 10)
    
    # Create date from year and day of year
    base_date = datetime(int(year), 1, 1, tzinfo=timezone.utc)
    # Add (days_to_add - 1) days since Jan 1 is day 1, not day 0
    from datetime import timedelta
    target_date = base_date + timedelta(days=int(days_to_add) - 1)
    
    return target_date