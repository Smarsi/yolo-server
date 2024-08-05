import datetime


def get_current_time():
    return (datetime.datetime.now()).strftime("%H:%M:%S.%f")


def get_current_datetime():
    return datetime.datetime.now()


def get_current_date():
    return datetime.date.today()


def calc_timelapse(initial, final):
    init_time = datetime.datetime.strptime(initial, "%H:%M:%S.%f")
    end_time = datetime.datetime.strptime(final, "%H:%M:%S.%f")
    return str(end_time - init_time)
