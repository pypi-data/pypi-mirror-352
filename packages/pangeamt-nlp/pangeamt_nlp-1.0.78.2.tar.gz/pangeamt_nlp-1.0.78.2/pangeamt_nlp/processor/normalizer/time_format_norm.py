from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg
import re as _re


class TimeFormatNorm(NormalizerBase):
    NAME = "time_format_norm"

    DESCRIPTION_DECODING = """
    This normalizer is applied to fix time format in translations.
    """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        super().__init__(src_lang, tgt_lang)

    def normalize(self, src_txt, tgt_txt):
        
        src_pattern = r"(\d{1,2})[:.](\d{1,2})(?= [Pp]\.?[Mm]\.?)"
        tgt_pattern = r"(\d{1,2})[:.](\d{2})(?! [Pp]\.?[Mm]\.?)"

        src_matches = _re.finditer(src_pattern, src_txt)
        tgt_matches = _re.finditer(tgt_pattern, tgt_txt)

        for src_match, tgt_match in zip(src_matches, tgt_matches):
            tgt_date = str(int(tgt_match.group(1))+12)
            tgt_txt = _re.sub(tgt_match.group(), f"{tgt_date}:{tgt_match.group(2)}", tgt_txt, count = 1)
        
        return tgt_txt

    def process_train(self, seg: Seg) -> None:
        pass

    def process_src_decoding(self, seg: Seg) -> None:
        pass

    def process_tgt_decoding(self, seg: Seg) -> None:
        seg.tgt = self.normalize(seg.src, seg.tgt)