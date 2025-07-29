# SignalKit

SignalKit is a lightweight Python signaling library built upon the robust [Blinker](https://github.com/pallets-eco/blinker) library. It provides a simple yet flexible way to dispatch signals and handle responses, automatically adapting to your handler function signatures.

## Installation
`pip install signalkit`

## Usage Example

### Synchronous
```python
from signalkit import CoolSignal

class Event:
    def __init__(self, text: str):
        self.text = text

def handle_event(sender, event: Event) -> str:
    return event.text.upper()

def handle_payload(payload):
    return payload.upper()

signal = CoolSignal()
signal.connect(handle_event)
signal.connect(handle_payload)

event = Event("hello world")
result = signal.send(event=event)  # 'HELLO WORLD'
print(result)
result = signal.emit("hello emit")  # 'HELLO EMIT'
print(result)
```

### Asynchronous
```python
from signalkit import CoolSignalAsync
import asyncio

class Event:
    def __init__(self, text: str):
        self.text = text

async def handle_event_async(sender, event: Event) -> str:
    return event.text.upper()

async def handle_payload_async(payload):
    return payload.upper()

signal = CoolSignalAsync()
signal.connect(handle_event_async)
signal.connect(handle_payload_async)

async def main():
    event = Event("hello async")
    result = await signal.send(event=event)  # 'HELLO ASYNC'
    print(result)
    result = await signal.emit("hello async emit")  # 'HELLO ASYNC EMIT'
    print(result)

asyncio.run(main())
```

## Benchmark Results

```
------------------------------------------------------------------------------------------------- benchmark: 10 tests -------------------------------------------------------------------------------------------------
Name (time in us)                                     Min                 Max               Mean            StdDev             Median               IQR            Outliers  OPS (Kops/s)            Rounds  Iterations
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
test_signal_performance_with_exception             3.2000 (1.0)       66.5000 (1.81)      3.8896 (1.0)      1.5917 (1.0)       3.6000 (1.0)      0.3000 (1.50)    1915;4411      257.0982 (1.0)       69931           1
test_signal_performance_varied_handlers[1000]      3.4000 (1.06)     113.4000 (3.08)      3.9687 (1.02)     1.7224 (1.08)      3.7000 (1.03)     0.2000 (1.0)     2120;7051      251.9693 (0.98)      85471           1
test_signal_performance_varied_handlers[100]       3.4000 (1.06)     163.3000 (4.44)      4.1366 (1.06)     2.2271 (1.40)      3.8000 (1.06)     0.2000 (1.00)    3044;7284      241.7465 (0.94)      84746           1
test_signal_performance_varied_handlers[10]        3.4000 (1.06)     236.3000 (6.42)      4.1971 (1.08)     2.2533 (1.42)      3.8000 (1.06)     0.4000 (2.00)    3060;5749      238.2570 (0.93)      79366           1
test_signal_performance_varied_handlers[1]         3.4000 (1.06)     154.3000 (4.19)      4.2039 (1.08)     2.2521 (1.41)      3.8000 (1.06)     0.3000 (1.50)    3463;6809      237.8722 (0.93)      85471           1
test_signal_performance                            3.9000 (1.22)      36.8000 (1.0)       4.8123 (1.24)     2.4681 (1.55)      4.2000 (1.17)     0.4000 (2.00)      523;909      207.7994 (0.81)      11099           1
test_signal_performance_with_return                4.4000 (1.38)     160.9000 (4.37)      5.4575 (1.40)     2.8904 (1.82)      4.9000 (1.36)     0.4000 (2.00)    3086;6667      183.2346 (0.71)      74627           1
test_signal_disconnect_performance                11.5000 (3.59)     231.0000 (6.28)     14.4356 (3.71)     4.9942 (3.14)     13.0000 (3.61)     1.4000 (7.00)    2926;5351       69.2731 (0.27)      40323           1
test_signal_connect_performance                   13.8000 (4.31)     230.1000 (6.25)     16.5758 (4.26)     5.7558 (3.62)     15.1000 (4.19)     1.0000 (5.00)    1259;2324       60.3287 (0.23)      19084           1
test_signal_performance_large_payload             21.6000 (6.75)      87.6000 (2.38)     25.2284 (6.49)     6.4509 (4.05)     22.8000 (6.33)     2.3000 (11.50)     316;425       39.6378 (0.15)       3178           1
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Legend:
  Outliers: 1 Standard Deviation from Mean; 1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd Quartile.
  OPS: Operations Per Second, computed as 1 / Mean
