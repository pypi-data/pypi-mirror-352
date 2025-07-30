from rara_meta_extractor.constants.data_classes import TEXT_BLOCKS

TEXT_CLASSIFIER_SCHEMA = [
    {
        "name": "text_type",
        "restrictions": {
            "enum": TEXT_BLOCKS,
            "maxItems": 1
        }
    }
]

META_SCHEMA = [
    {
        "name": "title",
        "restrictions": {}
    },
    {
        "name": "original title",
        "restrictions": {}
    },
    {
        "name": "title part number",
        "restrictions": {}
    },
    {
        "name": "edition",
        "restrictions": {}
    },
    {
        "name": "publisher",
        "restrictions": {}
    },
    {
        "name": "publication year",
        "restrictions": {
            "maxLength": 4,
            "minLength": 4,
            "type": "integer"
        }
    },
    {
        "name": "publication place",
        "restrictions": {}
    },
    {
        "name": "manufacture name",
        "restrictions": {}
    },
    {
        "name": "manufacture place",
        "restrictions": {}
    },
    {
        "name": "manufacture year",
        "restrictions": {
            "maxLength": 4,
            "minLength": 4,
            "type": "integer"
        }
    },
    {
        "name": "distribution name",
        "restrictions": {}
    },
    {
        "name": "distribution place",
        "restrictions": {}
    },
    {
        "name": "distribution year",
        "restrictions": {
            "maxLength": 4,
            "minLength": 4,
            "type": "integer"
        }
    },
    {
        "name": "publication place",
        "restrictions": {}
    },
    {
        "name": "copyright year",
        "restrictions": {
            "maxLength": 4,
            "minLength": 4,
            "type": "integer"
        }
    },
    {
        "name": "country",
        "restrictions": {}
    },
    {
        "name": "isbn",
        "restrictions": {
            "maxLength": 13,
            "minLength": 13,
            "type": "integer"
        }
    },
    {
        "name": "issn",
        "restrictions": {
            "maxLength": 8,
            "minLength": 8,
            "type": "integer"
        }
    }
]

AUTHORS_SCHEMA = [
    {
        "name": "author",
        "restrictions": {}
    },
    {
        "name": "story adaptor",
        "restrictions": {}
    },
    {
        "name": "foreword author",
        "restrictions": {}
    },
    {
        "name": "translator",
        "restrictions": {}
    },
    {
        "name": "illustrator",
        "restrictions": {}
    },
    {
        "name": "editor",
        "restrictions": {}
    },
    {
        "name": "designer",
        "restrictions": {}
    },
    {
        "name": "photographer",
        "restrictions": {}
    },
    {
        "name": "language editor",
        "restrictions": {}
    }
]
