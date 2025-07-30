from lxml import objectify, etree
from .namespaces import *

def xml(hi1) -> str:
    objectify.deannotate(hi1)
    etree.cleanup_namespaces(hi1, top_nsmap=None, keep_ns_prefixes=[XSI_NS])
    E = objectify.ElementMaker(annotate=False, namespace=CORE_NS, nsmap=ns_map)
    result = E.HI1Message(hi1.Header, hi1.Payload)
    etree.indent(result, space=" ")
    xml_bytes = etree.tostring(result,
                            pretty_print=True, 
                            xml_declaration=True, 
                            encoding="UTF-8"
                            )
    xml_str = xml_bytes.decode("UTF-8")
    # HACK I don't know why lxml makes xsi:type disappear
    xml_str = xml_str.replace("xsi:my_type", "xsi:type")
    return xml_str