from datetime import date, timedelta


def get_date_range_tuple(start_date: str, end_date: str):
    _start_date = start_date.split('-')
    _end_date = end_date.split('-')

    start_date = date(int(_start_date[0]), int(_start_date[1]), int(_start_date[2]))
    end_date = date(int(_end_date[0]),int(_end_date[1]), int(_end_date[2]))


    return start_date, end_date