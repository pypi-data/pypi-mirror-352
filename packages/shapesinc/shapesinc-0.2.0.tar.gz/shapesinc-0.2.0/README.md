# shapesinc-py

## Installation

From PyPI:
```
pip install shapesinc -U
```

From GitHub:
```
pip install git+https://github.com/Rishiraj0100/shapesinc-py.git
```

## Examples

### Synchronous Shape Example
```py
from shapesinc import (
  shape,
  ShapeUser as User,
  ShapeChannel as Channel
)

my_shape = shape("API_KEY", "my_shape")
user = User("u0")
channel = Channel("cli")

while True:
  inp = input(" >>> ")
  r = my_shape.prompt(inp, user = user, channel=channel)
  print(r.choices[0].message)
```
### Asynchronous Shape Example
```py
from shapesinc import (
  shape,
  ShapeUser as User,
  ShapeChannel as Channel
)

my_shape = shape("API_KEY", "my_shape", synchronous=False)
user = User("u0")
channel = Channel("cli")

async def run():
  while True:
    inp = input(" >>> ")
    r = await my_shape.prompt(inp, user = user, channel=channel)
    print(r.choices[0].message)

import asyncio
asyncio.run(run())
```
### Image Examples
```py
from shapesinc import Message, MessageContent, ContentType as C

msg = Message.new("Explain this image!", [dict(url = "URL OF IMAGE", type = c.image)])

resp = my_shape.prompt(msg)
```
### Audio Messages
```py
from shapesinc import Message, MessageContent, ContentType as C

msg = Message.new(files = [dict(url = "URL OF AUDIO FILE", type = c.audio)])

resp = my_shape.prompt(msg)
```

## Note
- When both audio and image files are given in one message, only audio will be processed!
- Commands like `!wack` can be normally used with `Shape.prompt` method.
