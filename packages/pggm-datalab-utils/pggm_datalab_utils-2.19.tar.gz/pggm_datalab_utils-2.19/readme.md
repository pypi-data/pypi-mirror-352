# Datalab utils
Well-specified utilities from the Datalab of PGGM. Our aim with this package is to provide some tooling to make our lives a bit easier.
So far the package contains:
- Database utilities, allowing you to connect to cloud databases using pyodbc in a standard pattern.
- Helpers around nested lists (flattening and unflattening).
- Helpers to make working with lists of dictionaries a bit easier so you don't have to resort to Pandas as fast.

## How to use the database helpers
```python
from pggm_datalab_utils.db import cursor, query

bbg_id = 'WOW'

with cursor('pggm-sql-lre-o.database.windows.net', 'lre') as c:
    data = query(c, 'select sedol, name from portfolio where bbg_id=?', bbg_id)
```