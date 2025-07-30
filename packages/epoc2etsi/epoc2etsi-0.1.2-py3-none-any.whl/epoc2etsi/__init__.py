import logging
from uuid import uuid4
from pathlib import Path
from sys import argv
from datetime import datetime

from lxml import objectify

from .hi1.generators import *
from .hi1.helpers import etsify_datetime
from .xml import xml

from .forms import form1, form2, form3, form5, form6

sender_cc = "XX"
sender_id = "RI_API"
receiver_cc = "XX"
receiver_id = "ServiceProviderID"

def main() -> None:
    if len(argv) < 2:
        logging.error("Please specify an input file")
        exit(-1)

    input_path = Path(argv[1])
    input_obj = objectify.parse(input_path, parser=None)

    input_root = input_obj.getroot()
    global_case_id = input_root.globalCaseId.text
    form_id = input_root.formId
    parent_form_id = input_root.parentFormId if hasattr(input_root, "parentFormId") else None
    form_obj = input_root.form.getchildren()[0]
    ri_to_sp = True

    hi1 = None

    match form_obj.tag.split("}")[1]:
        case "epocForm1" :      hi1 = form1.processForm1(form_obj, global_case_id, form_id)
        case "epocPrForm2" :    hi1 = form2.processForm2(form_obj, global_case_id, form_id)
        case "epocForm3" :      
            hi1 = form3.processForm3(form_obj, global_case_id, form_id, parent_form_id)
            ri_to_sp = False
        case "epocPrForm5" :    hi1 = form5.processForm5(form_obj, global_case_id, form_id, parent_form_id)
        case "epocPrForm6" :    hi1 = form6.processForm6(form_obj, global_case_id, form_id, parent_form_id)
        case _ :
            print (f"No matching form found for {form_obj.tag}")
            exit(-1)
    
    hi1.Header.SenderIdentifier.CountryCode = sender_cc if ri_to_sp else receiver_cc
    hi1.Header.SenderIdentifier.UniqueIdentifier = sender_id if ri_to_sp else receiver_id
    hi1.Header.ReceiverIdentifier.CountryCode = receiver_cc if ri_to_sp else sender_cc
    hi1.Header.ReceiverIdentifier.UniqueIdentifier = receiver_id if ri_to_sp else sender_id
    hi1.Header.Timestamp = etsify_datetime(datetime.now())
    hi1.Header.TransactionIdentifier = str(uuid4())

    print(xml(hi1))
