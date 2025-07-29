# sar_sdk

Python SDK for controlling SAR grippers over TCP.

## Installation

```bash
pip install sar_sdk
```

## Usage

```python
from sar_sdk import SARModule

sar = SARModule()
sar.grip_close()
```
