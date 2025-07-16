from datetime import datetime
from json import loads
from time import time

from lib.counters import DataCounter, DataDistribution, DataPermutation
from lib.dmarc import parse_dmarc
from datasets import datasets
from lib.util import get_org_domain, log


def main():
    dns_protocol_counter = DataCounter(
        'DNS resolver protocol usage',
        'Shows which network protocol was used to communicate with the DNS resolver.',
        'Protocol'
    )
    dns_error_counter = DataCounter(
        'DNS resolver error',
        'Shows the distribution of DNS resolver errors encountered.',
        'Error'
    )
    dns_status_counter = DataCounter(
        'DNS resolver response status codes',
        'Shows the distribution of response codes, excluding DNS communication errors like timeouts.',
        'RCODE'
    )
    dns_request_type_counter = DataCounter(
        'DNS request type statistics',
        'Shows how often each DNS request type (resource record type) was requested. In the data collection, mainly MX and TXT records were requested, A and AAAA excluded as they are not directly relevant for mail.',
        'Type of RR'
    )
    dns_resolver_ips_counter = DataCounter(
        'DNS resolver IP statistics',
        'Shows which resolver IP addresses handled the requests. As a list of resolvers was used for random selection, all are equally used.',
        'Resolver IP'
    )
    dns_response_flags = DataCounter(
        'DNS flags rd and ra',
        'Shows which DNS flags were set in the resolver responses: Recursion Desired, indicates if the client means a recursive query and Recursion Available, in a response, indicates if the replying DNS server supports recursion.',
        'DNS Flag'
    )
    # response_data = DataCounter(
    #     'DNS response type',
    #     'Shows what data types were returned in the responses. The resolver may have answered with more RRs than requested.',
    #     'Type of RR in Response'
    # )
    dns_response_data_items = DataCounter(
        'DNS response number of answers',
        'Shows how many different answers were received in the responses. These may be "answer" sections, "additional" sections or "authority" sections.',
        'Number of Answers'
    )
    dns_response_sections = DataCounter(
        'DNS response answer section types',
        'Shows how many different section types were received in the responses. There are "answer", "additional" and "authority" sections.',
        'Types of Answer Sections'
    )
    dns_response_data_type = DataCounter(
        'DNS response data types statistics',
        'Shows the breakdown of different data types included in each response.',
        'Response Data Type'
    )
    dns_response_data_class = DataCounter(
        'DNS response data class statistics',
        'Shows the breakdown of DNS classes for the response data.',
        'Response Data Class'
    )
    dmarc_org_src_record = DataPermutation(
        'Likely DMARC record found',
        'Shows how many potential DMARC records were found on the organizational domain (org) and also the correct subdomain _dmarc (sub). The test checks if the word "dmarc" is included in any of the TXT records. This does not mean that the record is valid, only that it is likely to be valid. ✓ means applicable. ✗ means not applicable. - means not set (don\'t care)',
        None
    )
    dmarc_org_src_record_valid = DataPermutation(
        'Valid DMARC record found',
        'Shows how many valid DMARC records were found on the organizational domain (org) and also the correct subdomain _dmarc (sub). It is expected to have the DMARC record only on the correct subdomain. ✓ means applicable. ✗ means not applicable. - means not set (don\'t care)',
        None
    )
    mail_auth_valid = DataPermutation(
        'Valid Mail authentication records found',
        'Shows how many valid mail configurations were found. ✓ means applicable. ✗ means not applicable. - means not set (don\'t care)',
        ['MX', 'SPF', 'DMARC']
    )
    dmarc_requests = DataCounter(
        'DMARC request policy',
        'Shows which DMARC policies are requested. The sum percentage is relative to all domains queried so not all domains have a valid DMARC record.',
        'DMARC Policy'
    )
    dmarc_pct = DataDistribution(
        'DMARC sampling rate',
        'Shows various statistical information about the DMARC sampling rate (pct). This refers to the percentage of messages subjected to DMARC policy. Useful for incremental rollout of the policy. Permitted values are 0 to 100 as per specification.'
    )
    dmarc_pct_valid = DataCounter(
        'DMARC sampling rate validity',
        'Shows how many DMARC pct values are valid. This refers to the percentage of messages subjected to DMARC policy. Useful for incremental rollout of the policy.',
        'DMARC Pct Valid'
    )
    dmarc_pct_explicit = DataCounter(
        'DMARC sampling rate explicitness',
        'Shows how many DMARC pct values are set. Default value is 100 but is optional. This refers to the percentage of messages subjected to DMARC policy. Useful for incremental rollout of the policy.',
        'DMARC Pct explicit'
    )
    dmarc_adkim = DataCounter(
        'DMARC adkim',
        'Shows which values are set for adkim key. Indicates DKIM Identifier Alignment mode. r = relaxed, s = strict.',
        'DMARC value of adkim key'
    )
    dmarc_adkim_valid = DataCounter(
        'DMARC adkim valid',
        'Shows if values set for adkim key are valid. Indicates DKIM Identifier Alignment mode.',
        'DMARC adkim valid'
    )
    dmarc_adkim_explicit = DataCounter(
        'DMARC adkim explicit',
        'Shows if values set for adkim key are explicit. Indicates DKIM Identifier Alignment mode. r = relaxed, s = strict. Default value is r.',
        'DMARC adkim explicit'
    )
    dmarc_aspf = DataCounter(
        'DMARC aspf',
        'Shows which values are set for aspf key. Indicates SPF Identifier Alignment mode. r = relaxed, s = strict. Default value is r.',
        'DMARC value of aspf key'
    )
    dmarc_aspf_valid = DataCounter(
        'DMARC aspf valid',
        'Shows if values set for aspf key are valid. Indicates SPF Identifier Alignment mode. r = relaxed, s = strict. Default value is r.',
        'DMARC aspf valid'
    )
    dmarc_aspf_explicit = DataCounter(
        'DMARC aspf explicit',
        'Shows if values set for aspf key are explicit. Indicates SPF Identifier Alignment mode. r = relaxed, s = strict. Default value is r.',
        'DMARC aspf explicit'
    )
    dmarc_rf = DataCounter(
        'DMARC rf',
        'Shows which values are set for rf key. Format(s) to be used for failure reports. For this version, only "afrf" (Auth Failure Reporting Format) is supported.',
        'DMARC value of rf key'
    )
    dmarc_rf_valid = DataCounter(
        'DMARC rf valid',
        'Shows if values set for rf key are valid. Format(s) to be used for failure reports. For this version, only "afrf" (Auth Failure Reporting Format) is supported.',
        'DMARC rf valid'
    )
    dmarc_rf_explicit = DataCounter(
        'DMARC rf explicit',
        'Shows if values set rf aspf key are explicit. Format(s) to be used for failure reports. For this version, only "afrf" (Auth Failure Reporting Format) is supported.',
        'DMARC rf explicit'
    )
    dmarc_ri_dist = DataDistribution(
        'DMARC ri distribution',
        'Shows various statistical information about the DMARC ri distribution key. Interval (in seconds) between aggregate reports. Daily (86400 seconds) is default; other intervals are on a best-effort basis.'
    )
    dmarc_ri_valid = DataCounter(
        'DMARC ri valid',
        'Shows if values set for ri key are valid. Interval (in seconds) between aggregate reports. Daily (86400 seconds) is default; other intervals are on a best-effort basis.',
        'DMARC ri valid'
    )
    dmarc_ri_explicit = DataCounter(
        'DMARC ri explicit',
        'Shows if values set for ri aspf key are explicit. Interval (in seconds) between aggregate reports. Daily (86400 seconds) is default; other intervals are on a best-effort basis.',
        'DMARC ri explicit'
    )
    dmarc_sp = DataCounter(
        'DMARC sp statistics',
        'Shows which values are set for sp key. Requested policy for subdomains. If absent, subdomains follow the p policy. As no DMARC policy of a subdomain was requested in the query, no value should be set for this key. A default value does not exist, so any value given is explicit. If default is given, this refers to the case where no policy is set for the domain (as expected).',
        'DMARC value of sp key'
    )
    dmarc_sp_valid = DataCounter(
        'DMARC sp valid statistics',
        'Shows sp values set for sp key are valid. Requested policy for subdomains. If absent, subdomains follow the p policy. As no DMARC policy of a subdomain was requested in the query, no value should be set for this key. A default value does not exist, so any value given is explicit. If default is given, this refers to the case where no policy is set for the domain (as expected).',
        'DMARC sp valid'
    )
    dmarc_sp_explicit = DataCounter(
        'DMARC sp explicit statistics',
        'Shows if values set sp aspf key are explicit. Requested policy for subdomains. If absent, subdomains follow the p policy. As no DMARC policy of a subdomain was requested in the query, no value should be set for this key. A default value does not exist, so any value given is explicit. If default is given, this refers to the case where no policy is set for the domain (as expected).',
        'DMARC sp explicit'
    )
    cname_redirect_dist = DataDistribution(
        'DNS CNAME redirect distribution',
        'Shows various statistical information about the number of DNS CNAME responses, including redirects. Each CNAME response is counted separately.'
    )
    dns_response_data_len_dist = DataDistribution(
        'DNS answer data length distribution',
        'Shows various statistical information about the number of DNS answer in a DNS response. Each answer is counted separately. An answer consists of resource record (RR) fields. Usually 1 answer is expected, as only one RR Type is requested, but CNAMEs or other records may be included. This data includes all DNS requests done.'
    )
    dns_response_data_answers_len_dist = DataDistribution(
        'DNS Count of responses of type "answer"',
        'Shows various statistical information about the number of DNS answers in a DNS response of section type "answer" only. Each answer is counted separately. An answer consists of resource record (RR) fields. Usually 1 answer is expected, as only one RR Type is requested, but CNAMEs or other records may be included. This data includes all DNS requests done.'
    )
    dns_response_data_authorities_len_dist = DataDistribution(
        'DNS Count of responses of type "authorities"',
        'Shows various statistical information about the number of DNS answers in a DNS response of section type "authorities" only. Each answer is counted separately. An answer consists of resource record (RR) fields. Usually no answer is expected, as only one RR Type is requested, but DNS servers may respond with additional information.'
    )
    dns_response_data_additionals_len_dist = DataDistribution(
        'DNS Count of responses of type "additionals"',
        'Shows various statistical information about the number of DNS answers in a DNS response of section type "additionals" only. Each answer is counted separately. An answer consists of resource record (RR) fields. Usually no answer is expected, as only one RR Type is requested, but DNS servers may respond with additional information.'
    )
    dns_ttl_histogram = DataDistribution(
        'DNS TTL of response items distribution',
        'Shows various statistical information about the time-to-live (TTL) of the DNS responses. The TTL is the time in seconds that a DNS server has cached the data for. This data includes all DNS requests done.'
    )
    dns_response_data_data_len_dist = DataDistribution(
        'DNS Response data length of each answer item distribution',
        'Shows various statistical information about the length of data responses, also known as RDATA. This field contains the actual data of the DNS record and has a variable length, as per RDLENGTH. Especially TXT answers may increase this value significantly. This data includes all DNS requests done.'
    )
    dns_config_perm = DataPermutation(
        'DNS Mail configuration statistics',
        'Shows the distribution of different mail configuration combinations. TXT means that at least one TXT record exists at _dmarc.domain.de. DMARC means that at least one TXT record was found, which contains the string "dmarc" (potential dmarc record). Valid means that the record is indeed a valid DMARC record. ✓ means applicable. ✗ means not applicable. - means not set (don\'t care)',
        ['TXT', 'DMARC', 'Valid']
    )
    dns_mail_config_perm = DataPermutation(
        'Mail DNS configuration statistics',
        'Shows the distribution of different DNS mail configuration combinations. MX means that the domain has at least one MX record, SPF means that a SPF record is present and DMARC means that a DMARC record is present. ✓ means applicable. ✗ means not applicable. - means not set (don\'t care)',
        ['MX', 'SPF', 'DMARC']
    )
    dns_request_perm = DataPermutation(
        'Overview of DNS requests statistics',
        'Shows the number of DNS requests (MX and TXT) per org domain name. ✓ means applicable. ✗ means not applicable. - means not set (don\'t care)',
        None
    )
    dns_request_detailed_perm = DataPermutation(
        'Overview of DNS requests statistics',
        'Shows the number of DNS requests (MX and TXT) per org domain name, specific request type. ✓ means applicable. ✗ means not applicable. - means not set (don\'t care)',
        None
    )
    mx_dmarc_perm = DataPermutation(
        'MX and valid dmarc on domain',
        'Shows the distribution of different DNS configuration combinations. MX means that the domain has at least one MX record, DMARC means that a DMARC record is present and valid. ✓ means applicable. ✗ means not applicable. - means not set (don\'t care)',
        None
    )
    dmarc_adkim_aspf_valid_perm = DataPermutation(
        'DMARC adkim and aspf valid statistics',
        'Shows the distribution of different DMARC configuration combinations. adkim and aspf are valid if the value is set to r or s. Otherwise, the value is set to none. This is the default value. ✓ means applicable. ✗ means not applicable. - means not set (don\'t care)',
        None
    )
    dmarc_adkim_aspf_explicit_perm = DataPermutation(
        'DMARC adkim and aspf explicit statistics',
        'Shows the distribution of different DMARC configuration combinations. adkim and aspf are explicit if the value is set to r or s. Otherwise, the value is set to none. This is the default value. ✓ means applicable. ✗ means not applicable. - means not set (don\'t care)',
        None
    )

    data_collections = [
        dns_protocol_counter,
        dns_error_counter,
        dns_status_counter,
        dns_request_type_counter,
        dns_request_perm,
        dns_request_detailed_perm,
        dns_resolver_ips_counter,
        dns_response_flags,
        # response_data,
        dns_response_data_items,
        dns_response_sections,
        dns_response_data_type,
        dns_response_data_class,
        cname_redirect_dist,
        dns_response_data_len_dist,
        dns_response_data_answers_len_dist,
        dns_response_data_authorities_len_dist,
        dns_response_data_additionals_len_dist,
        dns_ttl_histogram,
        dns_response_data_data_len_dist,
        dns_config_perm,
        mx_dmarc_perm,
        dns_mail_config_perm,
        dmarc_org_src_record,
        dmarc_org_src_record_valid,
        dmarc_requests,
        dmarc_pct_valid,
        dmarc_pct_explicit,
        dmarc_pct,
        dmarc_adkim_valid,
        dmarc_adkim_explicit,
        dmarc_adkim,
        dmarc_aspf_valid,
        dmarc_aspf_explicit,
        dmarc_aspf,
        dmarc_adkim_aspf_explicit_perm,
        dmarc_adkim_aspf_valid_perm,
        dmarc_rf_valid,
        dmarc_rf_explicit,
        dmarc_rf,
        dmarc_ri_dist,
        dmarc_ri_valid,
        dmarc_ri_explicit,
        dmarc_sp,
        dmarc_sp_valid,
        dmarc_sp_explicit,
        mail_auth_valid,
    ]

    files = [datasets['de_combined2_org'], datasets['de_combined2_dmarc']]
    line_count = 0
    document_counter: int = 0
    domain_pass = set()
    exit_early = False

    for file in files:
        with open(file, mode='rt', encoding='utf-8') as fp:
            for line in fp:
                line_count += 1
                if line_count % 200000 == 0:
                    print(f"Processed {line_count} lines")
                if exit_early and line_count > 10000:
                    line_count = 0
                    break

                doc = loads(line.strip())
                document_counter += 1
                name = doc['name']
                org_name = get_org_domain(name)
                domain_pass.add(org_name)
                is_org_domain = org_name == get_org_domain(name)
                is_dmarc_name = name.startswith('_dmarc.')

                dmarc_org_src_record.announce(org_name)
                dmarc_org_src_record_valid.announce(org_name)
                dns_config_perm.announce(org_name)
                dns_mail_config_perm.announce(org_name)
                dns_request_perm.announce(org_name)
                dns_request_detailed_perm.announce(org_name)
                mx_dmarc_perm.announce(org_name)
                dmarc_adkim_aspf_explicit_perm.announce(org_name)
                dmarc_adkim_aspf_valid_perm.announce(org_name)
                mail_auth_valid.announce(org_name)

                if 'proto' in doc:
                    dns_protocol_counter[doc['proto']] += 1
                if 'status' in doc:
                    dns_status_counter[doc['status']] += 1
                if 'error' in doc:
                    dns_error_counter[doc['error']] += 1
                else:
                    dns_error_counter['No error'] += 1
                if 'type' in doc:
                    dns_request_type_counter[doc['type']] += 1
                    dns_request_perm[org_name][doc['type']] = True
                    if doc['type'] == 'MX':
                        dns_request_detailed_perm[org_name]['MX for Mail'] = True
                    if doc['type'] == 'TXT':
                        if is_dmarc_name:
                            dns_request_detailed_perm[org_name]['TXT for DMARC'] = True
                        else:
                            dns_request_detailed_perm[org_name]['TXT for SPF'] = True
                if 'resolver' in doc:
                    dns_resolver_ips_counter[doc['resolver']] += 1
                if 'flags' in doc:
                    for flag in doc['flags']:
                        dns_response_flags[flag] += 1
                    dns_response_flags.reference_sum += 1
                if 'data' in doc:
                    doc_data = doc['data']
                    dns_response_data_items[len(doc_data)] += 1
                    for key, value in doc_data.items():
                        dns_response_sections[key] += 1
                        dns_response_data_len_dist[len(value)] += 1
                        for sv in value:
                            if 'type' in sv:
                                dns_response_data_type[sv['type']] += 1
                            if 'class' in sv:
                                dns_response_data_class[sv['class']] += 1
                            if 'data' in sv:
                                dns_response_data_data_len_dist[len(sv['data'])] += 1
                    if 'authorities' in doc_data:
                        dns_response_data_authorities_len_dist[len(doc_data['authorities'])] += 1
                    if 'additionals' in doc_data:
                        dns_response_data_additionals_len_dist[len(doc_data['additionals'])] += 1
                    if 'answers' in doc_data:
                        answers = doc_data['answers']
                        dns_response_data_answers_len_dist[len(answers)] += 1
                        cname_cnt = 0
                        for answer in answers:
                            if 'type' in answer:
                                if answer['type'] == 'CNAME':
                                    cname_cnt += 1
                        if cname_cnt > 0:
                            cname_redirect_dist[cname_cnt] += 1
                        if 'type' in doc and doc['type'] == 'TXT':
                            if is_dmarc_name:
                                dns_config_perm[org_name]['TXT'] = True
                            for answer in answers:
                                if 'data' in answer:
                                    dns_ttl_histogram[answer['ttl']] += 1
                                    if 'dmarc' in answer['data'].lower():
                                        if is_dmarc_name:
                                            dns_config_perm[org_name]['DMARC'] = True
                                            dmarc_org_src_record[org_name]['Sub'] = True
                                            dmarc_org_src_record_valid[org_name]['Sub'] = True
                                        else:
                                            dmarc_org_src_record[org_name]['Org'] = True
                                        dmarc_request = parse_dmarc(answer['data'])
                                        if dmarc_request:
                                            if is_dmarc_name:
                                                dns_config_perm[org_name]['Valid'] = dmarc_request.is_valid()
                                                mx_dmarc_perm[org_name]['DMARC'] = dmarc_request.is_valid()
                                                dns_mail_config_perm[org_name]['DMARC'] = dmarc_request.is_valid()
                                                dmarc_org_src_record_valid[org_name]['Sub'] = dmarc_request.is_valid()
                                            else:
                                                dmarc_org_src_record_valid[org_name]['Org'] = dmarc_request.is_valid()
                                            dmarc_requests[dmarc_request.p.value.value] += 1
                                            if dmarc_request.p.value.value != 'none':
                                                mail_auth_valid[org_name]['DMARC'] = True
                                            if dmarc_request.adkim.explicit:
                                                dmarc_adkim_explicit['Explicit'] += 1
                                                dmarc_adkim_aspf_explicit_perm[org_name]['adkim explicit'] = True
                                                if dmarc_request.adkim.valid:
                                                    dmarc_adkim[dmarc_request.adkim.value.value] += 1
                                                    dmarc_adkim_valid['Pass'] += 1
                                                    dmarc_adkim_aspf_valid_perm[org_name]['adkim valid'] = True
                                                else:
                                                    dmarc_adkim_valid['Fail'] += 1
                                            else:
                                                dmarc_adkim_explicit['Default'] += 1
                                            if dmarc_request.aspf.explicit:
                                                dmarc_aspf_explicit['Explicit'] += 1
                                                dmarc_adkim_aspf_explicit_perm[org_name]['aspf explicit'] = True
                                                if dmarc_request.aspf.valid:
                                                    dmarc_aspf[dmarc_request.aspf.value.value] += 1
                                                    dmarc_aspf_valid['Pass'] += 1
                                                    dmarc_adkim_aspf_valid_perm[org_name]['aspf valid'] = True
                                                else:
                                                    dmarc_aspf_valid['Fail'] += 1
                                            else:
                                                dmarc_aspf_explicit['Default'] += 1
                                            if dmarc_request.pct.explicit:
                                                dmarc_pct_explicit['Explicit'] += 1
                                                if dmarc_request.pct.valid:
                                                    dmarc_pct[dmarc_request.pct.value] += 1
                                                    dmarc_pct_valid['Pass'] += 1
                                                else:
                                                    dmarc_pct_valid['Fail'] += 1
                                            else:
                                                dmarc_pct_explicit['Default'] += 1
                                            if dmarc_request.rf.explicit:
                                                dmarc_rf_explicit['Explicit'] += 1
                                                if dmarc_request.rf.valid:
                                                    for v in dmarc_request.rf.value:
                                                        dmarc_rf[v] += 1
                                                    dmarc_rf_valid['Pass'] += 1
                                                else:
                                                    # for v in dmarc_request.rf.value:
                                                    #     dmarc_rf[f"{v}*"] += 1
                                                    dmarc_rf_valid['Fail'] += 1
                                            else:
                                                dmarc_rf_explicit['Default'] += 1
                                            if dmarc_request.ri.explicit:
                                                dmarc_ri_explicit['Explicit'] += 1
                                                if dmarc_request.ri.valid:
                                                    dmarc_ri_dist[dmarc_request.ri.value] += 1
                                                    dmarc_ri_valid['Pass'] += 1
                                                else:
                                                    dmarc_ri_valid['Fail'] += 1
                                            else:
                                                dmarc_ri_explicit['Default'] += 1
                                            if dmarc_request.sp.explicit:
                                                dmarc_sp_explicit['Explicit'] += 1
                                                if dmarc_request.sp.valid:
                                                    dmarc_sp[dmarc_request.sp.value.value] += 1
                                                    dmarc_sp_valid['Pass'] += 1
                                                else:
                                                    dmarc_sp_valid['Fail'] += 1
                                            else:
                                                dmarc_sp_explicit['Default'] += 1
                                    if 'spf1' in answer['data'].lower() and not is_dmarc_name:
                                        dns_mail_config_perm[org_name]['SPF'] = True
                                        mail_auth_valid[org_name]['SPF'] = True
                        if 'type' in doc and doc['type'] == 'MX':
                            answer_count = len(answers)
                            if answer_count > 0 and is_org_domain:
                                for answer in answers:
                                    if 'type' in answer:
                                        if answer['type'] == 'MX':
                                            mx_dmarc_perm[org_name]['MX'] = True
                                            dns_mail_config_perm[org_name]['MX'] = True
                                            mail_auth_valid[org_name]['MX'] = True
                                            break

    valid_domain_count = len(domain_pass)

    with open('dmarc_report.md', mode='wt', encoding='utf-8') as fp:
        fp.write('# DMARC Report \n\n')
        fp.write(f"\nProcessed {document_counter:,} massdns result reports (ndjson lines). This is the baseline for all sum values below.")
        fp.write(f"\nNumber of domains: {valid_domain_count:,}")
        fp.write(f"\nReport time: {datetime.now():%Y-%m-%d %H:%M:%S%z}")

        for data_collection in data_collections:
            fp.write('\n\n')
            if 'DNS' in data_collection.title:
                data_collection.reference_sum = document_counter
            else:
                data_collection.reference_sum = valid_domain_count
            data_str = data_collection.dump()
            fp.write(data_str)


if __name__ == '__main__':
    start = time()
    log('Started execution.')
    main()
    print(f"\nProcessing time: {time() - start:.3f} s")
