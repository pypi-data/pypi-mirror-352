from rara_meta_extractor.tools.utils import load_txt, load_json
from rara_meta_extractor.constants.schemas import TEXT_CLASSIFIER_SCHEMA
from rara_meta_extractor.constants.data_classes import (
    TextBlock, AuthorField, TextPartLabel, TEXT_BLOCKS, META_YEAR_FIELDS
)
import importlib.resources
import os
import logging


LOGGER = logging.getLogger("rara-meta-extractor")

METADATA_TEXT_BLOCKS = [TextBlock.METADATA, TextBlock.TITLE_PAGE]

# File paths
AUTHOR_FIELDS_FILE_PATH =  importlib.resources.files("rara_meta_extractor.data.fields") / "kata_author_fields.txt"
META_FIELDS_FILE_PATH = importlib.resources.files("rara_meta_extractor.data.fields") / "kata_meta_fields.txt"

META_EXTRACTOR_INSTRUCTIONS_FILE_PATH = importlib.resources.files("rara_meta_extractor.data.instructions") / "meta_extractor_instructions.txt"
TEXT_CLASSIFIER_INSTRUCTIONS_FILE_PATH = importlib.resources.files("rara_meta_extractor.data.instructions") / "text_classifier_instructions.txt"

META_SCHEMA_PATH = importlib.resources.files("rara_meta_extractor.data.schemas") / "meta_schema.json"

AUTHOR_ROLES_FILE_PATH = importlib.resources.files("rara_meta_extractor.data.field_translations") / "author_roles.json"

AUTHOR_ROLES_DICT = load_json(AUTHOR_ROLES_FILE_PATH)

AUTHOR_FIELDS = load_txt(AUTHOR_FIELDS_FILE_PATH, to_list=True)
META_FIELDS = load_txt(META_FIELDS_FILE_PATH, to_list=True)


LLAMA_META_EXTRACTOR_INSTRUCTIONS = load_txt(META_EXTRACTOR_INSTRUCTIONS_FILE_PATH)
LLAMA_TEXT_CLASSIFIER_INSTRUCTIONS = load_txt(TEXT_CLASSIFIER_INSTRUCTIONS_FILE_PATH)

META_SCHEMA = load_json(META_SCHEMA_PATH)


LLAMA_TEXT_CLASSIFIER_URL = "http://dev-elastic1.texta.ee:8080"
LLAMA_META_EXTRACTOR_URL = "http://localhost:8080"

FIELDS = META_FIELDS + AUTHOR_FIELDS


DEFAULT_INSTRUCTIONS = "This is a conversation between User and Llama - a metadata extrator with skills of professional cataloguer. Please extract the following fields: {0}"

KATA_INSTRUCTIONS = (
    f"This is a conversation between User and Llama - a metadata extrator with skills of professional cataloguer. " +
    f"Your only assignment is to extract relevant metadata and OUTPUT IT AS JSON DICT. " +
    f"THIS IS VERY IMPORTANT! Output it as JSON DICT or DIE. Fields you are trying to extract are the following: {FIELDS}\n"
)

META_EXTRACTOR_CONFIG = {
    "llama_host_url": LLAMA_META_EXTRACTOR_URL,
    "instructions": KATA_INSTRUCTIONS,
    "fields": [],
    "json_schema": {},
    "temperature": 0.0,
    "n_predict": 500
}

TEXT_CLASSIFIER_CONFIG = {
    "llama_host_url": LLAMA_TEXT_CLASSIFIER_URL,
    "instructions": LLAMA_TEXT_CLASSIFIER_INSTRUCTIONS,
    "fields": TEXT_CLASSIFIER_SCHEMA,
    "json_schema": {},
    "temperature": 0.0,
    "n_predict": 500
}
