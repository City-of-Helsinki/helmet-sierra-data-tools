import re
import json
import httpx
import urllib.parse
from src.scripts.rowprocessors.baserowprocessor import BaseRowProcessor


class RowProcessor(BaseRowProcessor):

    http_transport = httpx.HTTPTransport(retries=3)
    http_client = httpx.Client(transport=http_transport)

    fiction_check = r"^[1-9]{1}[.][0-9]{1,}"

    def __init__(self, outfile, dialect):
        super().__init__(outfile, dialect)

    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)

    def processkeys(self, param):
        if (tuple(param) != ("hklj",)):
            raise ValueError("Incompatible keys.")
        else:
            pass
            # do not write keys

    @classmethod
    def rowprocessingworker(cls, param):
        helsinki_cfn = param[0]
        helsinki_cfn_clean = re.sub(r'[^0-9.]', '', helsinki_cfn)
        is_fiction = (
            (re.match(cls.fiction_check, "" if helsinki_cfn is None else helsinki_cfn) is not None)
        )

        finto_ykls_narrow = cls.get_related(f"{'f' if is_fiction else ''}{helsinki_cfn_clean}", False)
        finto_ykls_broad = cls.get_related(f"{'f' if is_fiction else ''}{helsinki_cfn_clean}", True)

        return (helsinki_cfn, finto_ykls_narrow, finto_ykls_broad)

    def processed(self, param):
        self.pool_queue.release()
        try:
            result = param.result()
            self.outcsv.writerow(result)
        except Exception as e:
            print(e)

    @classmethod
    def get_related(cls, hklj_to_match, traverse):
        finto_ykls = []

        while len(hklj_to_match) != 0 and len(finto_ykls) == 0:
            try:
                hklj_uri = urllib.parse.quote_plus(f'http://urn.fi/URN:NBN:fi:au:hklj:{hklj_to_match}')
                finto_uri = f'https://api.finto.fi/rest/v1/hklj/mappings?uri={hklj_uri}&external=true&lang=fi&clang=fi'

                finto_result = cls.http_client.get(finto_uri)
                finto_json = finto_result.json()
                cfn_finto_ykls = []

                for mapping in finto_json['mappings']:
                    if mapping['toScheme']['uri'] == 'http://urn.fi/URN:NBN:fi:au:ykl:':
                        cfn_finto_ykls.append(mapping['notation'])

                finto_ykls.extend(cfn_finto_ykls)

                for node in json.loads(finto_json["graph"])["graph"]:
                    if traverse is True:
                        finto_ykls.extend(cls.get_related(node["uri"].replace("hklj:", ""), False))

            except Exception:
                pass

            hklj_to_match = hklj_to_match[0:len(hklj_to_match) - 1]

        return list(set([x for x in finto_ykls if x is not None]))
