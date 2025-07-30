from datetime import datetime, date, time
from hashlib import sha256
from uuid import UUID

def etsify_datetime(d: datetime, microseconds = True) -> str:
    if microseconds:
        return str(d.astimezone().isoformat())
    else:
        s = str(d.astimezone().isoformat())
        return s[0:-13] + s[-6:]

def etsify_datetime_from_date(d: date) -> str:
    return etsify_datetime(datetime.combine(d, time(0,0,0)))

# TODO - casting ISO time to date puts it in local timezone
# create a function that can just modify the string

def etisfy_tel_no(s: str) -> str:
    return s.replace("(","")\
            .replace(")","")\
            .replace(" ","")\
            .replace("+","")

def uuid_from_global_case_id (global_case_id: str):
    return str(UUID(bytes = sha256(global_case_id.encode()).digest()[:16], version=4))

def uuid_for_task(auth_form_id: str, id_number: str):
    return str(UUID(bytes = sha256(f"{auth_form_id}-{id_number}".encode()).digest()[:16], version=4))
