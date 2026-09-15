_WEEKDAYS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
_WEEKDAYS_SHORT = ["lun", "mar", "mie", "jue", "vie", "sab", "dom"]
_MONTHS = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def format_day_long(d):
    return f"{_WEEKDAYS[d.weekday()]} {d.day} de {_MONTHS[d.month - 1]}, {d.year}"


def format_weekday_short(d):
    return f"{_WEEKDAYS_SHORT[d.weekday()]} {d.strftime('%d/%m')}"
