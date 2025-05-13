from typing import Iterable
import re
import httpx
import json

from src.scripts.rowprocessors.baserowprocessor import BaseRowProcessor


class RowProcessor(BaseRowProcessor):
    """Processes rows to determine the YKL classification."""
    http_transport = httpx.HTTPTransport(retries=3)
    http_client = httpx.Client(transport=http_transport)
    fiction_check = r"^[1-9]{1}[.][0-9]{1,}"
    ykl_format_check = r"^([0-9]{2}[.][0-9]{1,}|[0-9]{2})$"
    jsonfile = open('hklj_automap.json', 'r')
    finto_lookup = json.load(jsonfile)

    def __init__(self, outfile, dialect):
        super().__init__(outfile, dialect)

    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)

    def processkeys(self, param):
        if (tuple(param) != ("bib_number", "bib_record_id", "bib_best_title", "bib_best_author", "isbn",
                             "ykl", "subject_classification",
                             "vantaa_classification", "kauniainen_classification", "espoo_classification", "helsinki_classification", "raw_data")):
            raise ValueError("Incompatible keys.")
        else:
            pass
            # do not write keys

    def processed(self, param):
        self.pool_queue.release()
        try:
            result = param.result()
            if result[2] == "save":
                self.outcsv.writerow((result[0], result[1]))
        except Exception as e:
            print(e)

    @classmethod
    def rowprocessingworker(cls, param):
        return cls.determine_ykl(
            param[0], param[1], param[2], param[3], param[4], param[5], param[6],
            param[7], param[8], param[9], param[10], param[11].replace('\t', ' '))

    @classmethod
    def determine_ykl(
            cls, bib_number, bib_record_id, bib_best_title, bib_best_author, isbn,
            ykl_084, subject_cfn, vantaa_cfn, kauniainen_cfn, espoo_cfn, helsinki_cfn, raw_data
            ) -> Iterable:

        vantaa_cfn_is_fiction = re.match(cls.fiction_check, vantaa_cfn) is not None
        kauniainen_cfn_is_fiction = re.match(cls.fiction_check, kauniainen_cfn) is not None
        espoo_cfn_is_fiction = re.match(cls.fiction_check, espoo_cfn) is not None
        helsinki_cfn_is_fiction = re.match(cls.fiction_check, helsinki_cfn) is not None

        is_fiction = (
            (vantaa_cfn is None or vantaa_cfn == "" or vantaa_cfn_is_fiction) and
            (kauniainen_cfn is None or kauniainen_cfn == "" or kauniainen_cfn_is_fiction) and
            (espoo_cfn is None or espoo_cfn == "" or espoo_cfn_is_fiction) and
            (helsinki_cfn is None or helsinki_cfn == "" or helsinki_cfn_is_fiction)
        )
        is_mixed = (
            (
                vantaa_cfn_is_fiction or
                kauniainen_cfn_is_fiction or
                espoo_cfn_is_fiction or
                helsinki_cfn_is_fiction
            ) and not is_fiction
        )

        heuristic_result = ""
        if is_fiction:
            heuristic_result = "fiction_"
            match = re.match(cls.ykl_format_check, "" if ykl_084 is None else cls.clean_classification(ykl_084))
            if match is not None:
                return (raw_data, f"<http://urn.fi/URN:NBN:fi:au:ykl:{cls.strip_form_class(match[0])}>", "save")
        elif is_mixed:
            heuristic_result = "mixed_"
            match = re.match(cls.ykl_format_check, "" if ykl_084 is None else cls.clean_classification(ykl_084))
            if match is not None:
                return (
                    bib_number, bib_record_id, bib_best_title, bib_best_author, isbn,
                    subject_cfn, ykl_084, vantaa_cfn, kauniainen_cfn, espoo_cfn, helsinki_cfn,
                    match[0], heuristic_result + "save")
        else:
            heuristic_result = "non-fiction_"
            try:
                match = re.match(cls.ykl_format_check, cls.clean_classification(vantaa_cfn))
                if match is not None:
                    return (raw_data, f"<http://urn.fi/URN:NBN:fi:au:ykl:{cls.strip_form_class(match[0])}>", "save")
            except Exception:
                pass
            try:
                match = re.match(cls.ykl_format_check, cls.clean_classification(espoo_cfn))
                if match is not None:
                    return (raw_data, f"<http://urn.fi/URN:NBN:fi:au:ykl:{cls.strip_form_class(match[0])}>", "save")
            except Exception:
                pass
            try:
                match = re.match(cls.ykl_format_check, cls.clean_classification(kauniainen_cfn))
                if match is not None:
                    return (raw_data, f"<http://urn.fi/URN:NBN:fi:au:ykl:{cls.strip_form_class(match[0])}>", "save")
            except Exception:
                pass
            try:
                match = re.match(cls.ykl_format_check, cls.clean_classification(ykl_084))
                if match is not None:
                    return (raw_data, f"<http://urn.fi/URN:NBN:fi:au:ykl:{cls.strip_form_class(match[0])}>", "save")
            except Exception:
                pass

        try:
            if isbn is not None:
                # try to find classification from Finna based on ISBN
                finna_result = cls.http_client.get(
                    'https://api.finna.fi/api/v1/search?lookfor={isbn}&field%5B%5D=classifications'.format(
                        isbn=isbn)
                ).json()
                cfn = cls.cfn_from_finna_result(finna_result)
                if cfn:
                    return (raw_data, f"<http://urn.fi/URN:NBN:fi:au:ykl:{cls.strip_form_class(cfn)}>", "save")
        except Exception:
            pass

        try:
            if bib_best_title is not None:
                # try to find classification from Finna based on title
                finna_result = cls.http_client.get(
                    'https://api.finna.fi/api/v1/search?lookfor={bib_best_title}&field%5B%5D=classifications'.format(
                        bib_best_title=bib_best_title)
                ).json()
                cfn = cls.cfn_from_finna_result(finna_result)
                if cfn:
                    return (raw_data, f"<http://urn.fi/URN:NBN:fi:au:ykl:{cls.strip_form_class(cfn)}>", "save")
        except Exception:
            pass

        try:
            if helsinki_cfn is not None:
                helsinki_cfn_clean = cls.clean_classification(helsinki_cfn)
                if cls.finto_lookup.get(helsinki_cfn_clean) is not None:
                    if len(cls.finto_lookup.get(helsinki_cfn_clean)["narrow"]) == 1:
                        cfn = cls.finto_lookup.get(helsinki_cfn_clean)["narrow"][0]
                        return (raw_data, f"<http://urn.fi/URN:NBN:fi:au:ykl:{cls.strip_form_class(cfn)}>", "save")
        except Exception:
            pass

        return (bib_best_title, ykl_084, "skip")

    @classmethod
    def clean_classification(cls, cfn):
        if cfn is not None:
            cfn_clean = re.sub(r'[^0-9.]', '', cfn)
            if cfn_clean != '':
                return cfn_clean
        return ""


    """
    @classmethod
    def determine_ykl(
            cls, bib_number, bib_record_id, bib_best_title, bib_best_author, isbn,
            ykl_084, subject_cfn, vantaa_cfn, kauniainen_cfn, espoo_cfn, helsinki_cfn, raw_data
            ) -> Iterable:

        is_fiction = (
            (re.match(cls.fiction_check, "" if vantaa_cfn is None else vantaa_cfn) is not None) or
            (re.match(cls.fiction_check, "" if kauniainen_cfn is None else kauniainen_cfn) is not None) or
            (re.match(cls.fiction_check, "" if espoo_cfn is None else espoo_cfn) is not None) or
            (re.match(cls.fiction_check, "" if helsinki_cfn is None else helsinki_cfn) is not None)
        )
        if is_fiction:
            match = re.match(cls.ykl_format_check, "" if ykl_084 is None else ykl_084)
            if match is not None:
                return (raw_data, f"<http://urn.fi/URN:NBN:fi:au:ykl:{cls.strip_form_class(match[0])}>", "save")
        else:
            try:
                match = re.match(cls.ykl_format_check, vantaa_cfn)
                if match is not None:
                    return (raw_data, f"<http://urn.fi/URN:NBN:fi:au:ykl:{cls.strip_form_class(match[0])}>", "save")
            except Exception:
                pass
            try:
                match = re.match(cls.ykl_format_check, espoo_cfn)
                if match is not None:
                    return (raw_data, f"<http://urn.fi/URN:NBN:fi:au:ykl:{cls.strip_form_class(match[0])}>", "save")
            except Exception:
                pass
            try:
                match = re.match(cls.ykl_format_check, kauniainen_cfn)
                if match is not None:
                    return (raw_data, f"<http://urn.fi/URN:NBN:fi:au:ykl:{cls.strip_form_class(match[0])}>", "save")
            except Exception:
                pass
            try:
                match = re.match(cls.ykl_format_check, ykl_084)
                if match is not None:
                    return (raw_data, f"<http://urn.fi/URN:NBN:fi:au:ykl:{cls.strip_form_class(match[0])}>", "save")
            except Exception:
                pass

        try:
            if isbn is not None:
                # try to find classification from Finna based on ISBN
                finna_result = cls.http_client.get(
                    'https://api.finna.fi/api/v1/search?lookfor={isbn}&field%5B%5D=classifications'.format(
                        isbn=isbn)
                ).json()
                cfn = cls.cfn_from_finna_result(finna_result)
                if cfn:
                    return (raw_data, f"<http://urn.fi/URN:NBN:fi:au:ykl:{cls.strip_form_class(cfn)}>", "save")
        except Exception:
            pass

        try:
            if bib_best_title is not None:
                # try to find classification from Finna based on title
                finna_result = cls.http_client.get(
                    'https://api.finna.fi/api/v1/search?lookfor={bib_best_title}&field%5B%5D=classifications'.format(
                        bib_best_title=bib_best_title)
                ).json()
                cfn = cls.cfn_from_finna_result(finna_result)
                if cfn:
                    return (raw_data, f"<http://urn.fi/URN:NBN:fi:au:ykl:{cls.strip_form_class(cfn)}>", "save")
        except Exception:
            pass

        return (bib_best_title, ykl_084, "skip")
      """

    @classmethod
    def strip_form_class(cls, cfn):
        """Strips the form from the classification number."""
        if cfn is not None:
            match = re.match(r"^([0-9]+[.][1-9]+)", cfn)
            if match is not None:
                return match[0]
        return None

    @classmethod
    def cfn_from_finna_result(cls, finna_result):
        finna_isbn_ykls = {}
        if finna_result["records"] is not None:
            for record in finna_result["records"]:
                if record["classifications"] is not None:
                    if record["classifications"]["ykl"] is not None:
                        for classfication in record["classifications"]["ykl"]:
                            match = re.match(cls.ykl_format_check, classfication)
                            if match is not None:
                                if match[0] in finna_isbn_ykls:
                                    finna_isbn_ykls[match[0]] = finna_isbn_ykls[match[0]] + 10
                                else:
                                    finna_isbn_ykls[match[0]] = 10
        if finna_isbn_ykls:
            count = {}
            for cfn1 in finna_isbn_ykls.keys():
                for cfn2 in finna_isbn_ykls.keys():
                    if cfn1[0:1] == cfn2[0:1]:
                        if cfn1[0:1] in count:
                            count[cfn1[0:1]] += 1
                        else:
                            count[cfn1[0:1]] = 1
            for c in count.keys():
                for cfn in finna_isbn_ykls:
                    if cfn[0:1] == c:
                        finna_isbn_ykls[cfn] += count[c]
            return max(finna_isbn_ykls, key=lambda key: finna_isbn_ykls[key])
        else:
            return None
