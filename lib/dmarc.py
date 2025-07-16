import re
from enum import Enum
from typing import Optional, List, Dict, Tuple, NamedTuple, Any

class DMARCError:
    """
    Represents an error encountered during DMARC record checking.
    """
    def __init__(self, error_id: str, description: str):
        self.id = error_id
        self.description = description

    def __str__(self):
        return f"[{self.id}] {self.description}"

    def __repr__(self):
        return f"DMARCError(id='{self.id}', description='{self.description}')"

# 1. DNS Lookup Errors
DNS_NO_RECORD_FOUND = DMARCError(
    "DNS_001", "No DMARC TXT record found for the domain (_dmarc.yourdomain.com)."
)
DNS_TIMEOUT = DMARCError(
    "DNS_002", "The DNS resolution timed out (e.g., due to server unreachable)."
)
DNS_NXDOMAIN = DMARCError(
    "DNS_003", "The queried domain name does not exist (NXDOMAIN)."
)
DNS_REFUSED = DMARCError(
    "DNS_004", "The DNS server explicitly refused to answer the query (REFUSED)."
)
DNS_YXDOMAIN = DMARCError(
    "DNS_005", "The queried domain name exists, but no record of the requested type (TXT) was found (YXDOMAIN)."
)
DNS_NO_ANSWER_SECTION = DMARCError(
    "DNS_006", "The DNS response contains no 'answer' section, indicating no record was returned."
)
DNS_INCORRECT_RECORD_TYPE = DMARCError(
    "DNS_007", "A record exists at _dmarc.yourdomain.com but it is not a TXT record."
)
DNS_WILDCARD_ISSUE = DMARCError(
    "DNS_008", "Misleading record returned due to a wildcard DNS entry."
)
DNS_PROPAGATION_DELAY = DMARCError(
    "DNS_009", "DMARC record changes have not yet propagated across all DNS servers."
)
DNS_SERVER_MISCONFIGURATION = DMARCError(
    "DNS_010", "The domain's nameservers are misconfigured, preventing proper resolution."
)
DNS_FIREWALL_RESTRICTION = DMARCError(
    "DNS_011", "Network or firewall restrictions preventing DNS queries."
)

# 2. Parsing and Syntax Errors
PARSING_MULTIPLE_DMARC_RECORDS = DMARCError(
    "PARSE_001", "Multiple TXT records starting with 'v=DMARC1' found for the domain."
)
PARSING_LEADING_WHITESPACE = DMARCError(
    "PARSE_002", "The DMARC TXT record value starts with leading whitespace, making it invalid."
)
PARSING_MISSING_REQUIRED_TAG = DMARCError(
    "PARSE_003", "Missing a required DMARC tag (e.g., 'v=DMARC1' or 'p=')."
)
PARSING_INVALID_VERSION_TAG = DMARCError(
    "PARSE_004", "Incorrect or invalid value for the 'v' (version) tag (must be 'DMARC1')."
)
PARSING_INVALID_POLICY_VALUE = DMARCError(
    "PARSE_005", "Invalid value for the 'p' (policy) tag (must be 'none', 'quarantine', or 'reject')."
)
PARSING_INCORRECT_TAG_ORDER = DMARCError(
    "PARSE_006", "DMARC tags are not in the recommended order (v=DMARC1 should be first)."
)
PARSING_MISSING_OR_INCORRECT_SEPARATORS = DMARCError(
    "PARSE_007", "Missing or incorrect separators (e.g., '=' between tag-value, ';' between pairs)."
)
PARSING_EXTRA_CHARACTERS_OR_TYPOS = DMARCError(
    "PARSE_008", "Extra characters, spaces, or typos within tag names or values."
)
PARSING_INCORRECTLY_QUOTED = DMARCError(
    "PARSE_009", "DMARC record is incorrectly enclosed in quotation marks."
)
PARSING_INVALID_RUA_RUF_URI = DMARCError(
    "PARSE_010", "Invalid format for 'rua' or 'ruf' URIs (e.g., missing 'mailto:')."
)
PARSING_MULTIPL_URI = DMARCError(
    "PARSE_011", "More than two mailto URIs given, which senders may ignore"
)
PARSING_DUPLICATE_TAGS = DMARCError(
    "PARSE_012", "Duplicate DMARC tags found within the record."
)

# 3. Policy Evaluation Errors
POLICY_IS_NONE = DMARCError(
    "POLICY_001", "The DMARC policy is 'p=none', which offers no enforcement against spoofing."
)
POLICY_PCT_TOO_LOW = DMARCError(
    "POLICY_002", "The 'pct' (percentage) tag is set to less than 100 with an enforcement policy."
)
POLICY_SUBDOMAIN_POLICY_OVERRIDE = DMARCError(
    "POLICY_003", "The 'sp' (subdomain policy) tag is set to 'none' or weaker than the main policy."
)
POLICY_NO_SPF_ALIGNMENT = DMARCError(
    "POLICY_004", "Lack of proper SPF record configuration or alignment, impacting DMARC."
)
POLICY_NO_DKIM_ALIGNMENT = DMARCError(
    "POLICY_005", "Lack of proper DKIM record configuration or alignment, impacting DMARC."
)
POLICY_SPF_DKIM_ALIGNMENT_FAILURE = DMARCError(
    "POLICY_006", "SPF and/or DKIM authentication passed, but alignment with the From: header domain failed."
)
POLICY_SPF_TOO_MANY_LOOKUPS = DMARCError(
    "POLICY_007", "SPF record exceeds the 10-lookup limit, potentially causing SPF failures."

)
POLICY_DKIM_INVALID_SIGNATURE = DMARCError(
    "POLICY_008", "DKIM signature is invalid, corrupted, or public key mismatch."
)


class DMARCWarning:
    """
    Represents a DMARC warning with a unique ID and a detailed description.
    """
    def __init__(self, warning_id: str, description: str):
        self.id = warning_id
        self.description = description

    def __str__(self):
        return f"WARNING {self.id}: {self.description}"

    def __repr__(self):
        return f"DMARCWarning(id='{self.id}', description='{self.description}')"

# General Record Structure Warnings
DMARC_WARNING_MISSING_V_TAG = DMARCWarning(
    "G001",
    "Missing 'v=DMARC1' tag. While mandatory per RFC, a robust parser might default to 'DMARC1' and issue this warning."
)
DMARC_WARNING_V_TAG_NOT_FIRST = DMARCWarning(
    "G002",
    "The 'v=DMARC1' tag is present but not the first tag in the record, violating RFC order."
)
DMARC_WARNING_MISSING_P_TAG = DMARCWarning(
    "G003",
    "Missing 'p=' tag. While mandatory per RFC, a robust parser might default to 'p=none' and issue this warning."
)
DMARC_WARNING_P_TAG_NOT_AFTER_V = DMARCWarning(
    "G004",
    "The 'p=' tag is present but not immediately following the 'v=' tag, violating RFC order."
)
DMARC_WARNING_UNKNOWN_TAG_FOUND = DMARCWarning(
    "G005",
    "An unknown or unrecognized tag was found in the DMARC record. Unknown tags must be ignored per RFC."
)
DMARC_WARNING_DUPLICATE_TAG = DMARCWarning(
    "G006",
    "A DMARC tag appears more than once in the record. The first encountered value will typically be used."
)
DMARC_WARNING_EMPTY_RECORD_STRING = DMARCWarning(
    "G007",
    "The DMARC record string is entirely empty."
)
DMARC_WARNING_RECORD_STARTS_WITH_WHITESPACE = DMARCWarning(
    "G008",
    "The DMARC record string starts with leading whitespace, indicating poor record hygiene."
)
DMARC_WARNING_RECORD_ENDS_WITH_WHITESPACE = DMARCWarning(
    "G009",
    "The DMARC record string ends with trailing whitespace, indicating poor record hygiene."
)
DMARC_WARNING_REMAINING_TAGS_IGNORED_DUE_TO_SYNTAX_ERROR = DMARCWarning(
    "G010",
    "A syntax error occurred after the 'p=' tag, causing subsequent tags to be unparseable and ignored per RFC guidance."
)
DMARC_WARNING_UNRELATED_TXT_RECORD_ON_DMARC_DOMAIN = DMARCWarning(
    "G011",
    "An unrelated TXT record (not starting with 'v=DMARC1') was found at the _dmarc subdomain. This may indicate misconfiguration."
)
DMARC_WARNING_SPF_RECORD_ON_DMARC_DOMAIN = DMARCWarning(
    "G012",
    "An SPF record (starting with 'v=spf1') was found at the _dmarc subdomain. SPF records should typically not be placed here."
)
DMARC_WARNING_DMARC_RECORD_ON_ROOT_DOMAIN = DMARCWarning(
    "G013",
    "The DMARC record was found on the root domain instead of the standard '_dmarc' subdomain. This is non-standard and may lead to unexpected behavior."
)
DMARC_WARNING_MISSING_SEMICOLON = DMARCWarning(
    "G014",
    "Semicolons are missing between DMARC tags. The parser will attempt to recover."
)
DMARC_WARNING_EXTRA_SEMICOLONS = DMARCWarning(
    "G015",
    "Multiple semicolons were found between DMARC tags."
)
DMARC_WARNING_WHITESPACE_AROUND_EQUALS = DMARCWarning(
    "G016",
    "Whitespace found around the equals sign in a tag-value pair (e.g., 'p = none')."
)
DMARC_WARNING_INCONSISTENT_CASING = DMARCWarning(
    "G017",
    "Inconsistent casing detected for a DMARC tag name (e.g., 'V=DMARC1' instead of 'v=DMARC1')."
)
DMARC_WARNING_NON_ASCII_CHARACTERS = DMARCWarning(
    "G018",
    "Non-ASCII characters detected in the DMARC record string, which are not part of a valid URI."
)
DMARC_WARNING_TRUNCATED_RECORD = DMARCWarning(
    "G019",
    "The DMARC record appears to be truncated or incomplete."
)


# Tag-Specific Syntax and Value Warnings
DMARC_WARNING_P_INVALID_VALUE = DMARCWarning(
    "T001",
    "The 'p' (policy) tag has an invalid value. Valid values are 'none', 'quarantine', or 'reject'."
)
DMARC_WARNING_P_EMPTY_VALUE = DMARCWarning(
    "T002",
    "The 'p' (policy) tag has an empty value."
)
DMARC_WARNING_SP_INVALID_VALUE = DMARCWarning(
    "T003",
    "The 'sp' (subdomain policy) tag has an invalid value. Valid values are 'none', 'quarantine', or 'reject'."
)
DMARC_WARNING_SP_EMPTY_VALUE = DMARCWarning(
    "T004",
    "The 'sp' (subdomain policy) tag has an empty value."
)
DMARC_WARNING_SP_ON_NON_SUBDOMAIN_RECORD = DMARCWarning(
    "T005",
    "The 'sp' tag is present on a DMARC record for a specific subdomain or root domain, where it may be redundant or confusing."
)
DMARC_WARNING_ADKIM_INVALID_VALUE = DMARCWarning(
    "T006",
    "The 'adkim' (DKIM alignment mode) tag has an invalid value. Valid values are 's' (strict) or 'r' (relaxed)."
)
DMARC_WARNING_ADKIM_EMPTY_VALUE = DMARCWarning(
    "T007",
    "The 'adkim' (DKIM alignment mode) tag has an empty value."
)
DMARC_WARNING_ADKIM_STRICT = DMARCWarning(
    "T008",
    "The 'adkim' (DKIM alignment mode) is set to 'strict'. This can be highly restrictive and may cause legitimate mail to fail DMARC."
)
DMARC_WARNING_ASPF_INVALID_VALUE = DMARCWarning(
    "T009",
    "The 'aspf' (SPF alignment mode) tag has an invalid value. Valid values are 's' (strict) or 'r' (relaxed)."
)
DMARC_WARNING_ASPF_EMPTY_VALUE = DMARCWarning(
    "T010",
    "The 'aspf' (SPF alignment mode) tag has an empty value."
)
DMARC_WARNING_ASPF_STRICT = DMARCWarning(
    "T011",
    "The 'aspf' (SPF alignment mode) is set to 'strict'. This can be highly restrictive and may cause legitimate mail to fail DMARC."
)
DMARC_WARNING_PCT_NON_NUMERIC_VALUE = DMARCWarning(
    "T012",
    "The 'pct' (percentage) tag has a non-numeric value. It should be an integer between 0 and 100."
)
DMARC_WARNING_PCT_OUT_OF_RANGE_VALUE = DMARCWarning(
    "T013",
    "The 'pct' (percentage) tag has a value outside the valid 0-100 range. The value will be clamped."
)
DMARC_WARNING_PCT_EMPTY_VALUE = DMARCWarning(
    "T014",
    "The 'pct' (percentage) tag has an empty value."
)
DMARC_WARNING_RF_INVALID_FORMAT = DMARCWarning(
    "T015",
    "The 'rf' (reporting format) tag contains an invalid format. 'afrf' is the currently defined standard."
)
DMARC_WARNING_RF_UNSUPPORTED_MULTIPLE_FORMATS = DMARCWarning(
    "T016",
    "The 'rf' (reporting format) tag specifies multiple formats, some of which may be unsupported by the parser."
)
DMARC_WARNING_RF_EMPTY_VALUE = DMARCWarning(
    "T017",
    "The 'rf' (reporting format) tag has an empty value."
)
DMARC_WARNING_RI_NON_NUMERIC_VALUE = DMARCWarning(
    "T018",
    "The 'ri' (reporting interval) tag has a non-numeric value. It should be a positive integer representing seconds."
)
DMARC_WARNING_RI_ZERO_OR_NEGATIVE_VALUE = DMARCWarning(
    "T019",
    "The 'ri' (reporting interval) tag has a zero or negative value. It should be a positive integer representing seconds."
)
DMARC_WARNING_RI_VERY_LOW_VALUE = DMARCWarning(
    "T020",
    "The 'ri' (reporting interval) is set to a very low value (less than 4 hours). This may lead to an excessive number of reports."
)
DMARC_WARNING_RI_VERY_HIGH_VALUE = DMARCWarning(
    "T021",
    "The 'ri' (reporting interval) is set to a very high value. This may indicate a lack of active monitoring."
)
DMARC_WARNING_RI_EMPTY_VALUE = DMARCWarning(
    "T022",
    "The 'ri' (reporting interval) tag has an empty value."
)
DMARC_WARNING_RUA_NO_TAG_FOUND = DMARCWarning(
    "T023",
    "No 'rua' (aggregate reporting URI) tag found. No aggregate reports will be sent, limiting DMARC visibility."
)
DMARC_WARNING_RUA_INVALID_URI_FORMAT = DMARCWarning(
    "T024",
    "The 'rua' (aggregate reporting URI) tag contains an invalid URI format. Only 'mailto:' URIs are explicitly supported by senders."
)
DMARC_WARNING_RUA_UNSUPPORTED_URI_SCHEME = DMARCWarning(
    "T025",
    "The 'rua' (aggregate reporting URI) uses an unsupported URI scheme (other than 'mailto:'). Senders may ignore this URI."
)
DMARC_WARNING_RUA_MISSING_MAILTO_SCHEME = DMARCWarning(
    "T026",
    "The 'rua' (aggregate reporting URI) is an email address but is missing the 'mailto:' scheme prefix."
)
DMARC_WARNING_RUA_MULTIPLE_URIS_NO_COMMA = DMARCWarning(
    "T027",
    "Multiple 'rua' (aggregate reporting URIs) are present but are not correctly separated by commas."
)
DMARC_WARNING_RUA_MORE_THAN_TWO_URIS = DMARCWarning(
    "T028",
    "More than two 'rua' (aggregate reporting URIs) were found. Receivers may ignore URIs beyond the first two."
)
DMARC_WARNING_RUA_EMPTY_VALUE = DMARCWarning(
    "T029",
    "The 'rua' (aggregate reporting URI) tag has an empty value."
)
DMARC_WARNING_RUF_NO_TAG_FOUND = DMARCWarning(
    "T030",
    "No 'ruf' (forensic reporting URI) tag found. No forensic reports will be sent."
)
DMARC_WARNING_RUF_INVALID_URI_FORMAT = DMARCWarning(
    "T031",
    "The 'ruf' (forensic reporting URI) tag contains an invalid URI format. Only 'mailto:' URIs are explicitly supported by senders."
)
DMARC_WARNING_RUF_UNSUPPORTED_URI_SCHEME = DMARCWarning(
    "T032",
    "The 'ruf' (forensic reporting URI) uses an unsupported URI scheme (other than 'mailto:'). Senders may ignore this URI."
)
DMARC_WARNING_RUF_MISSING_MAILTO_SCHEME = DMARCWarning(
    "T033",
    "The 'ruf' (forensic reporting URI) is an email address but is missing the 'mailto:' scheme prefix."
)
DMARC_WARNING_RUF_MULTIPLE_URIS_NO_COMMA = DMARCWarning(
    "T034",
    "Multiple 'ruf' (forensic reporting URIs) are present but are not correctly separated by commas."
)
DMARC_WARNING_RUF_MORE_THAN_TWO_URIS = DMARCWarning(
    "T035",
    "More than two 'ruf' (forensic reporting URIs) were found. Receivers may ignore URIs beyond the first two."
)
DMARC_WARNING_RUF_EMPTY_VALUE = DMARCWarning(
    "T036",
    "The 'ruf' (forensic reporting URI) tag has an empty value."
)
DMARC_WARNING_FO_INVALID_OPTION_CHAR = DMARCWarning(
    "T037",
    "The 'fo' (failure reporting options) tag contains an invalid option character. Valid options are '0', '1', 'd', or 's'."
)
DMARC_WARNING_FO_DUPLICATE_OPTION_CHAR = DMARCWarning(
    "T038",
    "The 'fo' (failure reporting options) tag contains a duplicate option character."
)
DMARC_WARNING_FO_EMPTY_VALUE = DMARCWarning(
    "T039",
    "The 'fo' (failure reporting options) tag has an empty value."
)


# Logical/Best Practice/External Lookup Warnings
DMARC_WARNING_PCT_NOT_100_WITH_ENFORCEMENT = DMARCWarning(
    "L001",
    "The 'pct' (percentage) tag is not 100 while the policy ('p' tag) is set to 'reject' or 'quarantine'. This means full enforcement is not active."
)
DMARC_WARNING_RUF_ENABLED_WITHOUT_RUA = DMARCWarning(
    "L002",
    "Forensic reporting ('ruf' tag) is enabled, but aggregate reporting ('rua' tag) is missing. Receiving only forensic reports may limit overall DMARC analysis."
)
DMARC_WARNING_WILDCARD_DOMAIN_DETECTED = DMARCWarning(
    "L003",
    "A wildcard domain was detected in the DMARC record's placement (e.g., '_dmarc.*.example.com'). This is an unusual configuration and may lead to unexpected behavior."
)
DMARC_WARNING_REPORT_URI_MISSING_MX = DMARCWarning(
    "L004",
    "The domain part of a DMARC report URI (rua or ruf) is missing MX records, meaning DMARC reports cannot be delivered to that address."
)
DMARC_WARNING_REPORT_URI_DEST_NO_ACCEPTANCE_INDICATION = DMARCWarning(
    "L005",
    "The destination of a DMARC report URI (rua or ruf) does not explicitly indicate that it accepts DMARC reports for the given domain. This may require further DNS lookups (e.g., for a DMARC reporting service TXT record)."
)

class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class AlignmentMode(str, ExtendedEnum):
    """Enum for the adkim/aspf tag values."""
    RELAXED = "r"
    STRICT = "s"


class Policy(str, ExtendedEnum):
    """Enum for the p/sp tag values."""
    NONE = "none"
    QUARANTINE = "quarantine"
    REJECT = "reject"


class ReportFormat(str, ExtendedEnum):
    """Enum for the report format values."""
    AFRF = 'afrf'  # Authentication Failure Reporting Format (AFRF)


class TagValue:
    value: Any
    explicit: bool = False
    valid: bool = True

    def __init__(self, value: Any, explicit: bool = False, valid: bool = True):
        self.value = value
        self.explicit = explicit
        self.valid = valid

    def __repr__(self) -> str:
        return f"{self.value}"

    def __str__(self) -> str:
        if type(self.value) == str:
            return self.value
        if type(self.value) == int:
            return str(self.value)
        if type(self.value) == list:
            return ', '.join(map(str, self.value))
        else:
            raise NotImplementedError

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, TagValue) and self.value == other.value and self.explicit == other.explicit and self.valid == other.valid

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)


class DMARCRecord:
    """
    Represents a DMARC record with specific known tags, providing
    defaults where applicable and capturing unknown tags.

    :param record_dict:
        Dictionary of DMARC tags (key: tag name, value: tag data).
        Assumes required tags such as 'v' and 'p' are present and valid.
    """

    def __init__(self, record_dict: Dict[str, str]) -> None:
        # Known tags:
        #   v (REQUIRED, must be DMARC1) -- but assume it's already validated
        #   p (Policy; REQUIRED in policy records; no default here)
        #   adkim (AlignmentMode; default='r')
        #   aspf (AlignmentMode; default='r')
        #   fo (list of failure-reporting options; default='0')
        #   pct (int; default=100)
        #   rf (list of report formats; default='afrf')
        #   ri (int; default=86400)
        #   rua (list of URIs; optional)
        #   ruf (list of URIs; optional)
        #   sp (Policy; optional; no explicit default, but if absent, 'p' applies to subdomains)
        #   Unknown tags are stored in self.unknown_tags
        self.v: TagValue = TagValue('DMARC1', True)
        self.p: TagValue = TagValue(Policy(record_dict['p']), True)

        # 'adkim' can be either 'r' or 's'
        if 'adkim' in record_dict:
            adkim_str = record_dict['adkim']
            if adkim_str in AlignmentMode.list():
                self.adkim = TagValue(AlignmentMode(adkim_str), True)
            else:
                self.adkim = TagValue(adkim_str, True, False)
        else:
            self.adkim: TagValue = TagValue(AlignmentMode.RELAXED)

        # 'aspf' can be either 'r' or 's'
        if 'aspf' in record_dict:
            aspf_str = record_dict['aspf']
            if aspf_str in AlignmentMode.list():
                self.aspf = TagValue(AlignmentMode(aspf_str), True)
            else:
                self.aspf = TagValue(aspf_str, True, False)
        else:
            self.aspf: TagValue = TagValue(AlignmentMode.RELAXED)

        # 'fo' can be multiple colon-separated values (e.g., '0', '1', 'd', 's', etc.)
        if 'fo' in record_dict:
            fo_list = []
            fo_valid = True
            for fo_str in record_dict['fo'].split(':'):
                fo_list.append(fo_str)
                if fo_str not in ['0', '1', 'd', 's']:
                    fo_valid = False
            self.fo: TagValue = TagValue(fo_list, True, fo_valid)
        else:
            self.fo: TagValue = TagValue(['0'])

        # 'pct' is an integer with default 100
        if 'pct' in record_dict:
            try:
                pct_val = int(record_dict['pct'])
                if pct_val < 0 or pct_val > 100:
                    raise ValueError
                self.pct: TagValue = TagValue(pct_val, True)
            except ValueError:
                self.pct: TagValue = TagValue(record_dict['pct'], True, False)
        else:
            self.pct: TagValue = TagValue(100)

        # 'rf' is a colon-separated list of one or more report formats; default 'afrf'
        if 'rf' in record_dict:
            rf_list = []
            rf_valid = True
            for rf_str in record_dict['rf'].split(':'):
                rf_list.append(rf_str)
                if rf_str not in ReportFormat.list():
                    rf_valid = False
            self.rf: TagValue = TagValue(rf_list, True, rf_valid)
        else:
            self.rf: TagValue = TagValue([ReportFormat.AFRF])

        # 'ri' is the aggregate report interval, default 86400
        if 'ri' in record_dict:
            try:
                ri_val = int(record_dict['ri'])
                self.ri: TagValue = TagValue(ri_val, True)
            except ValueError:
                self.ri: TagValue = TagValue(record_dict['ri'], True, False)
        else:
            self.ri: TagValue = TagValue(86400)

        # 'rua' is a comma-separated list of URIs (if present)
        if 'rua' in record_dict:
            rua_str = record_dict['rua']
            self.rua: TagValue = TagValue([uri.strip() for uri in rua_str.split(",")] if rua_str else [], True)
        else:
            self.rua: TagValue = TagValue(None)

        # 'ruf' is a comma-separated list of URIs (if present)
        if 'ruf' in record_dict:
            ruf_str = record_dict['ruf']
            self.ruf: TagValue = TagValue([uri.strip() for uri in ruf_str.split(",")] if ruf_str else [], True)
        else:
            self.ruf: TagValue = TagValue(None)

        # 'sp' is an optional policy for subdomains
        if 'sp' in record_dict:
            sp_str = record_dict['sp']
            if sp_str in Policy.list():
                self.sp: TagValue = TagValue(Policy(sp_str), True)
            else:
                self.sp: TagValue = TagValue(sp_str, True, False)
        else:
            self.sp: TagValue = TagValue(None)

        # Gather unknown (unregistered) tags
        known_tags = {
            "v",
            "adkim",
            "aspf",
            "fo",
            "p",
            "pct",
            "rf",
            "ri",
            "rua",
            "ruf",
            "sp",
        }
        self.unknown_tags: Dict[str, str] = {
            k: v for k, v in record_dict.items() if k not in known_tags
        }

    def __repr__(self) -> str:
        return (
            f"DMARCRecord("
            f"v={self.v!r}, adkim={self.adkim!r}, aspf={self.aspf!r}, fo={self.fo!r}, "
            f"p={self.p!r}, pct={self.pct!r}, rf={self.rf!r}, ri={self.ri!r}, "
            f"rua={self.rua!r}, ruf={self.ruf!r}, sp={self.sp!r}, "
            f"unknown_tags={self.unknown_tags!r}"
            f")"
        )

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            v = self.p == other.p
            v &= self.adkim == other.adkim
            v &= self.aspf == other.aspf
            v &= self.fo == other.fo
            v &= self.pct == other.pct
            v &= self.rf == other.rf
            v &= self.ri == other.ri
            v &= self.rua == other.rua
            v &= self.ruf == other.ruf
            v &= self.sp == other.sp
            return v
        else:
            return False

    def normalize(self) -> str:
        text = "v=DMARC1; "
        text += f"p={self.p}; "
        if self.adkim.explicit:
            text += f"adkim={self.adkim}; "
        if self.aspf.explicit:
            text += f"aspf={self.aspf}; "
        if self.fo.explicit:
            fo = ':'.join(self.fo.value)
            text += f"fo={fo}; "
        if self.pct.explicit:
            text += f"pct={self.pct}; "
        if self.rf.explicit:
            rf = ':'.join(self.rf.value)
            text += f"rf={rf}; "
        if self.ri.explicit:
            text += f"ri={self.ri}; "
        if self.rua.explicit:
            text += f"rua={self.rua}; "
        if self.ruf.explicit:
            text += f"ruf={self.ruf}; "
        if self.sp:
            text += f"sp={self.sp}; "

        return text.strip()

    def is_valid(self) -> bool:
        result = True
        result &= self.v.valid
        result &= self.p.valid
        result &= self.adkim.valid
        result &= self.aspf.valid
        result &= self.fo.valid
        result &= self.pct.valid
        result &= self.rf.valid
        result &= self.ri.valid
        result &= self.rua.valid
        result &= self.ruf.valid
        result &= self.sp.valid
        return result



def consume_prefix(s: str, prefix: str | list[str], strip_sp: bool = True) -> Tuple[str | None, str | None]:
    """
    Strips leading spaces/tabs from s, checks if it starts with prefix,
    and if so removes prefix and returns the remainder of the string.
    Otherwise, returns None.
    """
    if strip_sp:
        s = s.lstrip(" \t")
    if type(prefix) is str:
        prefix = [prefix]
    matched_prefix = None
    for item in prefix:
        if s.startswith(item):
            matched_prefix = item
            break
    if matched_prefix is None:
        return None, None
    return s[len(matched_prefix):], matched_prefix


def parse_remaining_tags(dmarc_record: str) -> dict[str, str] | None:
    # Remove any leading and trailing semicolon for the split operation, if any, and only one respectively
    dmarc_record = dmarc_record.removeprefix(';').removesuffix(';')

    # Split the string by semicolons to get individual "key=value" chunks
    raw_pairs = dmarc_record.split(';')

    # Precompute the set of allowed start/end characters
    # (ASCII 33..58, 60..125 => excludes ASCII code 59 which is ';')
    allowed_chars = {chr(c) for c in range(33, 127) if c != 59}

    # Dictionary to hold parsed tags
    tags = {}

    for pair in raw_pairs:
        # Each valid pair must contain at least one '='
        if '=' not in pair:
            return None

        # But the split is done only at the first one
        key_part, value_part = pair.split('=', maxsplit=1)

        # Strip whitespace (WSP) around both key and value
        key = key_part.strip(' \t')
        value = value_part.strip(' \t')

        # Key checks:
        # - must not be empty
        # - first character must be alphabetic
        # - subsequent characters alphanumeric or underscore
        if not key:
            return None
        if not key[0].isalpha():
            return None
        if not all(ch.isalnum() or ch == '_' for ch in key[1:]):
            return None

        # Value checks:
        # - must not be empty
        # - first and last character must be in the allowed set
        if not value:
            return None
        if value[0] not in allowed_chars or value[-1] not in allowed_chars:
            return None

        # No duplicate keys allowed
        if key in tags:
            return None

        tags[key] = value

    return tags


def parse_dmarc(dmarc_record: str) -> Optional[DMARCRecord]:
    original_dmarc_record = dmarc_record
    dmarc_record, _ = consume_prefix(dmarc_record, 'v', False)
    if dmarc_record is None:
        if original_dmarc_record.lstrip(' \t').startswith('v'):
            err = PARSING_LEADING_WHITESPACE
        return None

    prefix_list = ['=', 'DMARC1', ';', 'p', '=']
    for prefix in prefix_list:
        dmarc_record, _ = consume_prefix(dmarc_record, prefix)
        if dmarc_record is None:
            return None

    dmarc_record, dmarc_request = consume_prefix(dmarc_record, ['none', 'quarantine', 'reject'], False)
    if dmarc_record is None:
        return None

    # After this point, the record may become invalid and may be ignored
    # Syntax errors in the remainder of the record SHOULD be discarded in favor of default values (if any) or ignored outright.
    # Therefore, the approach is completely different
    tags = parse_remaining_tags(dmarc_record)
    if tags is None:
        # If the remaining tags are invalid, we return the bare minimum
        return DMARCRecord({'p': dmarc_request})

    # The remaining tags should be syntactically ok
    tags['p'] = dmarc_request
    record = DMARCRecord(tags)
    return record

dmarc_regex = re.compile(r"(^[^a-z]*v[^a-z]*=)|(\bD[^a-z]*M[^a-z]*A[^a-z]*R[^a-z]*C\b)", re.IGNORECASE)

def dmarc_heuristic(text: str) -> bool:
    """
    Applies a heuristic to determine if the given text likely contains DMARC-related information.

    This function uses a pre-compiled regular expression to search for patterns
    commonly found in DMARC records or reports within the input text.

    Args:
        text: The input string to be analyzed.

    Returns:
        True if any of the DMARC patterns are found in the text, False otherwise.
    """
    return dmarc_regex.search(text) is not None
