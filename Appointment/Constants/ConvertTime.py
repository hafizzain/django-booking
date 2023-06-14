def convert_24_to_12(time):
    if time == "00:00:00":
        return "12:00:00 AM"
    elif int(time[:2]) == 0:
        return time[3:] + " AM"
    elif int(time[:2]) < 12:
        return time + " AM"
    elif int(time[:2]) == 12:
        return time + " PM"
    else:
        return str(int(time[:2]) - 12) + time[2:] + " PM"