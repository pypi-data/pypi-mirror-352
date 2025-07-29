[![flake8 Lint](https://github.com/acdh-oeaw/acdh-wikidata-pyutils/actions/workflows/lint.yml/badge.svg)](https://github.com/acdh-oeaw/acdh-wikidata-pyutils/actions/workflows/lint.yml)
[![Test](https://github.com/acdh-oeaw/acdh-wikidata-pyutils/actions/workflows/test.yml/badge.svg)](https://github.com/acdh-oeaw/acdh-wikidata-pyutils/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/acdh-oeaw/acdh-wikidata-pyutils/graph/badge.svg?token=5ZWMXlmFmr)](https://codecov.io/gh/acdh-oeaw/acdh-wikidata-pyutils)
[![PyPI version](https://badge.fury.io/py/acdh-wikidata-pyutils.svg)](https://badge.fury.io/py/acdh-wikidata-pyutils)

# acdh-wikidata-pyutils
Utility package to fetch data from Wikidata

## development

* create virtual env `python -m venv venv` and activate it `source venv/bin/activate`
* install dev-dependencies `pip install -r requirements_dev.txt`
* install acdh-wikidata-pyutils locally `pip install -e .`
* run tests `coverage run -m pytest`

# usage

```python
from acdh_wikidata_pyutils import WikiDataPerson

item = WikiDataPerson("https://www.wikidata.org/wiki/Q44331")
person = item.get_apis_entity()
print(person)
# {'name': 'Schnitzler', 'first_name': 'Arthur', 'start_date_written': '1862-05-15', 'end_date_written': '1931-10-21', 'gender': 'male'}
```

```python
from acdh_wikidata_pyutils import WikiDataPlace

item = WikiDataPlace("https://www.wikidata.org/wiki/Q41329")
place = item.get_apis_entity()
print(place)
# {'name': 'Linz', 'lat': 48.30583333333333, 'long': 14.286388888888888}
```