# Search translations

## Install requirements
`pip install -r requirements.txt`

## Basic translation (default values, with test files)
`python search_translations.py`

## Reset translation file
`python reset_test_translations.py`

## Test Google translate
`test_google.py`

# Config
Basic config demo: `search_translations_config_demo.json`
```
{
	"path_search" : ".",
	"path_translations" : ".",
	"domain" : "translation",
	"translate" : false,
	"transform_lowercase" : false,
	"rem_old_translations" : false,
	"generate_mo" : false,
	"languages_code_translate" : ["es_ES", "en_US"]
}
```
