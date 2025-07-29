from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg
import re as _re


class EnglishChangesNorm(NormalizerBase):
    NAME = "english_changes_norm"

    DESCRIPTION_DECODING = """
        Apply this normalizer process to the target.
    """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        if src_lang != "en" and tgt_lang != "en":
            raise ValueError("This normalizer requires English")

        super().__init__(src_lang, tgt_lang)
        self._regex = _re.compile(
            r'( |,|;|:|\.|\{|\}|\[|\]|\/|\\|\(|\)|\?|¡|"|\')'
        )
        self._words = {"jumper": "sweater", "JUMPER":"SWEATER", "Jumper":"Sweater"}

    def normalize(self, txt: str) -> str:
        entry = self._regex.split(txt)
        result = list()

        for item in entry:
            if len(item) < 3:
                result.append(item)
                continue

            if item in self._words:
                result.append(self._words[item])
            else:
                result.append(item)

        return "".join(result)

    def process_train(self, seg: Seg) -> None:
        pass

    def process_src_decoding(self, seg: Seg) -> None:
        pass

    def process_tgt_decoding(self, seg: Seg) -> None:
        if self.tgt_lang == "en":
            seg.tgt = self.normalize(seg.tgt)