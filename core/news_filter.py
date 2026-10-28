import datetime

# High-impact news dates / days generator and checker
class MacroNewsFilter:
    """
    Filters trades occurring on or around high-impact macroeconomic announcements:
    - Non-Farm Payrolls (NFP): First Friday of each month.
    - Consumer Price Index (CPI): Monthly release around 10th-14th.
    - FOMC Interest Rate Decisions: 8 Wednesdays per year (approx every 6 weeks).
    - Advance GDP: Late January, April, July, October.
    """
    
    @staticmethod
    def is_first_friday(dt: datetime.datetime) -> bool:
        """Returns True if dt is the first Friday of the month (NFP day)."""
        return dt.weekday() == 4 and 1 <= dt.day <= 7

    @staticmethod
    def is_cpi_window(dt: datetime.datetime) -> bool:
        """Returns True if dt is within typical CPI release window (10th-14th of month, weekdays)."""
        return 10 <= dt.day <= 14 and dt.weekday() in (1, 2, 3, 4)

    @staticmethod
    def is_fomc_window(dt: datetime.datetime) -> bool:
        """Returns True if dt is a typical FOMC Wednesday (mid-cycle, 8x per year)."""
        # FOMC is typically late January, mid-March, early May, mid-June, late July, mid-September, early November, mid-December
        if dt.weekday() == 2:  # Wednesday
            fomc_ranges = [
                (1, 24, 31),  # late Jan
                (3, 14, 22),  # mid March
                (5, 1, 7),    # early May
                (6, 10, 18),  # mid June
                (7, 24, 31),  # late July
                (9, 14, 22),  # mid Sept
                (11, 1, 8),   # early Nov
                (12, 10, 18)  # mid Dec
            ]
            for m, start_d, end_d in fomc_ranges:
                if dt.month == m and start_d <= dt.day <= end_d:
                    return True
        return False

    @staticmethod
    def is_advance_gdp_window(dt: datetime.datetime) -> bool:
        """Returns True if dt is within Advance GDP quarterly release window (late Jan, Apr, Jul, Oct)."""
        if dt.month in (1, 4, 7, 10) and dt.day >= 25 and dt.weekday() in (2, 3, 4):
            return True
        return False

    @classmethod
    def should_skip(cls, dt: datetime.datetime) -> tuple[bool, str]:
        """
        Determines whether the trade should be skipped due to major economic news.
        Returns: (should_skip, reason)
        """
        if cls.is_first_friday(dt):
            return True, "Non-Farm Payrolls (NFP) Release Day"
        if cls.is_fomc_window(dt):
            return True, "FOMC Rate Decision Day"
        if cls.is_cpi_window(dt) and dt.weekday() == 2:  # typically mid-week CPI
            return True, "Consumer Price Index (CPI) Release Window"
        if cls.is_advance_gdp_window(dt):
            return True, "Advance GDP Release Window"
        return False, "Clear (No High-Impact News)"
