import io
import zipfile
import xml.etree.cElementTree as ET
import xlrd.xlsx

from django.test import TestCase
from defusedxml.common import EntitiesForbidden


# https://en.wikipedia.org/wiki/Billion_laughs
BILLION_LAUGHS_XML = """\
<?xml version="1.0"?>
<!DOCTYPE lolz [
 <!ENTITY lol "lol">
 <!ELEMENT lolz (#PCDATA)>
 <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
 <!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
 <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
 <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
 <!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
 <!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;">
 <!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;">
 <!ENTITY lol8 "&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;">
 <!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">
]>
<lolz>&lol9;</lolz>"""


def build_zipfile(files):
    blob = io.BytesIO()
    zf = zipfile.ZipFile(blob, mode='w')
    for key, value in files.items():
        zf.writestr(key, value)
    zf.close()
    return blob.getvalue()


class BillionLaughsTests(TestCase):
    def test_xlrd_open_workbook_raises_entities_forbidden(self):
        with self.assertRaises(EntitiesForbidden):
            xlrd.open_workbook(file_contents=build_zipfile({
                'xl/_rels/workbook.xml.rels': BILLION_LAUGHS_XML,
                'xl/workbook.xml': BILLION_LAUGHS_XML
            }))

    def test_et_parse_raises_entities_forbidden(self):
        with self.assertRaises(EntitiesForbidden):
            ET.parse(io.StringIO(BILLION_LAUGHS_XML))
