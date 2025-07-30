# x13py

Python wrapper for the US Census Bureau's X-13ARIMA-SEATS tool.

## How to use

```python
from x13py import X13

data = [100, 102, 105, 108, 110]
x = X13()
x.write_spc(data)
x.run()
df = x.get_adjusted()
print(df)
