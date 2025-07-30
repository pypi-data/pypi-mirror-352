# Richerator

Use [`rich`](https://github.com/Textualize/rich) to create a [`tqdm`](https://github.com/tqdm/tqdm)-like iterator wrapper that hacks the print statement to print into a live-updating rich panel.

# Install

`pip install richerator`

# Example

```python
from richerator import richerator

for x in richerator(range(1, 31), description="Looping Demo"):
    print(f"step {x}")
    print("  detail A", "detail B", sep=" | ")
    if x % 3 == 0:
        print(f"  detail C")
        time.sleep(0.5)

    time.sleep(0.1)
```

gives

![example](richerator_example.gif)

# todo

- [ ] TODO auto save repeated outputs to a file if want to keep track of each iteration's output
 
