from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg
import re as _re


class InvertDatesNorm(NormalizerBase):
    NAME = "invert_dates_norm"

    DESCRIPTION_DECODING = """
    This normalizer is applied to fix date format in translations.
    """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        super().__init__(src_lang, tgt_lang)

    def normalize(self, src_txt, tgt_txt):
        pattern = r"(\d{1,2})/(\d{1,2})/(\d{4})"
        src_matches = _re.finditer(pattern, src_txt)
        tgt_matches = _re.finditer(pattern, tgt_txt)

        for src_match, tgt_match in zip(src_matches, tgt_matches):
            if src_match.group(1) != tgt_match.group(1):
                tgt_txt = _re.sub(tgt_match.group(), f"{tgt_match.group(2)}/{tgt_match.group(1)}/{tgt_match.group(3)}", tgt_txt)
            
        return tgt_txt

    def process_train(self, seg: Seg) -> None:
        pass

    def process_src_decoding(self, seg: Seg) -> None:
        pass

    def process_tgt_decoding(self, seg: Seg) -> None:
        seg.tgt = self.normalize(seg.src, seg.tgt)