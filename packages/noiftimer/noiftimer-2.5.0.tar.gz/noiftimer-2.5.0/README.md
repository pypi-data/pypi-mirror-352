# noiftimer

Simple timer class to track elapsed time.  
Install with:

```console
pip install noiftimer
```

Usage:

```python
from noiftimer import Timer, time_it, log_time
import time
```

`Timer` object:

```python
>>> def very_complicated_function():
...     time.sleep(1)
...
>>> timer = Timer()
>>> for _ in range(10):
...     timer.start()
...     very_complicated_function()
...     timer.stop()
...
>>> print(timer.stats)
elapsed time: 1s 1ms 173us
average elapsed time: 1s 912us
>>> timer.elapsed
1.001173496246338
>>> timer.elapsed_str
'1s 1ms 173us'
>>> timer.average_elapsed
1.0009121656417848
>>> timer.average_elapsed_str
'1s 912us'
```

`time_it` decorator (executes the decorated function 10 times)

```python
>>> @time_it(10)
... def very_complicated_function():
...     time.sleep(1)
...
>>> very_complicated_function()
very_complicated_function average execution time: 1s 469us
```

Alternatively, the `log_time` decorator can be used to instead log the execution time to a file.
