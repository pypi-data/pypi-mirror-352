from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg
import re as _re


class SpanishSentencesNorm2(NormalizerBase):
    NAME = "spanish_sentences_norm_2"

    DESCRIPTION_DECODING = """
    This normalizer is applied to fix translation errors related to Spanish conjuctions.
    """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        if tgt_lang != "es":
            raise ValueError("This normalizer requires a Spanish target.")
        super().__init__(src_lang, tgt_lang)
        

    def normalize(self, txt: str) -> str:
        
        result = _re.sub(r"(?<=\s)o(?=\s[oO])", "u", txt)
        result = _re.sub(r"^O(?=\s[oO])|(?<=\s)O(?=\s[oO])", "U", result, flags=_re.MULTILINE)
        result = _re.sub(r"(?<=\s)y(?=\s[iI])", "e", result)
        result = _re.sub(r"^Y(?=\s[iI])|(?<=\s)Y(?=\s[iI])", "E", result, flags=_re.MULTILINE)
        result = _re.sub(r"(?<=\s)u(?=\s[aeiuAEIU])", "o", result)
        result = _re.sub(r"(?<=\s)e(?=\s[aeouAEOU])", "y", result)
        
        
        return result

    def process_train(self, seg: Seg) -> None:
        pass

    def process_src_decoding(self, seg: Seg) -> None:
        pass

    def process_tgt_decoding(self, seg: Seg) -> None:
        if self.tgt_lang == "es":
            seg.tgt = self.normalize(seg.tgt)
