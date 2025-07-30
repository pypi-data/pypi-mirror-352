from lxml import objectify
from base64 import b64encode

from ..namespaces import *

def generate_120_request():
    root = objectify.fromstring('''<HI1Message xmlns="http://uri.etsi.org/03120/common/2019/10/Core" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:common="http://uri.etsi.org/03120/common/2016/02/Common" xmlns:task="http://uri.etsi.org/03120/common/2020/09/Task" xmlns:auth="http://uri.etsi.org/03120/common/2020/09/Authorisation" xmlns:ph="http://uri.etsi.org/03120/common/2025/02/EPOCPlaceholder">
    <Header>
        <SenderIdentifier>
            <CountryCode>XX</CountryCode>
            <UniqueIdentifier>UNKNOWN</UniqueIdentifier>
        </SenderIdentifier>
        <ReceiverIdentifier>
            <CountryCode>XX</CountryCode>
            <UniqueIdentifier>UNKNOWN</UniqueIdentifier>
        </ReceiverIdentifier>
        <TransactionIdentifier></TransactionIdentifier>
        <Timestamp></Timestamp>
        <Version>
            <ETSIVersion>V1.20.1</ETSIVersion>
            <NationalProfileOwner>EU</NationalProfileOwner>
            <NationalProfileVersion>v1.1.1</NationalProfileVersion>
        </Version>
    </Header>
    <Payload>
        <RequestPayload>
            <ActionRequests/>
        </RequestPayload>
    </Payload>
</HI1Message>
''', parser=None)
    return root


def generate_CREATE_Action(new_object, hi1):
    index = len(list(hi1.Payload.RequestPayload.ActionRequests.getchildren()))
    root = objectify.fromstring(f'''<ActionRequest>
    <ActionIdentifier>{index}</ActionIdentifier>
    <CREATE>
    </CREATE>
</ActionRequest>
''', parser=None)
    root.CREATE.append(new_object)
    hi1.Payload.RequestPayload.ActionRequests.append(root)
    return root

def generate_UPDATE_Action(new_object, hi1):
    index = len(list(hi1.Payload.RequestPayload.ActionRequests.getchildren()))
    root = objectify.fromstring(f'''<ActionRequest>
    <ActionIdentifier>{index}</ActionIdentifier>
    <UPDATE>
    </UPDATE>
</ActionRequest>
''', parser=None)
    root.UPDATE.append(new_object)
    hi1.Payload.RequestPayload.ActionRequests.append(root)
    return root    


def generate_HI1Object(object_id: str, country_code: str, owner_id: str,associated_object: str | None = None,  concrete_type: str | None = None):
    root = objectify.fromstring(f'''<HI1Object xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <ObjectIdentifier>{object_id}</ObjectIdentifier>
    <CountryCode>{country_code}</CountryCode>
    <OwnerIdentifier>{owner_id}</OwnerIdentifier>
</HI1Object>''', parser=None)
    # HACK for some reason xsi:type disappears if we specify it as an attribute here
    # Instead, we call it xsi:my_type, which doesn't disappear (for some reason)
    # Then we do a string replacement later
    # No idea why this is. Come back to it later.
    if concrete_type is not None:
        root.set(f"{{{XSI_NS}}}my_type", concrete_type)
    if associated_object is not None:
        root.append(objectify.fromstring(f"<AssociatedObjects><AssociatedObject>{associated_object}</AssociatedObject></AssociatedObjects>", parser=None))
    return root

def generate_AuthorisationObject(object_id: str, country_code: str, owner_id: str, associated_object = None):
    return generate_HI1Object(object_id, country_code, owner_id, associated_object, "auth:AuthorisationObject")

def generate_LDTaskObject(object_id: str, country_code: str, owner_id: str, associated_object = None):
    return generate_HI1Object(object_id, country_code, owner_id, associated_object, "task:LDTaskObject")

def generate_LPTaskObject(object_id: str, country_code: str, owner_id: str, associated_object = None):
    return generate_HI1Object(object_id, country_code, owner_id, associated_object, "task:LPTaskObject")

def generate_DocumentObject(object_id: str, country_code: str, owner_id: str, associated_object: str):
    return generate_HI1Object(object_id, country_code, owner_id, associated_object, "doc:DocumentObject")

def generate_NotificationObject(object_id: str, country_code: str, owner_id: str, associated_object: str):
    return generate_HI1Object(object_id, country_code, owner_id, associated_object, "notify:NotificationObject")

def generate_PlaceholderObject(object_id: str, country_code: str, owner_id: str, associated_object: str):
    return generate_HI1Object(object_id, country_code, owner_id, associated_object, "ph:EPOCPlaceholderObject")



def generate_Form_Document(object_id: str, country_code: str, owner_id: str, associated_object: str, doc_name: str, doc_type: str):
    doc = generate_DocumentObject(object_id, country_code, owner_id, associated_object)
    add_child(doc, "DocumentName", doc_name, ns=DOC_NS)
    add_dict_child(doc, "DocumentType", "ETSI", "EPOCDocumentType", doc_type, ns=DOC_NS)
    body = add_child(doc, "DocumentBody", ns=DOC_NS)
    contents_b64 = b64encode(doc_name.encode("utf-8"))
    body.Contents = contents_b64
    body.ContentType = "text/plain"
    # TODO - come back and put a checksum in here if we want it
    return doc


def add_child(tree, tag_name, value = None, ns = None):
    if value is None:
        return add_cmplx_child(tree, tag_name, ns)
    M = objectify.ElementMaker(namespace=ns)
    new_element = M(tag_name, value)
    tree.append(new_element)
    return new_element

def add_cmplx_child(tree, tag_name, ns = None):
    new_element = objectify.SubElement(tree, (f"{{{ns}}}" if ns is not None else "") + tag_name)
    return new_element

def add_dict_child(tree, tag_name, dict_owner, dict_name, dict_value, ns = None):
    new_field = add_child(tree, tag_name, ns = ns)
    insert_DictionaryEntry(new_field, dict_owner, dict_name, dict_value)
    return new_field

def map_child(out_tree, tag_name, in_tree, xpath, ns = None, translation_func = None, process_func = None):
    in_element = in_tree.find(xpath)
    if in_element is not None:
        if process_func is not None:
            value = process_func(in_element)
        else:
            value = in_element.text
            if translation_func is not None:
                value = translation_func(value)
        return add_child(out_tree, tag_name, value = value, ns=ns)
    return None

def insert_DictionaryEntry(parent, owner: str, name: str, value: str):
    maker = objectify.ElementMaker(namespace=COMMON_NS, nsmap=ns_map)
    parent.append(maker.Owner(owner))
    parent.append(maker.Name(name))
    parent.append(maker.Value(value))

def insert_Flag(parent, flag_tag:str, owner: str, name: str, value: str):
    newFlag = objectify.Element(flag_tag, attrib=None, nsmap=None)
    insert_DictionaryEntry(newFlag, owner, name, value)
    parent.append(newFlag)

def flatten_children(tree):
    return "\n".join([str(c.text) for c in tree.getchildren()])