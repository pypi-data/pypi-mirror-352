from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg
from pangeamt_nlp.processor.normalizer.quote_dec_norm import QuotesInfo

import csv as _csv
import re as _re
import os as _os


class AmericanizerNormalizer(NormalizerBase):
    NAME = "americanizer"

    DESCRIPTION_TRAINING = """
        Apply the americanizer process to the source or the target, checking
        with the src_lang and tgt_lang to decide where to apply it.
    """

    DESCRIPTION_DECODING = """
        Apply the americanizer process to src if src_lang is english, do nothing
        otherwise.
    """

    def __init__(self, src_lang: str, tgt_lang: str, britaniser=False) -> None:
        if src_lang != "en" and tgt_lang != "en":
            raise Warning("Americanizer processor requires English")

        else:
            super().__init__(src_lang, tgt_lang)
            self._regex = _re.compile(
                r'( |,|;|:|\.|\{|\}|\[|\]|\/|\\|\(|\)|\?|¡|"|“|”|‘|’|\')'
            )
            self._words = {}
            csv_path = _os.path.join(
                _os.path.dirname(_os.path.realpath(__file__)), "americanizer.csv"
            )
            with open(csv_path, newline="") as csvfile:
                spamreader = _csv.reader(csvfile, delimiter=",", quotechar="|")
                if not britaniser:
                    for row in spamreader:
                        self._words[row[0]] = row[1]
                else:
                    for row in spamreader:
                        self._words[row[1]] = row[0]
            self._britaniser = britaniser
            self._dict_quotes = {
                '“': '‘',
                "‘": "“",
                "”": "’",
                '’': '”',
            }

    def quotes_lang(self) -> str:
        if not self._britaniser:
            lang = "en-us"
        else:
            lang = "en"
        return lang

    def normalize(self, txt: str) -> str:
        entry = self._regex.split(txt)
        result = list()
        for item in entry:
            if item in ['“', '”', "‘", "’"]:
                item = item.replace(item, self._dict_quotes[item])
            
            if len(item) < 3:
                result.append(item)
                continue
            item_inflected = [item.lower(), item.upper(), item.capitalize(), item.title()]

            _words_inflected_idx = [inflection in self._words  for inflection in item_inflected]
            if any(_words_inflected_idx):
                idx = _words_inflected_idx.index(True)
                if item.islower():
                    result.append(self._words[item_inflected[idx]].lower())
                elif item.capitalize() == item:
                    result.append(self._words[item_inflected[idx]].capitalize())
                elif item.isupper():
                    result.append(self._words[item_inflected[idx]].upper())
            else:
                result.append(item)

        return "".join(result)

    def process_train(self, seg: Seg) -> None:
        if self.src_lang == "en":
            seg.src = self.normalize(seg.src)
        elif self.tgt_lang == 'en':
            seg.tgt = self.normalize(seg.tgt)

    def process_src_decoding(self, seg: Seg) -> None:
        if self.src_lang == "en":
            seg.src = self.normalize(seg.src)

    def process_tgt_decoding(self, seg: Seg) -> None:
        if self.tgt_lang == "en":
            seg.tgt = self.normalize(seg.tgt)
