from dataclasses import dataclass

@dataclass(frozen=True)
class TextBlock:
    REGULAR: str = "regular text block"
    METADATA: str = "metadata text block"
    TITLE_PAGE: str = "title page"
    ABSTRACT: str = "abstract text block"
    SUMMARY: str = "summary text block"

@dataclass(frozen=True)
class TextPartLabel:
    TABLE_OF_CONTENTS: str = "Sisukord"
    ABSTRACT: str = "Abstrakt"
    CONCLUSION: str = "Kokkuvõte"
    OTHER: str = "Muu"

@dataclass(frozen=True)
class AuthorField:
    AUTHOR: str = "author"
    UNKNOWN: str = "Teadmata"

@dataclass(frozen=True)
class MetaField:
    ISBN: str = "isbn"
    ISSN: str = "issn"

@dataclass(frozen=True)
class DataRestrictions:
    ISBN_LENGTH: int = 13
    ISSN_LENGTH: int = 8
    YEAR_LENGTH: int = 4

@dataclass(frozen=True)
class MetaYearField:
    DISTRIBUTION_DATE: str = "distribution date"
    PUBLICATION_DATE: str = "publication date"
    MANUFACTURE_DATE: str = "manufacture date"


TEXT_BLOCKS = [v for v in vars(TextBlock()).values()]
META_YEAR_FIELDS = [v for v in vars(MetaYearField()).values()]
