XSI_NS      = "http://www.w3.org/2001/XMLSchema-instance"

EPOC_NS     = "http://data.europa.eu/edm/1/ns/epoc"
EIO_NS      = "http://data.europa.eu/edm/1/ns/eio"
FORM1_NS    = "http://data.europa.eu/edm/1/ns/forms/EPOC-FORM-1#"
FORM2_NS    = "http://data.europa.eu/edm/1/ns/forms/EPOC-PR-FORM-2#"
FORM3_NS    = "http://data.europa.eu/edm/1/ns/forms/EPOC-FORM-3#"
FORM5_NS    = "http://data.europa.eu/edm/1/ns/forms/EPOC-PR-FORM-5#"
FORM6_NS    = "http://data.europa.eu/edm/1/ns/forms/EPOC-PR-FORM-6#"

COMMON_NS   = "http://uri.etsi.org/03120/common/2016/02/Common"
CORE_NS     = "http://uri.etsi.org/03120/common/2019/10/Core"
DOC_NS      = "http://uri.etsi.org/03120/common/2020/09/Document"
TASK_NS     = "http://uri.etsi.org/03120/common/2020/09/Task"
AUTH_NS     = "http://uri.etsi.org/03120/common/2020/09/Authorisation"
EF1_NS      = "http://uri.etsi.org/03120/common/2025/02/EpocForm1"
PH_NS       = "http://uri.etsi.org/03120/common/2025/02/EPOCPlaceholder"
NOTIFY_NS   = "http://uri.etsi.org/03120/common/2016/02/Notification"

EC_AUTH_NS  = "http://uri.etsi.org/03120/common/2025/02/EioAuthority"

ns_map = {
    None : CORE_NS,
    'auth' : AUTH_NS,
    'doc' : DOC_NS,
    'task' : TASK_NS,
    'notify' : NOTIFY_NS,
    'ef1' : EF1_NS,
    'xsi' : XSI_NS,
    'ph' : PH_NS,

    'epoc' : EPOC_NS,
    'eio' : EIO_NS,
    'epocform1' : FORM1_NS,
    'epocform2' : FORM2_NS,
    'epocform3' : FORM3_NS,
    'eopcform5' : FORM5_NS,
    'eopcform6' : FORM6_NS,
    'common' : COMMON_NS,
    'ecauth' : EC_AUTH_NS,
}