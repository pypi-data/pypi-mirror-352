# py_simpledataflow

A simple Pyhton library for processing stream data using a logical sequence of functions.

## Use cases

Transform, select, remove... data from a generator by a sequence of functions.

## Installation

```bash
poetry add py_simpledataflow
# or
pip install py_simpledataflow
# or
pipenv install py_simpledataflow
```

## Quick start

Example:

During run, the steps are in this order:

1. Initialization
   * This part is used to initialize the flow context.
     * This part is useful to open database connexion, files or something like that.
   * Only one time
   * Flow parameter: "`fct_init`"
     * Signature: "`Optional[Union[Callable, List[Callable]]]`"
   * If you use a list of functions, the functions are called in the list order
1. Data loading
   * This part is used to return data, one by one
     * This function return one data by "`yield`" instruction
   * Only one time but return a generator
   * Flow parameter: "`fct_load`"
     * Signature: "`Optional[Callable]`"
1. Filtering
   * This part is used to modify data
     * This is usefull to change the data value
     * By default, if a filter function return "`None`" value, the filter sequence is stopped for the data. This behavior could be change by init "`continue_if_none`" parameter.
   * One time per data
   * Flow parameter: "`fct_filter`"
     * Signature: "`Optional[Union[Callable, List[Callable]]]`"
   * If you use a list of functions, the functions are called in the list order
1. Finalization
   * This part us used to finalize the flow context
     * This part is useful to close database connexion, files or something like that.
     * Usefull also to print report.
   * Only one time
   * Flow parameter: "`fct_finalyze`"
     * Signature: "`Optional[Union[Callable, List[Callable]]]`"
   * If you use a list of functions, the functions are called in the list order

Notes:

* All parameters are optional;
* All functions in parameters accept the "`context: Dict`". It's essential for initialization and finalization parts;
* You could init context outside the flow and pass it to init class method by "`context`" parameter.

Code:

```python
import json
from typing import Any, Dict, Generator

from pysimpledataflow.flow import Flow


def __init(context: Dict) -> None:
    context['mult'] = 2
    context['result'] = []


def __read_data_one_by_one(context: Dict) -> Generator[Dict[str, int], Any, None]:
    mult: int = context['mult']
    for i in range(10):
        yield {
            'num': i * mult,
        }


def __filter(data: Dict, context: Dict) -> None:
    context['result'].append(data['num'])


def __finalyze(context: Dict) -> None:
    print("final context:%s" % json.dumps(context, indent=2))


def test_flow_base() -> None:
    Flow(
        fct_init=__init,
        fct_load=__read_data_one_by_one,
        fct_filter=__filter,
        fct_finalyze=__finalyze,
    ).run()
```

Output:

```json
final context:{
  "mult": 2,
  "result": [
    0,
    2,
    4,
    6,
    8,
    10,
    12,
    14,
    16,
    18
  ]
}
```

## Examples

See [tests](https://github.com/ArnaudValmary/py_simpledataflow/tree/main/tests/test_flow) for variants:

* Without init function
* Multiple init functions
* Without filter function
* With a context initialized before run flow
* Multiple filter functions
* With modulo functions
* Without load function
