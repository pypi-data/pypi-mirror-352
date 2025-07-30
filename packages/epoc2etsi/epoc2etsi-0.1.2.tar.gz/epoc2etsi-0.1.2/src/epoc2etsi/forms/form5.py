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

def add_lp_task_update(hi1, input_xml, identifier, auth_obj_id):
    ia_technical_id = input_xml.findall(f".//{{{FORM5_NS}}}SectionA//{{{EIO_NS}}}AuthorityTechnicalIdentifier")[0]
    taskObj = generate_LPTaskObject(uuid_for_task(auth_obj_id, identifier), ia_technical_id.Country, ia_technical_id.NationalId, auth_obj_id)
    generate_UPDATE_Action(taskObj, hi1)

    add_dict_child(taskObj, "DesiredStatus", "ETSI", "LDTaskDesiredStatus", "SubsequentProductionRequest", ns=TASK_NS)

    return taskObj    


def add_document_object(hi1, input_xml, form_id: str, parent_form_id):
    sp_technical_id = input_xml.findall(f".//{{{FORM5_NS}}}SectionA//{{{EIO_NS}}}AuthorityTechnicalIdentifier")[0]
    doc = generate_Form_Document(str(uuid4()), sp_technical_id.Country.text, sp_technical_id.NationalId.text, parent_form_id, "EPOC/EPOC-PR Form", "Form5")
    generate_CREATE_Action(doc, hi1)
    
def processForm5(input_xml, global_case_id: str, form_id: str, parent_form_id: str, num_of_identifiers = 1):
    hi1 = generate_120_request()

    # TODO - Form 5 doesn't contain any indication of the identifiers
    # so the RI will need to supply the number of identifiers (in order to generate the
    # object identifiers for the Tasks correctly)
    for i in range(num_of_identifiers):
        add_lp_task_update(hi1, input_xml, i+1, parent_form_id)

    add_document_object(hi1, input_xml, form_id, parent_form_id)

    return hi1