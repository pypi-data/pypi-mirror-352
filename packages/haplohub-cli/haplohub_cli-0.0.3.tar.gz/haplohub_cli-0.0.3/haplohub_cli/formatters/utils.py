from datetime import datetime

import pendulum


def format_date(date: datetime) -> str:
    return pendulum.instance(date).to_day_datetime_string()


def truncate(text: str, length: int) -> str:
    if len(text) <= length:
        return text
    return text[:length] + "..."
