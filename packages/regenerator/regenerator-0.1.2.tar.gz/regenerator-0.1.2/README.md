# regenerator
Create a reusable generator.

Depending on your process, it is likely faster to simply run the code to create your generator to create a "copy". However, if all you have is the generator itself, the `regenerator` package can create a copy. For large iterables, it is expected that copying the generator will offer speed-up. Furthermore, generators can be copied multiple times. The use-case therefore is in operations that need to be repeated, but creating a list out of the generator is too expensive.


## Example use

```
# Import
from regenerator import Regenerator

# Create a generator
generator = (x for x in range(10))

# Create a Regenerator from generator
regenerator = Regenerator(generator)

# Run through generator once
for x in regenerator:
    print(x)

# Run through the generator again
for x in regenerator:
    print(x)

...
```


## Installation

This package is available through pip,

```
pip install regenerator
```


