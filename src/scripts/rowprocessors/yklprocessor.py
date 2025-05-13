from typing import Iterable
import re
import httpx
import json
import traceback as tb


from src.scripts.rowprocessors.baserowprocessor import BaseRowProcessor


class RowProcessor(BaseRowProcessor):
    """Processes rows to determine the YKL classification."""
    http_transport = httpx.HTTPTransport(retries=3)
    http_client = httpx.Client(transport=http_transport)
    fiction_check = r"^[1-9]{1}[.][0-9]{1,}"
    ykl_format_check = r"^([0-9]{2}[.][0-9]{1,}|[0-9]{2})$"
    no_high_level_ykl_format_check = r"^[0-9]{2}[.][0-9]{1,}$"

    jsonfile = open('hklj_automap.json', 'r')
    finto_lookup = json.load(jsonfile)

    def __init__(self, outfile, dialect):
        super().__init__(outfile, dialect)

    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)

    def processkeys(self, param):
        if (tuple(param) != ("bib_number", "record_id", "bib_best_title", "bib_best_author", "isbn",
                             "espoo_item_count", "helsinki_item_count", "kauniainen_item_count", "vantaa_item_count",
                             "subject_classification", "ykl",
                             "vantaa_classification", "kauniainen_classification", "espoo_classification", "helsinki_classification", "raw_data")):
            raise ValueError("Incompatible keys.")
        else:
            super().processkeys(
                ("bib_number", "record_id", "bib_best_title", "bib_best_author", "isbn",
                 "espoo_item_count", "helsinki_item_count", "kauniainen_item_count", "vantaa_item_count",
                 "subject_classification", "ykl_084",
                 "vantaa_classification", "kauniainen_classification", "espoo_classification", "helsinki_classification",
                 "ykl", "heuristic_result"
                 )
            )

    def processed(self, param):
        super().processed(param)

    @classmethod
    def clean_classification(cls, cfn):
        if cfn is not None:
            cfn_clean = re.sub(r'[^0-9.]', '', cfn)
            if cfn_clean != '':
                return cfn_clean
        return ""

    @classmethod
    def rowprocessingworker(cls, param):
        return cls.determine_ykl(
            param[0], param[1], param[2], param[3], param[4], param[5],
            param[6], param[7], param[8], param[9],
            param[10], param[11], param[12], param[13], param[14], param[15].replace('\t', ' '))

    @classmethod
    def determine_ykl(
            cls, bib_number, record_id, bib_best_title, bib_best_author, isbn,
            espoo_item_count, helsinki_item_count, kauniainen_item_count, vantaa_item_count,
            subject_cfn, ykl_084, vantaa_cfn, kauniainen_cfn, espoo_cfn, helsinki_cfn, raw_data
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
                return (
                    bib_number, record_id, bib_best_title, bib_best_author, isbn,
                    espoo_item_count, helsinki_item_count, kauniainen_item_count, vantaa_item_count,
                    subject_cfn, ykl_084, vantaa_cfn, kauniainen_cfn, espoo_cfn, helsinki_cfn,
                    match[0], heuristic_result + "084_ykl")
        elif is_mixed:
            heuristic_result = "mixed_"
            match = re.match(cls.ykl_format_check, "" if ykl_084 is None else cls.clean_classification(ykl_084))
            if match is not None:
                return (
                    bib_number, record_id, bib_best_title, bib_best_author, isbn,
                    espoo_item_count, helsinki_item_count, kauniainen_item_count, vantaa_item_count,
                    subject_cfn, ykl_084, vantaa_cfn, kauniainen_cfn, espoo_cfn, helsinki_cfn,
                    match[0], heuristic_result + "084_ykl")
        else:
            heuristic_result = "non-fiction_"
            try:
                match = re.match(cls.ykl_format_check, cls.clean_classification(vantaa_cfn))
                if match is not None:
                    return (bib_number, record_id, bib_best_title, bib_best_author, isbn,
                            espoo_item_count, helsinki_item_count, kauniainen_item_count, vantaa_item_count,
                            subject_cfn, ykl_084, vantaa_cfn, kauniainen_cfn, espoo_cfn, helsinki_cfn,
                            match[0], heuristic_result + "vantaa_cfn")
            except Exception:
                pass
            try:
                match = re.match(cls.ykl_format_check, cls.clean_classification(espoo_cfn))
                if match is not None:
                    return (bib_number, record_id, bib_best_title, bib_best_author, isbn,
                            espoo_item_count, helsinki_item_count, kauniainen_item_count, vantaa_item_count,
                            subject_cfn, ykl_084, vantaa_cfn, kauniainen_cfn, espoo_cfn, helsinki_cfn,
                            match[0], heuristic_result + "espoo_cfn")
            except Exception:
                pass
            try:
                match = re.match(cls.ykl_format_check, cls.clean_classification(kauniainen_cfn))
                if match is not None:
                    return (bib_number, record_id, bib_best_title, bib_best_author, isbn,
                            espoo_item_count, helsinki_item_count, kauniainen_item_count, vantaa_item_count,
                            subject_cfn, ykl_084, vantaa_cfn, kauniainen_cfn, espoo_cfn, helsinki_cfn,
                            match[0], heuristic_result + "kauniainen_cfn")
            except Exception:
                pass
            try:
                match = re.match(cls.no_high_level_ykl_format_check, cls.clean_classification(ykl_084))
                if match is not None:
                    return (bib_number, record_id, bib_best_title, bib_best_author, isbn,
                            espoo_item_count, helsinki_item_count, kauniainen_item_count, vantaa_item_count,
                            subject_cfn, ykl_084, vantaa_cfn, kauniainen_cfn, espoo_cfn, helsinki_cfn,
                            match[0], heuristic_result + "084_ykl")
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
                    return (bib_number, record_id, bib_best_title, bib_best_author, isbn,
                            espoo_item_count, helsinki_item_count, kauniainen_item_count, vantaa_item_count,
                            subject_cfn, ykl_084, vantaa_cfn, kauniainen_cfn, espoo_cfn, helsinki_cfn,
                            cfn, heuristic_result + "finna_isbn")
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
                    return (bib_number, record_id, bib_best_title, bib_best_author, isbn,
                            espoo_item_count, helsinki_item_count, kauniainen_item_count, vantaa_item_count,
                            subject_cfn, ykl_084, vantaa_cfn, kauniainen_cfn, espoo_cfn, helsinki_cfn,
                            cfn, heuristic_result + "finna_title")
        except Exception:
            pass

        try:
            if helsinki_cfn is not None:
                helsinki_cfn_clean = cls.clean_classification(helsinki_cfn)
                if cls.finto_lookup.get(helsinki_cfn_clean) is not None:
                    if len(cls.finto_lookup.get(helsinki_cfn_clean)["narrow"]) == 1:
                        cfn = cls.finto_lookup.get(helsinki_cfn_clean)["narrow"][0]
                        return (bib_number, record_id, bib_best_title, bib_best_author, isbn,
                                espoo_item_count, helsinki_item_count, kauniainen_item_count, vantaa_item_count,
                                subject_cfn, ykl_084, vantaa_cfn, kauniainen_cfn, espoo_cfn, helsinki_cfn,
                                cfn, heuristic_result + "finto_narrow_1_1")
        except Exception:
            pass

        try:
            if raw_data is not None:

                helsinki_cfn_clean = cls.clean_classification(helsinki_cfn)

                finto_narrow_ykls = []
                finto_wide_ykls = []
                if cls.finto_lookup.get(helsinki_cfn_clean) is not None:

                    finto_narrow_ykls = cls.finto_lookup.get(helsinki_cfn_clean)["narrow"]
                    if finto_narrow_ykls is None:
                        finto_narrow_ykls = []

                    finto_wide_ykls = cls.finto_lookup.get(helsinki_cfn_clean)["wide"]
                    if finto_wide_ykls is None:
                        finto_wide_ykls = []

                annif_results = cls.http_client.post(
                    'http://localhost:5000/v1/projects/omikuji-parabel-en/suggest', data={'text': raw_data}
                ).json()

                cfn = None

                if len(finto_narrow_ykls) > 0:
                    annif_rank = 0
                    cfn_result = ""
                    for result in annif_results['results']:
                        annif_rank += 1
                        if result['notation'] in finto_narrow_ykls:
                            cfn = result['notation']
                            # cfn_result = f"annif_rank_{annif_rank}_narrow_finto_match"
                            cfn_result = "annif_narrow_finto_match"
                            break
                    if cfn_result != "":
                        return (bib_number, record_id, bib_best_title, bib_best_author, isbn,
                                espoo_item_count, helsinki_item_count, kauniainen_item_count, vantaa_item_count,
                                subject_cfn, ykl_084, vantaa_cfn, kauniainen_cfn, espoo_cfn, helsinki_cfn,
                                cfn, heuristic_result + cfn_result)

                annif_rank = 0
                if len(finto_wide_ykls) == 0:
                    cfn_result = "annif_no_hklj_finto_match"
                elif len(finto_wide_ykls) > 0:
                    cfn_result = "annif_no_cfn_finto_match"
                    for result in annif_results['results']:
                        annif_rank += 1
                        if result['notation'] in finto_wide_ykls:
                            cfn = result['notation']
                            # cfn_result = f"annif_rank_{annif_rank}_wide_finto_match"
                            cfn_result = "annif_wide_finto_match"
                            break

                if cfn is None:
                    if len(annif_results['results']) > 0:
                        cfn = annif_results['results'][0]['notation']
                if cfn is not None:
                    return (bib_number, record_id, bib_best_title, bib_best_author, isbn,
                            espoo_item_count, helsinki_item_count, kauniainen_item_count, vantaa_item_count,
                            subject_cfn, ykl_084, vantaa_cfn, kauniainen_cfn, espoo_cfn, helsinki_cfn,
                            cfn, heuristic_result + cfn_result)
        except Exception:
            pass

        return (bib_number, record_id, bib_best_title, bib_best_author, isbn,
                espoo_item_count, helsinki_item_count, kauniainen_item_count, vantaa_item_count,
                subject_cfn, ykl_084, vantaa_cfn, kauniainen_cfn, espoo_cfn, helsinki_cfn,
                ykl_084, heuristic_result + "no_match")

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
