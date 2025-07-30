import logging
from uuid import uuid4
from datetime import datetime, timedelta

from .mappings import *

from ..hi1.generators import *
from ..hi1.helpers import *
from ..xml import xml


# ----------------------------------------------------------
# Authorisation object - clause 5.7.3
# ----------------------------------------------------------
def add_auth_object(hi1, input_xml, global_case_id, form_id):
    ia_technical_id = input_xml.findall(f".//{{{EPOC_NS}}}Addressee//{{{EIO_NS}}}AuthorityTechnicalIdentifier")[0]
    authObj = generate_AuthorisationObject(form_id, ia_technical_id.Country, ia_technical_id.NationalId)
    generate_CREATE_Action(authObj, hi1)

    # TODO - set authObject associated objects from Section D

    add_child(authObj, "AuthorisationReference", global_case_id, ns = AUTH_NS)
    add_dict_child(authObj, "AuthorisationLegalType", "ETSI", "EPOCLegalType", "EPOCPR", ns=AUTH_NS)
    add_dict_child(authObj, "AuthorisationDesiredStatus", "ETSI", "AuthorisationDesiredSatus", "SubmittedToCSP", ns=AUTH_NS)

    sp_concerned = input_xml.findall(f".//{{{EPOC_NS}}}Addressee//{{{EPOC_NS}}}ServiceProviderConcerned/{{{EPOC_NS}}}TechnicalIdentifier")
    if len(sp_concerned) > 0:
        sp_concerned = sp_concerned[0]
        auth_cspid = add_child(authObj, "AuthorisationCSPID", ns=AUTH_NS)
        auth_cspid = add_child(auth_cspid, "CSPID", ns=AUTH_NS)
        add_child(auth_cspid, "CountryCode", sp_concerned[f"{{{EIO_NS}}}Country"].text, ns=CORE_NS)
        add_child(auth_cspid, "UniqueIdentifier", sp_concerned[f"{{{EIO_NS}}}NationalId"].text, ns=CORE_NS)

    fill_in_approval_details(authObj, input_xml, is_validating_auth=False)
    if input_xml.find(f".//{{{FORM2_NS}}}SectionG") is not None:
        fill_in_approval_details(authObj, input_xml, is_validating_auth=True)

    flags = add_child(authObj, "AuthorisationFlags", ns=AUTH_NS)
    emergency_flag = input_xml.find(f".//{{{FORM2_NS}}}SectionB/{{{EPOC_NS}}}EmergencyCase")
    if emergency_flag is not None and emergency_flag.text.lower() == "true":
        add_dict_child(flags, "AuthorisationFlag", "ETSI", "AuthorisationFlag", "IsEmergency", ns=AUTH_NS)

    map_child(authObj, "AuthorisationLegalEntity", input_xml, f".//{{{FORM2_NS}}}SectionB/{{{EPOC_NS}}}Addressee/{{{EPOC_NS}}}Authority/{{{EIO_NS}}}NameOfAuthority", ns=AUTH_NS)
    return authObj

# Mapping as described in table 5.3.3.5 (issuing) table 5.3.3-8 (validating)
def fill_in_approval_details(parent, tree, is_validating_auth):
    approval_details = add_child(parent, "AuthorisationApprovalDetails", ns=AUTH_NS)

    if is_validating_auth:
        input_section = tree.find(f".//{{{FORM2_NS}}}SectionG/{{{EPOC_NS}}}Details")
    else:
        input_section = tree.find(f".//{{{EPOC_NS}}}IssuingAndContactAuthority/{{{EPOC_NS}}}IssuingAuthority")

    add_child(approval_details, "ApprovalType", "ValidatingAuthority" if is_validating_auth else "IssuingAuthority", ns=COMMON_NS)
    map_child(approval_details, "ApprovalReference", input_section, f"{{{EIO_NS}}}FileReference", ns=COMMON_NS)

    fill_in_approver_details(approval_details, tree, input_section, is_validating_auth)


# Mapping as described in table 5.3.3-5 (issuing) and 5.3.3-8 (validating)
def fill_in_approver_details(parent, tree, input_section, is_validating_auth):
    approver_details = add_child(parent, "ApproverDetails", ns=COMMON_NS)

    # TODO - check whether this can actually be absent (we have it as mandatory)
    map_child(approver_details, "ApproverName", input_section, f"{{{EIO_NS}}}NameOfAuthority", ns=COMMON_NS)    
    # TODO - check whether this can actually be absent (we have it as mandatory)
    approver_role = map_child(approver_details, 
                              "ApproverRole", 
                              tree, 
                              f".//{{{FORM2_NS}}}SectionG/{{{EPOC_NS}}}Type" if is_validating_auth else f".//{{{FORM2_NS}}}SectionF/{{{EPOC_NS}}}Type", 
                              ns=COMMON_NS, 
                              translation_func = lambda v: ROLE_MAPPING[v])
    
    fill_in_approver_contact_details(approver_details, tree, is_alternate_poc=False, is_validating_auth=is_validating_auth)
    if not is_validating_auth:
        if input_section.find(f"../{{{EPOC_NS}}}ContactAuthority") is not None:
            fill_in_approver_contact_details(approver_details, tree, is_alternate_poc=True, is_validating_auth=False)


# Mapping as described in 5.3.3.7
def fill_in_approver_contact_details(parent, tree, is_validating_auth, is_alternate_poc):
    contact_details = add_child(parent, "ApproverContactDetails", ns=COMMON_NS)

    if is_validating_auth:
        input_section = tree.find(f".//{{{EPOC_NS}}}IssuingAndContactAuthority/{{{EPOC_NS}}}IssuingAuthority")
    elif is_alternate_poc:
        input_section = tree.find(f".//{{{EPOC_NS}}}IssuingAndContactAuthority/{{{EPOC_NS}}}ContactAuthority/{{{EPOC_NS}}}Authority")
    else:
        input_section = tree.find(f".//{{{FORM2_NS}}}SectionG/{{{EPOC_NS}}}Details")

    if is_alternate_poc:
        map_child(contact_details, "Name", input_section, f"{{{EIO_NS}}}NameOfAuthority", ns=COMMON_NS)    
        add_child(contact_details, "Role", "Point of Contact", ns=COMMON_NS)
    else:
        map_child(contact_details, "Name", input_section, f"{{{EIO_NS}}}NameOfRepresentative", ns=COMMON_NS)    
        map_child(contact_details, "Role", input_section, f"{{{EIO_NS}}}PostHeld", ns=COMMON_NS)    
    map_child(contact_details, "EmailAddress", input_section, f"{{{EIO_NS}}}Email", ns=COMMON_NS)    
    map_child(contact_details, "PhoneNumber", input_section, f"{{{EIO_NS}}}TelNo", ns=COMMON_NS, translation_func=etisfy_tel_no)    
    map_child(contact_details, "FaxNumber", input_section, f"{{{EIO_NS}}}FaxNo", ns=COMMON_NS, translation_func=etisfy_tel_no)    
    map_child(contact_details, "Address", input_section, f"{{{EIO_NS}}}Address", ns=COMMON_NS, process_func=flatten_children)    
    if is_alternate_poc:
        return
    
    # TODO - make this translation complete
    languages = input_section.find(f".//{{{EIO_NS}}}LanguagesToCommunicate")
    if languages is not None:
        for language in languages.getchildren():
            if len(language.text) > 2:
                iso_id = LANGUAGE_MAPPING[language.text]
            else:
                iso_id = language.text
            add_child(contact_details, "Languages", ns=COMMON_NS).ISO639Set1LanguageIdentifier = iso_id

# Clause 5.4.2 and table 5.3.4-1
def add_lp_task_object(hi1, input_xml, identifier, auth_obj_id):
    ia_technical_id = input_xml.findall(f".//{{{EPOC_NS}}}Addressee//{{{EIO_NS}}}AuthorityTechnicalIdentifier")[0]
    taskObj = generate_LPTaskObject(uuid_for_task(auth_obj_id, identifier.Identifier.Id.text), ia_technical_id.Country, ia_technical_id.NationalId, auth_obj_id)
    generate_CREATE_Action(taskObj, hi1)

    add_dict_child(taskObj, "DesiredStatus", "ETSI", "LDTaskDesiredStatus", "AwaitingPreservation", ns=TASK_NS)
    fill_in_request_details(taskObj, input_xml, identifier)
    
    # TODO - this is unlikely to be the correct way to work out the expiration time. Check.
    add_child(taskObj, "DesiredPreservationExpiration", etsify_datetime(datetime.now() + timedelta(days=60), microseconds=False), ns=TASK_NS)
    return taskObj    


def fill_in_request_details(taskObj, input_xml, identifier):
    request_details = add_child(taskObj, "RequestDetails", ns=TASK_NS)

    subscriber_data = identifier.DataCategories.find(f"{{{EPOC_NS}}}Subscriber")
    user_data = identifier.DataCategories.find(f"{{{EPOC_NS}}}UserIdentification")
    traffic_data = identifier.DataCategories.find(f"{{{EPOC_NS}}}Traffic")
    content_data = identifier.DataCategories.find(f"{{{EPOC_NS}}}Content")
    
    if subscriber_data is not None and user_data is not None:
        add_dict_child(request_details, "Type", "ETSI", "SubscriberDataAndUserIdentifyingData", "SubscriberData", ns=AUTH_NS)
    elif subscriber_data is not None:
        add_dict_child(request_details, "Type", "ETSI", "RequestType", "SubscriberData", ns=TASK_NS)
    elif user_data is not None:
        add_dict_child(request_details, "Type", "ETSI", "RequestType", "UserIdentifyingData", ns=TASK_NS)
    elif content_data is not None and traffic_data is not None:
        add_dict_child(request_details, "Type", "ETSI", "TrafficDataAndStoredContentData", "SubscriberData", ns=AUTH_NS)
    elif content_data is not None:
        add_dict_child(request_details, "Type", "ETSI", "RequestType", "StoredContentData", ns=TASK_NS)
    elif traffic_data is not None:
        add_dict_child(request_details, "Type", "ETSI", "RequestType", "TrafficData", ns=TASK_NS)

    request_details.StartTime = etsify_datetime(datetime.fromisoformat(identifier.Identifier.DateTimeRange.Start.text))
    request_details.EndTime = etsify_datetime(datetime.fromisoformat(identifier.Identifier.DateTimeRange.End.text))

    # TODO - work out how to get the ObservedTimes if IP details are specified
    fill_in_request_values(request_details, input_xml, identifier)

    category_selections = identifier.DataCategories.find(f".//{{{EPOC_NS}}}Selection")
    # TODO - check wether this is correct per the schema or not.
    # TODO - finish this mapping properly
    sub_types = add_child(request_details, "Subtype", ns=TASK_NS)
    for category in category_selections:
        add_dict_child(sub_types, "RequestSubtype", "ETSI", "EPOCRequestSubtype", category.text, ns=TASK_NS)
    
    # TODO - come back and do TargetIdentifierSubtypes

def fill_in_request_values(request_details, input_xml, identifier):
    request_values = add_child(request_details, "RequestValues", ns=TASK_NS)
    request_value = add_child(request_values, "RequestValue", ns=TASK_NS)

    # TODO - Come back to this as/when we know how SP-provided types are being handles
    format_name = IDENTIFIER_TYPE_MAPPING[identifier.Identifier.Type.text]
    format_value = identifier.Identifier.Value.text
    target_format = add_child(request_value, "FormatType", ns=TASK_NS)
    target_format.FormatOwner = "ETSI"
    target_format.FormatName = format_name
    request_value.Value = format_value

def add_document_object(hi1, input_xml, form_id: str):
    ia_technical_id = input_xml.findall(f".//{{{EPOC_NS}}}Addressee//{{{EIO_NS}}}AuthorityTechnicalIdentifier")[0]
    doc = generate_Form_Document(str(uuid4()), ia_technical_id.Country.text, ia_technical_id.NationalId.text, form_id, "EPOC/EPOC-PR Form", "Form2")
    generate_CREATE_Action(doc, hi1)


def processForm2(input_xml, global_case_id: str, form_id: str):
    hi1 = generate_120_request()

    auth_obj = add_auth_object(hi1, input_xml, global_case_id, form_id)
    auth_obj_id = auth_obj.ObjectIdentifier

    identifiers = input_xml.findall(f".//{{{FORM2_NS}}}SectionC/{{{EPOC_NS}}}Evidence")
    for identifier in identifiers:
        add_lp_task_object(hi1, input_xml, identifier, auth_obj_id)

    add_document_object(hi1, input_xml, form_id)

    return hi1