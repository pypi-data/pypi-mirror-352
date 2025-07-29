from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg
import re as _re


class KilometresNorm(NormalizerBase):
    NAME = "kilometres_norm"

    DESCRIPTION_DECODING = """
        This normalizer is applied to translated sentences containing 
        the following piece of text: Km 10 + 10. 
        After applying the normalization the text will look like this: Km 10+10. 
    """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:
        # if src_lang != "en" and tgt_lang != "en":
        #     raise ValueError("This normalizer requires English")

        super().__init__(src_lang, tgt_lang)
        self._regex = _re.compile(
            r'\b[kK]m\s*\d+[\s\d]*\+\s*\d+[\s\d]*\b'
        )

    def normalize(self, txt: str) -> str:
        items = _re.findall(self._regex,txt)
        result = list()

        for item in items:
            if item[-1].isnumeric():
                item_split = item.split()
                final_item = item_split[0]+' '+''.join(item_split[1:])
        #         print(final_w)
            else:
                final_char = item[-1]
                item_split = item.split()
                final_item = item_split[0]+' '+''.join(item_split[1:])+final_char
        #         print(final_w)
            txt = txt.replace(item,final_item)

        # for item in entry:
        #     if len(item) < 3:
        #         result.append(item)
        #         continue

        #     if item in self._words:
        #         result.append(self._words[item])
        #     else:
        #         result.append(item)

        return txt

    def process_train(self, seg: Seg) -> None:
        pass

    def process_src_decoding(self, seg: Seg) -> None:
        pass

    def process_tgt_decoding(self, seg: Seg) -> None:
        seg.tgt = self.normalize(seg.tgt)