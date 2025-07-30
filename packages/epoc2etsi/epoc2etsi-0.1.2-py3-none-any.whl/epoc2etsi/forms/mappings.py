PRIORITY_MAPPING = {
    "AS_SOON_AS_POSSIBLE" : "TenDaysASAP",
    "AT_THE_END_OF_TEN_DAYS" : "TenDaysSubjectToEA",
    "IMMINENT_THREAT_TO_LIFE" : "EightHours",
    "IMMINENT_THREAT_TO_CRITICAL_INFRASTRUCTURE" : "EightHours",
}

ROLE_MAPPING = {
    "PUBLIC_PROSECUTOR" : "PublicProsecutor",
    "JUDGE_COURT_OR_INVESTIGATING_JUDGE"  : "JudgeCourtOrInvestigatingJudge",
    "JUDGE"  : "JudgeCourtOrInvestigatingJudge",
    "OTHER_COMPETENT_AUTHORITY" : "OtherCompetentAuthority",
}

LANGUAGE_MAPPING = {
    "fin" : "fi",
    "est" : "et",
    "eng" : "en",
    "dut" : "nl",
}

# TODO - work out what to do with "IP Address Range" and "IP Block"

IDENTIFIER_TYPE_MAPPING = {
    "IPV_4" : "IPV4Address",
    "IPV_6" : "IPV6Address",
    "IP_ADDRESS_RANGE" : "TBD",
    "IP_BLOCKS" : "TBD",
    "EMAIL" : "InternationalizedEmailAddress",
    "PHONE_NUMBER" : "InternationalE164",
    "IMEI_NUMBER" : "IMEI",
    "MAC_ADDRESS" : "MACAddress",
    "USER_ID" : "ServiceAccessIdentifier",
}
