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
    ykl_format_check = r"^[0-9]{2}[.][0-9]{1,}"

    try:
        with open('hklj_ykl_mapping.json', 'r') as file:
            hklj_ykl_mapping = json.load(file)
    except Exception as e:
        hklj_ykl_mapping = {}
        print("HKLJ YKL mapping file load failed.")
        print(e)
        pass

    def __init__(self, outfile, dialect):
        self.hklj_ykl_matches = {}
        super().__init__(outfile, dialect)

    def __exit__(self, exc_type, exc_value, traceback):
        with open('hklj_ykl_mapping.json', 'w') as file:
            for hklj in self.hklj_ykl_matches.keys():
                self.hklj_ykl_matches[hklj] = max(self.hklj_ykl_matches[hklj], key=lambda key: self.hklj_ykl_matches[hklj][key])
            json.dump(self.hklj_ykl_matches, file)
        super().__exit__(exc_type, exc_value, traceback)

    def processkeys(self, param):
        if (tuple(param) != ("bib_number", "record_id", "bib_best_title", "bib_best_author", "isbn", "item_count",
                             "subject_classification", "ykl",
                             "vantaa_classification", "kauniainen_classification", "espoo_classification", "helsinki_classification")):
            raise ValueError("Incompatible keys.")
        else:
            super().processkeys(
                ("bib_number", "record_id", "bib_best_title", "bib_best_author", "isbn", "item_count",
                 "subject_classification", "ykl_084",
                 "vantaa_classification", "kauniainen_classification", "espoo_classification", "helsinki_classification",
                 "ykl", "heuristic_result"
                 )
            )

    def processed(self, param):
        result = param.result()
        hklj = result[11]
        ykl = result[12]
        if hklj is not None and ykl is not None:
            if re.match(self.__class__.ykl_format_check, ykl) is not None:
                self.add_to_mapping(hklj.strip(), ykl)
        super().processed(param)

    def add_to_mapping(self, hklj, ykl):
        if hklj is not None and ykl is not None:
            if hklj in self.hklj_ykl_matches:
                if ykl in self.hklj_ykl_matches[hklj]:
                    self.hklj_ykl_matches[hklj][ykl] += 1
                else:
                    self.hklj_ykl_matches[hklj][ykl] = 1
            else:
                self.hklj_ykl_matches[hklj] = {}
                self.hklj_ykl_matches[hklj][ykl] = 1

    @classmethod
    def rowprocessingworker(cls, param):
        return cls.determine_ykl(
            param[0], param[1], param[2], param[3], param[4], param[5], param[6],
            param[7], param[8], param[9], param[10], param[11])

    @classmethod
    def determine_ykl(
            cls, bib_number, record_id, bib_best_title, bib_best_author, isbn, item_count,
            subject_cfn, ykl_084, vantaa_cfn, kauniainen_cfn, espoo_cfn, helsinki_cfn
            ) -> Iterable:

        is_fiction = (
            (re.match(cls.fiction_check, "" if vantaa_cfn is None else vantaa_cfn) is not None) or
            (re.match(cls.fiction_check, "" if kauniainen_cfn is None else kauniainen_cfn) is not None) or
            (re.match(cls.fiction_check, "" if espoo_cfn is None else espoo_cfn) is not None) or
            (re.match(cls.fiction_check, "" if helsinki_cfn is None else helsinki_cfn) is not None)
        )
        heuristic_result = ""
        if is_fiction:
            heuristic_result = "fiction_"
            match = re.match(cls.ykl_format_check, "" if ykl_084 is None else ykl_084)
            if match is not None:
                return (
                    bib_number, record_id, bib_best_title, bib_best_author, isbn, item_count,
                    subject_cfn, ykl_084, vantaa_cfn, kauniainen_cfn, espoo_cfn, helsinki_cfn,
                    match[0], heuristic_result + "084_ykl")
        else:
            heuristic_result = "non-fiction_"
            try:
                match = re.match(cls.ykl_format_check, vantaa_cfn)
                if match is not None:
                    return (bib_number, record_id, bib_best_title, bib_best_author, isbn, item_count,
                            subject_cfn, ykl_084, vantaa_cfn, kauniainen_cfn, espoo_cfn, helsinki_cfn,
                            match[0], heuristic_result + "vantaa_cfn")
            except Exception:
                pass
            try:
                match = re.match(cls.ykl_format_check, espoo_cfn)
                if match is not None:
                    return (bib_number, record_id, bib_best_title, bib_best_author, isbn, item_count,
                            subject_cfn, ykl_084, vantaa_cfn, kauniainen_cfn, espoo_cfn, helsinki_cfn,
                            match[0], heuristic_result + "espoo_cfn")
            except Exception:
                pass
            try:
                match = re.match(cls.ykl_format_check, kauniainen_cfn)
                if match is not None:
                    return (bib_number, record_id, bib_best_title, bib_best_author, isbn, item_count,
                            subject_cfn, ykl_084, vantaa_cfn, kauniainen_cfn, espoo_cfn, helsinki_cfn,
                            match[0], heuristic_result + "kauniainen_cfn")
            except Exception:
                pass
            try:
                match = re.match(cls.ykl_format_check, ykl_084)
                if match is not None:
                    return (bib_number, record_id, bib_best_title, bib_best_author, isbn, item_count,
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
                    return (bib_number, record_id, bib_best_title, bib_best_author, isbn, item_count,
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
                    return (bib_number, record_id, bib_best_title, bib_best_author, isbn, item_count,
                            subject_cfn, ykl_084, vantaa_cfn, kauniainen_cfn, espoo_cfn, helsinki_cfn,
                            cfn, heuristic_result + "finna_title")
        except Exception:
            pass

        try:
            if helsinki_cfn is not None:
                if cls.hklj_ykl_mapping[helsinki_cfn.strip()] is not None:
                    return (bib_number, record_id, bib_best_title, bib_best_author, isbn, item_count,
                            subject_cfn, ykl_084, vantaa_cfn, kauniainen_cfn, espoo_cfn, helsinki_cfn,
                            cls.hklj_ykl_mapping[helsinki_cfn.strip()], heuristic_result + "most_popular_ykl")
        except Exception as e:
            print(e)
            pass

        return (bib_number, record_id, bib_best_title, bib_best_author, isbn, item_count,
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
