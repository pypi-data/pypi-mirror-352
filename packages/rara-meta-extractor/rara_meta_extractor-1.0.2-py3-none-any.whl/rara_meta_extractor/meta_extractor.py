from typing import List, Dict
from collections import defaultdict
from rara_meta_extractor.config import (
    META_EXTRACTOR_CONFIG, TEXT_CLASSIFIER_CONFIG, METADATA_TEXT_BLOCKS, LOGGER,
    AUTHOR_FIELDS, META_FIELDS, TextBlock
)
from rara_meta_extractor.constants.data_classes import TextBlock, AuthorField, TextPartLabel
from rara_meta_extractor.tools.meta_formatter import Meta
from rara_meta_extractor.llm_agents import TextClassifierAgent, MetaExtractorAgent
from rara_meta_extractor.text_part_classifier import TextPartClassifier
import regex as re


class MetaExtractor:
    def __init__(self,
        meta_extractor_config: dict = META_EXTRACTOR_CONFIG,
        text_classifier_config: dict = TEXT_CLASSIFIER_CONFIG
    ):
        self.meta_extractor_config = meta_extractor_config
        self.text_classifier_config = text_classifier_config

        self.meta_agent = MetaExtractorAgent(self.meta_extractor_config)
        self.text_classifier_agent = TextClassifierAgent(self.text_classifier_config)

        self.text_part_classifier = TextPartClassifier()



    def classify_text(self, text: str, default: str = TextBlock.METADATA) -> str:
        """ Classifies text into one of the text blocks defined in TextBlock.

        Parameters
        -----------
        text: str
            Text to classify
        default: str
            Default value to return in case of an exception.

        Returns
        -----------
        str:
            Text class.
        """
        try:
            text_type_dict = self.text_classifier_agent.extract(text=text)
            text_class = text_type_dict.get("text_type")[0]
        except Exception as e:
            LOGGER.error(
                f"Detecting text type for text '{text[:50]}' failed with error: {e}. "
                f"Defaulting to '{default}'"
            )
            text_class = default
        return text_class



    def _construct_llama_input(self, texts: List[str], use_llm: bool = False,
            max_length_per_text: int = 1500
    ) -> List[str]:
        LOGGER.debug("Constructing Llama input!")
        if use_llm:
            verified_texts = []
            for text in texts:
                text_type = self.classify_text(text)
                if text_type in METADATA_TEXT_BLOCKS:
                    verified_texts.append(text)
            if not verified_texts:
                LOGGER.error(
                    f"No verified metadata text block found from texts {texts} with LLM!"
                )
        else:
            verified_texts = texts[:3]
            if len(texts) > 5:
                for text in texts[3:5]:
                    if (len(text) < max_length_per_text and not
                        re.search("sisukord|table of contents", text, re.IGNORECASE)
                    ):
                        verified_texts.append(text)

        return verified_texts

    def _get_text_parts(self, texts: List[dict]) -> List[dict]:
        text_parts = []
        _text_parts = defaultdict(lambda: defaultdict(list))

        for text in texts:
            raw_text = text.get("text", "")
            lang = text.get("lang", "")
            label = self.text_part_classifier.get_label(raw_text)
            if label != TextPartLabel.OTHER:
                _text_parts[label]["texts"].append(raw_text)
                _text_parts[label]["langs"].append(lang)

        for label, values in _text_parts.items():
            texts = values.get("texts")
            langs = values.get("langs")
            lang_counts = defaultdict(int)
            for lang in langs:
                lang_counts[lang]+=1
            most_frequent_lang = sorted(list(lang_counts.items()), key=lambda x: x[1], reverse=True)[0][0]
            text_part = "\n".join(texts)
            text_parts.append(
                {"text_type": label, "text_value": text_part, "language": most_frequent_lang}
            )
        return text_parts


    def extract(self, texts: List[dict], epub_xml: List[str] = [], mets_alto_xml: List[str] = [],
        verify_text: bool = True, n_trials: int = 1, merge_texts: bool = True, min_ratio=0.8,
        add_missing_keys: bool = False, detect_text_parts: bool = True
    ) -> dict:
        """ Extracts relevant metadata from a batch of texts

        Parameters
        -----------
        # TODO!!!! Texts should actually be a dict with metsalto_xml, epub_xml and plaintext keys?!?
        texts: List[str]
            List of texts from where to extract meta information. Expected to contain keys
            "lang", "section_meta" and "text"
        epub_xml: List[str] or str???
            List of epub XML strings.
        mets_alto_xml: List[str] or str????
            List of METS/ALTO XML strings.
        verify_text: bool
            If enabled, each text is passed to text classifier agent first
            and only texts classified as metadata blocks are passed to
            meta extractor(s).
        n_trials:
            if temperature > 0, run `n_trials` trials and output only statistically relevant
            results.
        """
        if epub_xml:
            # TODO: apply epub XML parsers
            pass

        if mets_alto_xml:
            # TODO: apply METS/ALTO XML parsers
            pass

        raw_texts = [doc.get("text") for doc in texts if doc.get("text").strip()]

        verified_texts = self._construct_llama_input(raw_texts, use_llm=verify_text)
        if merge_texts:
            verified_texts = ["\n\n".join(verified_texts)]
            LOGGER.debug(f"Constructed Llama input of size {len(verified_texts[0])} characters.")

        meta_batches = []

        for text in verified_texts:
            for trial_nr in range(n_trials):
                try:
                    LOGGER.debug(
                        f"Trial nr {trial_nr}. Extracting information with Llama agent " \
                        f"from text '{text[:20]}...'."
                    )
                    meta_batch = self.meta_agent.extract(text=text)
                    LOGGER.debug(f"Raw LLM output: {meta_batch}")
                    meta_batches.append(meta_batch)
                except Exception as e:
                    LOGGER.error(
                        f"Extracting meta information from text: {text[:50]} " \
                        f"failed with error: {e}."
                )
        text_parts = []
        if detect_text_parts:
            text_parts = self._get_text_parts(texts)

        meta = Meta(
            meta_batches=meta_batches,
            text_parts=text_parts,
            min_ratio=min_ratio,
            add_missing_keys=add_missing_keys
        )
        return meta.to_dict()
