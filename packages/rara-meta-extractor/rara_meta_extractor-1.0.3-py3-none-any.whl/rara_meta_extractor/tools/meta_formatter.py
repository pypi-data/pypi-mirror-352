import regex as re
from copy import deepcopy
from typing import List, Dict, NoReturn, Any, Tuple
from collections import defaultdict
from rara_meta_extractor.config import (
    LOGGER, META_FIELDS, AUTHOR_FIELDS,
    META_YEAR_FIELDS, AUTHOR_ROLES_DICT
)
from rara_meta_extractor.constants.data_classes import (
    AuthorField, MetaField, TextBlock, DataRestrictions
)

difference = lambda x, y: set(x) - set(y)

class MetaValidator:
    def __init__(self, meta_fields: List[str] = META_FIELDS,
            author_fields: List[str] = AUTHOR_FIELDS
    ) -> NoReturn:
        self.meta_fields: List[str] = meta_fields
        self.author_fields: List[str] = author_fields

    def _filter_by_length(self,
        key: str, values: List[Any], length: int, values_to_str: bool = False
    ) -> List[Any]:
        """ Filters out values not complying to length requirements.
        """
        original_values = deepcopy(values)
        filtered_values = []
        for value in values:
            if len(str(value)) == length:
                if values_to_str:
                    filtered_values.append(str(value))
                else:
                    filtered_values.append(value)
        diff = difference(original_values, filtered_values)
        if diff:
            LOGGER.debug(
                f"Removed the following values for key '{key}' not complying " \
                f" to length requirement ({length} characters): {list(diff)}"
            )
        return filtered_values

    def _remove_empty(self, key: str, values: List[Any]) -> List[Any]:
        """ Remove empty strings and "None"-s.
        """
        original_values = deepcopy(values)
        values = [
            v for v in values
            if str(v).strip() and str(v).strip() != "None"
        ]
        n_removed = len(original_values) - len(values)
        if n_removed > 0:
            LOGGER.debug(f"Removed {n_removed} empty values for key '{key}'.")
        return values

    def _get_validated_values(self, key: str, values: list,
            check_dates: bool = True
    ) -> List[Any]:
        values = self._remove_empty(key, values)

        if key == MetaField.ISBN:
            values = self._filter_by_length(
                key=key,
                values=values,
                length=DataRestrictions.ISBN_LENGTH,
                values_to_str=True
            )
        elif key == MetaField.ISSN:
            values = self._filter_by_length(
                key=key,
                values=values,
                length=DataRestrictions.ISSN_LENGTH,
                values_to_str=True
            )
        elif check_dates and key.strip() in META_YEAR_FIELDS:
            values = self._filter_by_length(
                key=key,
                values=values,
                length=DataRestrictions.YEAR_LENGTH,
                values_to_str=False
            )
        return values

    def _is_valid_key(self, key: str) -> bool:
        """ Checks, if the key is a valid key present in either
        META_FIELDS or AUTHOR_FIELDS list.
        """
        if key in META_FIELDS or key in AUTHOR_FIELDS:
            return True
        return False


class MetaFormatter:
    """ Formats meta
    """
    def __init__(self,
        meta_fields: List[str] = META_FIELDS,
        author_fields: List[str] = AUTHOR_FIELDS
    ) -> NoReturn:
        self.meta_validator = MetaValidator(
            meta_fields=META_FIELDS,
            author_fields=AUTHOR_FIELDS
        )

    def _filter_by_ratio(self, values: List[Tuple[Any, int]],
            n_trials: int, min_ratio: float
    ) -> List[Any]:
        """ Keeps only values that have been predicted
        in `min_ratio` trials.
        """
        filtered_values = [
            v[0] for v in values
            if float(v[1]/n_trials) >= min_ratio
        ]
        return filtered_values

    def _merge_meta(self, meta_batches: List[dict], min_ratio: float = 0.5) -> dict:
        """ Merges meta into a single dict.
        """
        LOGGER.debug("Merging and formatting metadata.")

        formatted_meta = [
            self._format_meta(meta_dict)
            for meta_dict in meta_batches
        ]
        meta = {}
        frequencies = defaultdict(lambda: defaultdict(int))
        n_trials = len(meta_batches)

        for meta_dict in formatted_meta:
            for key, values in meta_dict.items():
                for value in values:
                    frequencies[key][value]+=1

        for key, value_dict in frequencies.items():
            value_list = sorted(
                list(value_dict.items()),
                key=lambda x: x[1],
                reverse=True
            )
            meta[key] = self._filter_by_ratio(
                values=value_list,
                n_trials=n_trials,
                min_ratio=min_ratio
            )
        return meta

    def _parse_authors(self, authors_list: List[str]) -> List[str]:
        """ Parse weirdly extracted authors like:
        "Reelika RätsepMari-Liis TammikElmar Zimmer"
        """
        LOGGER.debug("Parsing authors.")
        new_authors = []
        for author in authors_list:
            parsed = re.split("(?<=[a-züõöäšž])(?=[A-ZÜÕÖÄŠŽ])", author)
            new_authors.extend(parsed)
        return new_authors

    def _parse_dates(self, values: List[str]) -> List[str]:
        parsed = []
        for value in values:
            match = re.search("(?<=\D)\d{4}(?=\D)", value)
            if match:
                parsed.append(match.group())
        return parsed

    def _add_missing_keys(self, meta: dict) -> dict:
        """ Adds missing meta keys.
        """
        meta_copy = deepcopy(meta)
        missing_keys = {}
        for key in META_FIELDS:
            if key not in meta:
                missing_keys[key] = []
        meta_copy.update(missing_keys)
        return meta_copy

    def _remove_empty_fields(self, meta: dict) -> dict:
        """ Removes empty fields.
        """
        new_meta = {}
        for key, values in meta.items():
            if values:
                new_meta[key] = values
        return new_meta

    def _format_meta(self, meta: dict, check_dates: bool = False) -> dict:
        """ Format meta.
        """
        formatted_meta = {}
        for key, values in list(meta.items()):
            key = key.strip()
            if not self.meta_validator._is_valid_key(key):
                LOGGER.error(
                    f"Detected an invalid key '{key}'. " \
                    f"This will NOT be added to the output."
                )
                continue
            values = self.meta_validator._get_validated_values(
                key=key, values=values, check_dates=check_dates
            )
            if values:
                if key in AUTHOR_FIELDS:
                    formatted_meta[key] = self._parse_authors(values)
                elif key in META_YEAR_FIELDS:
                    formatted_meta[key] = self._parse_dates(values)
                else:
                    formatted_meta[key] = values
        return formatted_meta


    def _format_authors(self, meta: dict) -> dict:
        """ Convert authors from a flat structure into
        a list of dicts.
        """
        LOGGER.debug("Formatting authors.")
        new_meta = {"authors": [], "main_author": ""}
        for key, values in list(meta.items()):
            if key in AUTHOR_FIELDS:
                for value in values:
                    new_author = Author(name=value, role=key).to_dict()
                    new_meta["authors"].append(new_author)
                if key == AuthorField.AUTHOR and values:
                    new_meta["main_author"] = values[0]
            else:
                new_meta[key] = values
        return new_meta


class Author:
    def __init__(self, name: str, role: str, unknown_role: str = AuthorField.UNKNOWN):
        self.name: str = name
        self.en_role: str = role
        self.et_role: str = AUTHOR_ROLES_DICT.get(self.en_role, unknown_role)

    def to_dict(self) -> dict:
        author_dict = {
            "author": self.name,
            "author_role": self.et_role
        }
        return author_dict

class Title:
    def __init__(self, titles: List[str], lang: str):
        self.titles = titles
        self.lang = lang

    def to_dict() -> dict:
        title_dict = {
            "title": self.titles[0] if self.titles else "",
            "title_language": self.lang, # TODO: translate ?
            "part_number": "",
            "part_title": "",
            "version": "",
            "author_from_title": ""
        }
        return title_dict

class TextParts:
    def __init__(self):
        pass

class Meta:
    def __init__(self, meta_batches: List[dict], text_parts: List[dict], min_ratio: float = 0.8,
        add_missing_keys: bool = False
    ) -> NoReturn:
        self.meta_batches: List[dict] = meta_batches
        self.text_parts: List[dict] = text_parts
        self.min_ratio: float = min_ratio
        self.add_missing_keys: bool = add_missing_keys

        self.meta_formatter: MetaFormatter = MetaFormatter(
            meta_fields = META_FIELDS,
            author_fields=AUTHOR_FIELDS
        )

        self.__merged_meta: dict = {}
        self.__meta_with_reformatted_authors: dict = {}
        self.__meta_with_all_keys: dict = {}
        self.__meta_without_empty_fields: dict = {}

    @property
    def merged_meta(self) -> dict:
        if not self.__merged_meta:
            self.__merged_meta = self.meta_formatter._merge_meta(
                meta_batches=self.meta_batches,
                min_ratio=self.min_ratio
            )
        return self.__merged_meta

    @property
    def meta_with_reformatted_authors(self):
        if not self.__meta_with_reformatted_authors:
            self.__meta_with_reformatted_authors = self.meta_formatter._format_authors(
                meta=self.merged_meta
            )
        return self.__meta_with_reformatted_authors

    @property
    def meta_with_all_keys(self):
        if not self.__meta_with_all_keys:
            self.__meta_with_all_keys = self.meta_formatter._add_missing_keys(
                meta=self.meta_without_empty_fields
            )
        return self.__meta_with_all_keys

    @property
    def meta_without_empty_fields(self):
        if not self.__meta_without_empty_fields:
            self.__meta_without_empty_fields = self.meta_formatter._remove_empty_fields(
                meta=self.meta_with_reformatted_authors
            )
        return self.__meta_without_empty_fields

    def _concat(self, meta: dict) -> dict:
        concatted = {}
        for key, value in meta.items():
           key_tokens = key.split()
           new_key = "_".join(key_tokens)
           concatted[new_key] = value
        return concatted

    def to_dict(self):
        if self.add_missing_keys:
            meta_dict = self._concat(self.meta_with_all_keys)
        else:
            meta_dict = self._concat(self.meta_without_empty_fields)
        if self.text_parts or self.add_missing_keys:
            meta_dict["text_parts"] = self.text_parts
        return meta_dict
