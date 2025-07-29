from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg
import re as _re


class CatalanEleGeminada(NormalizerBase):
    NAME = "catalan_ele_geminada"
    DESCRIPTION_TRAINING = """
          Postrocess to delete spaces between l·l in the target
    """
    DESCRIPTION_DECODING = """
          Postrocess to delete spaces between l·l in the target
    """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        if tgt_lang != "ca":
            raise Warning("CatalanEleGeminada processor requires Catalan")
        else:
            super().__init__(src_lang, tgt_lang)

    def process_train(self, seg: Seg) -> None:
        pass

    def process_src_decoding(self, seg: Seg) -> None:
        pass

    def process_tgt_decoding(self, seg: Seg) -> None:
        if self.tgt_lang == "ca":
            seg.tgt = self.normalize(seg.tgt)

    def normalize(self, txt: str) -> str:
        """
        Delete spaces between l·l in the target
        """
        txt = _re.sub(r"(\w+l)( *)(·)( *)(l\w+)", r"\1\3\5", txt)
        return txt
