import logging
from uuid import uuid4
from pathlib import Path
from sys import argv
from datetime import datetime, date

from lxml import etree, objectify

from .mappings import *

from ..hi1.generators import *
from ..hi1.helpers import *
from ..xml import xml

def fill_in_status(parent, obj_id, status_dict, status_value, details):
    status = add_child(parent, "AssociatedObjectStatus", ns=NOTIFY_NS)
    status.AssociatedObject = obj_id
    add_dict_child(status, "Status", "ETSI", status_dict, status_value, ns=NOTIFY_NS)
    status.Details = details
    return status

def add_notification_object(hi1, input_xml, notif_id, original_auth_id):
    sp_technical_id = input_xml.findall(f".//{{{FORM3_NS}}}SectionH//{{{EIO_NS}}}AuthorityTechnicalIdentifier")[0]
    notif_obj = generate_NotificationObject(notif_id, sp_technical_id.Country.text, sp_technical_id.NationalId.text, original_auth_id)
    generate_CREATE_Action(notif_obj, hi1)

    add_child(notif_obj, "NotificationDetails", "Notification of Form 3", ns=NOTIFY_NS)
    add_dict_child(notif_obj, "NotificationType", "ETSI", "EPOCNotificationType", "DeFactoImpossibility", ns=NOTIFY_NS)
    add_child(notif_obj, "NewNotification", "true", ns=NOTIFY_NS)
    add_child(notif_obj, "NotificationTimestamp", etsify_datetime(datetime.now(), microseconds=False), ns=NOTIFY_NS)

    statuses = add_child(notif_obj, "StatusOfAssociatedObjects", ns=NOTIFY_NS)

    auth_error_str = "From Form 3 Section E (as an example of what could be done)\n"
    for elem in input_xml.find(f".//{{{FORM3_NS}}}SectionE").getchildren():
        if elem.tag == f"{{{FORM3_NS}}}NatureOfConflictingObligations":
            pass
        else:
            auth_error_str += f"{elem.tag.split("}")[1]}: {elem.text}\n"

    information_required = input_xml.find(f".//{{{FORM3_NS}}}SectionF/{{{FORM3_NS}}}InformationRequiredFromIssuingAuthority")
    if information_required is not None:
        auth_error_str += f"From Section F\nInformationRequiredFromIssuingAuthority: {information_required.text}"
    fill_in_status(statuses, original_auth_id, "AuthorisationStatus", "Invalid", auth_error_str)

    task_map = {}
    for identifier in input_xml.findall(f".//{{{FORM3_NS}}}SectionD/{{{FORM3_NS}}}NonExecutionReason"):
        task_id = uuid_for_task(original_auth_id, identifier.IdentifierId)
        task_error_str = ""
        if hasattr(identifier, "Reasons"):
            for reason in identifier.Reasons.getchildren():
                task_error_str += f"Reason: {reason.text}\n"
        if hasattr(identifier, "ExplanationOrOtherReason"):
            task_error_str += f"ExplanationOrOtherReason:{identifier.ExplanationOrOtherReason}"
        task_map[task_id] = task_error_str
    for identifier in input_xml.findall(f".//{{{FORM3_NS}}}SectionG/{{{FORM3_NS}}}PreservationOfData"):
        task_id = uuid_for_task(original_auth_id, identifier.IdentifierId)
        task_error_str = task_map.get(task_id, "")
        for elem in identifier.getchildren():
            task_error_str += f"{elem.tag.split("}")[1]}: {elem.text}\n"
    
    # TODO - Need to work out whether each task is an LPTask or an LDTask
    for task_id, error_str in task_map.items():
        fill_in_status(statuses, task_id, "LPTaskStatus", "Invalid", error_str)
    return hi1

def add_document_object(hi1, input_xml, form_id: str, parent_form_id):
    sp_technical_id = input_xml.findall(f".//{{{FORM3_NS}}}SectionH//{{{EIO_NS}}}AuthorityTechnicalIdentifier")[0]
    doc = generate_Form_Document(str(uuid4()), sp_technical_id.Country.text, sp_technical_id.NationalId.text, parent_form_id, "EPOC/EPOC-PR Form", "Form3")
    generate_CREATE_Action(doc, hi1)
    
def processForm3(input_xml, global_case_id: str, form_id: str, parent_form_id: str):
    hi1 = generate_120_request()

    add_notification_object(hi1, input_xml, form_id, parent_form_id)
    add_document_object(hi1, input_xml, form_id, parent_form_id)

    return hi1