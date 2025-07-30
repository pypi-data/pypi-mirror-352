# Data Flag Protocol (DFP)

A lightweight TCP-based messaging protocol for structured communication using flags like `PING`, `SEND`, `LOGIN`, etc.

## Installation

```bash
pip install dfp-protocol
```

## Usage

```python
from dfp import DFPClient
client = DFPClient()
client.connect()
print(client.send("PING", "Hello"))
```
