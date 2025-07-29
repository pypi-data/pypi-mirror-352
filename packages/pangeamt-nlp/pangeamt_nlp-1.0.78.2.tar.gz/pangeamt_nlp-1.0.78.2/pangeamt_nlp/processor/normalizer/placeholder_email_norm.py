import re
from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.seg import Seg


class PlaceholderEmailNorm(NormalizerBase):

    NAME = "placeholder_email_normalizer"

    DESCRIPTION_TRAINING = """
        Wrap emails in placeholders. Empty for now.
    """

    DESCRIPTION_DECODING = """
        Wrap emails in placeholders.
    """

    def __init__(self, src_lang: str, tgt_lang: str) -> None:

        super().__init__(src_lang, tgt_lang)

    def normalize(self, txt: str) -> str:
        """ Normalize placeholder emails

        Parameters:
        txt (str): String to normalize

        Returns:
        str: Returns the string normalized

        """

        #\\b[\\w\\.-]+@[\\w\\.-]+\\b
        mails = re.findall(r'[\w.-]+@[\w.-]+', txt)
        if len(mails) > 0:
            count = 1
            for token in mails:
                txt = txt.replace(token, "(EML"+str(count)+":"+token+")")
                count += 1
            return (txt, mails)
        else:
            return (txt, [])

    def substitute(self, txt: str, entities: []) -> str:
        if "(EML" in txt:
            ids = re.findall('EML[1-99]:', txt)
            for i in range(len(ids)):
                txt=re.sub("\(EML"+str(i+1)+":.*?\)",entities[i],txt)
        return (txt)

    def process_train(self, seg: Seg) -> None:
        pass

    def process_src_decoding(self, seg: Seg) -> None:
        seg.src, seg._src_entities_emails = self.normalize(seg.src)

    def process_tgt_decoding(self, seg: Seg) -> None:
        seg.tgt = self.substitute(seg.tgt, seg._src_entities_emails)