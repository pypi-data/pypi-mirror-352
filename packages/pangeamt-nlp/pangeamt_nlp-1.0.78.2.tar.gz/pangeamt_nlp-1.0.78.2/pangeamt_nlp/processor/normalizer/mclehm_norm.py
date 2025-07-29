from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg
import re as _re


class MclehmNorm(NormalizerBase):
    NAME = "mclehm_norm"

    DESCRIPTION_DECODING = """
    This normalizer is applied to fix specific translation errors related to a client.
    """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        if tgt_lang != "es":
            raise ValueError("This normalizer requires a Spanish target.")

        super().__init__(src_lang, tgt_lang)

    def normalize(self, txt: str) -> str:
        
        result = _re.sub(r"(Cláusula|Apartado) (\d+),(\d+)", r"\1 \2.\3", txt)
        result = _re.sub(r"Bahrein", r"Bahréin", result)
        
        return result

    def process_train(self, seg: Seg) -> None:
        pass

    def process_src_decoding(self, seg: Seg) -> None:
        pass

    def process_tgt_decoding(self, seg: Seg) -> None:
        if self.tgt_lang == "es":
            seg.tgt = self.normalize(seg.tgt)
        
