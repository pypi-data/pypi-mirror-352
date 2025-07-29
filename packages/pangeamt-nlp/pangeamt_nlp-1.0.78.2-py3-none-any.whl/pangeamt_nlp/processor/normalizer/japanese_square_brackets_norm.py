from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg
import re as _re

class JapaneseSquareBracketsNorm(NormalizerBase):
    NAME = "japanese_square_brackets_norm"


    DESCRIPTION_DECODING = """
        Apply the normalizer process to src if src_lang is japanese, do nothing
        otherwise. Change japanese square brackets to european square brackets because our engines work better applying this. 
    """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        if src_lang != "ja":
            raise ValueError("Japanese Normalizer processor requires Japanese")

        super().__init__(src_lang, tgt_lang)

    def normalize(self, txt: str) -> str:
        result = _re.sub(r"［", "[", txt)
        result = _re.sub(r"］", "]", result)
        return result

    def process_train(self, seg: Seg) -> None:
        pass

    def process_src_decoding(self, seg: Seg) -> None:
        if self.src_lang == "ja":
            seg.src = self.normalize(seg.src)

    def process_tgt_decoding(self, seg: Seg) -> None:
        pass
