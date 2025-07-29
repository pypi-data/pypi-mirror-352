from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg
import re as _re
import logging

logger = logging.getLogger(__name__) 

class UsdNosotrosNorm(NormalizerBase):
    NAME = "usd_nosotros_norm"

    DESCRIPTION_DECODING = """
        This normalizer is applied to translated sentences containing 
        the following piece in the source and target texts: US$### ----> NOSOTROS +amount USD 
        After applying the normalization the target text will look like this: amount USD. 
    """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        super().__init__(src_lang, tgt_lang)
        if src_lang != "en" and tgt_lang != "es":
            raise ValueError("This normalizer requires English-Spanish direction.")
        self._regex = _re.compile(
            r'.*[uU][sS]\$[0-9]+'
        )

    def normalize(self, txt: str) -> str:
        txt = txt.replace("NOSOTROS ", "").replace("nosotros", "")
        return txt

    def process_train(self, seg: Seg) -> None:
        pass

    def process_src_decoding(self, seg: Seg) -> None:
        pass

    def process_tgt_decoding(self, seg: Seg) -> None:
        matches = _re.findall(self._regex, seg.src_raw)
        if len(matches)>0:
            seg.tgt = self.normalize(seg.tgt)
