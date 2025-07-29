[![Tests](https://github.com/DataShades/ckanext-composite-search/workflows/Tests/badge.svg?branch=main)](https://github.com/DataShades/ckanext-composite-search/actions)

# ckanext-composite-search

Complex search form for the dataset search page.

Filter by field, search by multiple criteria, combine filter with the AND/OR operators and
forget about Lucene queries

## Requirements

Compatibility with core CKAN versions:

| CKAN version    | Compatible? |
|-----------------|-------------|
| 2.9             | yes         |
| 2.10            | yes         |
|                 |             |


## Installation

To install ckanext-composite-search:

1. Install the extension
     ```sh
	pip install ckanext-composite-search
     ```

1. Add `composite_search default_composite_search` to the `ckan.plugins`
   setting in your CKAN config file.


## Config settings


```ini
# Prefix for field-names of the search form. Due to the way,
# CKAN handles extra search parameters, prefix must begin with `ext_`
# (optional, default: ext_composite_).
ckanext.composite_search.prefix = ext_p_

# Escape search terms using single-quote, double-quote or both at the same time.
# (optional, default: double, values: single|double|both).
ckanext.composite_search.plugin.default.literal_quotes = single

# List of field names that must not be tokenized. Usually, one will
# use this option when searching by tags or other keywords.
# (optional, default: <empty>).
ckanext.composite_search.plugin.default.keyword_fields = tags groups

```

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
