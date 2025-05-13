import regex
import uroman as ur
from typing import Iterable

from src.scripts.rowprocessors.baserowprocessor import BaseRowProcessor


class RowProcessor(BaseRowProcessor):
    """Processes rows to determine the pääsana."""

    uroman = ur.Uroman()

    def __init__(self, outfile, dialect):
        super().__init__(outfile, dialect)

    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)

    def processkeys(self, param):
        if (tuple(param) != ("bib_number", "bib_record_id", "bib_best_title", "bib_best_author", "json")):
            raise ValueError("Incompatible keys.")
        else:
            return ("bib_number", "bib_record_id", "bib_best_title", "bib_best_author", "pääsana")

    def processed(self, param):
        self.pool_queue.release()
        try:
            result = param.result()
            self.outcsv.writerow((result[0], result[1], result[2], result[3], result[4]))
        except Exception as e:
            print(e)

    @classmethod
    def rowprocessingworker(cls, param):
        return cls.determine_paasana(param[0], param[1], param[2], param[3], param[4])

    @classmethod
    def determine_paasana(cls, bib_number, bib_record_id, bib_best_title, bib_best_author, fields) -> Iterable:
        try:
            for field in fields:
                if field["marc_tag"] == "100" and field["tag"] == "a" and field["marc_ind1"] == "1":
                    try:
                        return (bib_number, bib_record_id, bib_best_title, bib_best_author, cls.signumize(field["content"], 0))
                    except Exception:
                        pass
            for field in fields:
                if field["marc_tag"] == "110" and field["tag"] == "a" and field["marc_ind1"] == "2":
                    try:
                        return (bib_number, bib_record_id, bib_best_title, bib_best_author, cls.signumize(field["content"], 0))
                    except Exception:
                        pass
            for field in fields:
                if field["marc_tag"] == "100" and field["tag"] == "a" and field["marc_ind1"] == "0":
                    try:
                        return (bib_number, bib_record_id, bib_best_title, bib_best_author, cls.signumize(field["content"], 0))
                    except Exception:
                        pass
            for field in fields:
                if field["marc_tag"] == "100" and field["tag"] == "a" and field["marc_ind1"] == "2":
                    try:
                        return (bib_number, bib_record_id, bib_best_title, bib_best_author, cls.signumize(field["content"], 0))
                    except Exception:
                        pass
            for field in fields:
                if field["marc_tag"] == "110" and field["tag"] == "a" and field["marc_ind1"] == "1":
                    try:
                        return (bib_number, bib_record_id, bib_best_title, bib_best_author, cls.signumize(field["content"], 0))
                    except Exception:
                        pass
            for field in fields:
                if field["marc_tag"] == "110" and field["tag"] == "a" and field["marc_ind1"] == "0":
                    try:
                        return (bib_number, bib_record_id, bib_best_title, bib_best_author, cls.signumize(field["content"], 0))
                    except Exception:
                        pass

            for field in fields:
                if field["marc_tag"] == "100" and field["tag"] == "a" and field["marc_ind1"] == "3":
                    try:
                        return (bib_number, bib_record_id, bib_best_title, bib_best_author, cls.signumize(field["content"], 0))
                    except Exception:
                        pass
            for field in fields:
                if field["marc_tag"] == "111" and field["tag"] == "a" and field["marc_ind1"] == "0":
                    try:
                        return (bib_number, bib_record_id, bib_best_title, bib_best_author, cls.signumize(field["content"], 0))
                    except Exception:
                        pass

            for field in fields:
                if field["marc_tag"] == "111" and field["tag"] == "a" and field["marc_ind1"] == "1":
                    try:
                        return (bib_number, bib_record_id, bib_best_title, bib_best_author, cls.signumize(field["content"], 0))
                    except Exception:
                        pass
            for field in fields:
                if field["marc_tag"] == "111" and field["tag"] == "a" and field["marc_ind1"] == "2":
                    try:
                        return (bib_number, bib_record_id, bib_best_title, bib_best_author, cls.signumize(field["content"], 0))
                    except Exception:
                        pass
            for field in fields:
                if field["marc_tag"] == "245" and field["tag"] == "a" and field["marc_ind1"] == "0":
                    try:
                        skip = int(field["marc_ind2"])
                        return (bib_number, bib_record_id, bib_best_title, bib_best_author, cls.signumize(field["content"], skip))
                    except Exception:
                        pass
            for field in fields:
                if field["marc_tag"] == "245" and field["tag"] == "a" and field["marc_ind1"] == "1":
                    try:
                        skip = int(field["marc_ind2"])
                        return (bib_number, bib_record_id, bib_best_title, bib_best_author, cls.signumize(field["content"], skip))
                    except Exception:
                        pass
            for field in fields:
                if field["marc_tag"] == "245" and field["tag"] == "a":
                    try:
                        skip = int(field["marc_ind2"])
                        return (bib_number, bib_record_id, bib_best_title, bib_best_author, cls.signumize(field["content"], skip))
                    except Exception:
                        pass
            for field in fields:
                if field["marc_tag"] == "245" and field["tag"] == "a":
                    try:
                        return (bib_number, bib_record_id, bib_best_title, bib_best_author, cls.signumize(field["content"], 0))
                    except Exception:
                        pass

            """
            for field in fields:
                if field["marc_tag"] == "130" and field["tag"] == "a":
                    try:
                        skip = int(field["marc_ind1"])
                        return (bib_number, bib_record_id, bib_best_title, bib_best_author, cls.signumize(field["content"], skip))
                    except Exception:
                        pass
            """
        except Exception:
            pass

        return (bib_number, bib_record_id, bib_best_title, bib_best_author, "-*-")

    @classmethod
    def signumize(cls, content, skip=0):
        cleaned = regex.sub(r'[^\p{Latin}0-9]', '', content[skip:len(content)]).capitalize()
        if len(cleaned) == 0:
            cleaned = regex.sub(r'[^\p{Latin}0-9]', '', str(cls.uroman.romanize_string(s=content[skip:len(content)], rom_format=ur.RomFormat.STR))).capitalize()
            if len(cleaned) == 0:
                raise AttributeError("Signum is empty.")
        return cleaned[0: 3 if len(cleaned) >= 3 else len(cleaned)]
