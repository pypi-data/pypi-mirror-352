from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg
import re as _re

class SloveneNormalizer(NormalizerBase):
    NAME = "slovene_normalizer"

    DESCRIPTION_TRAINING = """
        Apply the slovene normalizer process to the target
    """

    DESCRIPTION_DECODING = """
        Apply the slovene normalizer process to tgt if tgt_lang is slovene, do nothing
        otherwise.
    """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        if tgt_lang != "sl":
            raise Warning("SloveneNormalizer processor requires Slovene")
        else:
            super().__init__(src_lang, tgt_lang)

    def process_train(self, seg: Seg) -> None:
        if self.tgt_lang == "sl":
            seg.tgt = self.normalize(seg.tgt)

    def process_src_decoding(self, seg: Seg) -> None:
        pass

    def process_tgt_decoding(self, seg: Seg) -> None:
        if self.tgt_lang == "sl":
            seg.tgt = self.normalize(seg.tgt)

    def normalize(self, txt: str) -> str:
        """
        Set the dot as thousand separator on numbers larger than 9999
        """
        numbers = []
        numbers = _re.findall(r"(\d{5,})", txt)
        if numbers != []:
            for number in numbers:
                new = str('{:,}'.format(int(number))).replace(',', '.')
                txt = _re.sub(number, new, txt)
        """
        Set the dot as thousand separator on numbers separated by space
        """
        txt = _re.sub(r"(\s\d{2,3})( )(\d{3})(\b|\Z)", r"\1.\3\4", txt)
        """
        Delete the word minute if it is followed by a number with format hh:mm,ss
        """
        txt = _re.sub(r"(\d+:\d+,\d+)( )?minute(\b|\Z)", r"\1\3", txt)
        """
        Substitute the SI units with the correct format, for example: 1Ghz -> 1 GHz
        """
        txt = _re.sub(r"(\d+)( )?(da|[QRYZEPTGMhdcmµnpfazyrq])hz", r"\1 \3Hz", txt)
        txt = _re.sub(r"(\d+)( )?(da|[QRYZEPTGMhdcmµnpfazyrq])pa", r"\1 \3Pa", txt)
        txt = _re.sub(r"(\d+)( )?(da|[QRYZEPTGMhdcmµnpfazyrq])wh", r"\1 \3Wh", txt)
        txt = _re.sub(r"(\d+)( )?(da|[QRYZEPTGMhdcmµnpfazyrq])ah", r"\1 \3Ah", txt)
        """
        Substitute the mile with the correct format, for example: 1mi -> 1 milj
        """
        txt = _re.sub(r"(\d+)( )?mi(\b|\Z)", r"\1 milj\3", txt)
        """
        Establish a space between the number and the unit, for example: 1mm -> 1 mm
        """
        txt = _re.sub(r"(\d+)((da|[QRYZEPTGMkhdcmµnpfazyrq])?([shmlgVAKJWNFTHCR]|Pa|ºC|ºF|milj|cal|rad|Wh|Hz|Ah|mol|min|po)(\u00B2|\u00B3|\u207B\u00B9)?)(\/\w+)?(\b|\Z)", r"\1 \3\4\5\6\7", txt)
        """
        Substitute the dot with the comma as decimal separator
        """
        txt = _re.sub(r"(\d+)\.(\d{1,2})(\b|\Z)", r"\1,\2\3", txt)
        """
        Delete the space between a closing parenthesis and a dot
        """
        txt = _re.sub(r"(\))( +)(\.\s?)", r"\1\3", txt)
        """
        Substitute the time format from hh:mm h GMT to hh.mm po GMT
        """
        txt = _re.sub(r"(\d{1,2}):(\d{2})( h)( [A-Z]{3})?(\b|\Z)",r"\1.\2 po\4\5", txt)
        """
        Substitute the time format from hh:mm AM/PM to hh.mm in 24h format
        """
        hours = []
        hours = _re.findall(r"(\d{1,2}):(\d{2})( )(AM|PM|m\.)?(\b|\Z)?", txt)
        if hours != []:
            for hour in hours:
                if hour[3] != "":
                    h = hour[0] + ":" + hour[1] + hour[2] + hour[3]
                else:
                    h = hour[0] + ":" + hour[1]
                if hour[3] == "PM":
                    if hour[0] == "12":
                        new = "12." + hour[1]
                        txt = _re.sub(h, new, txt)
                    else:
                        new = str(int(hour[0]) + 12) + "." + hour[1]
                        txt = _re.sub(h, new, txt)
                elif hour[3] == "AM":
                    if hour[0] == "12":
                        new = "00." + hour[1]
                        txt = _re.sub(h, new, txt)
                    else:
                        new = hour[0] + "." + hour[1]
                        txt = _re.sub(h, new, txt)
                else:
                    new = hour[0] + "." + hour[1]
                    txt = _re.sub(h, new, txt)
        return txt