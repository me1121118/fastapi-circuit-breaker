# ⚡ fastapi-circuit-breaker

[![FastAPI](https://img.shields.io/badge/FastAPI-Supported-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Resilience: Fault-Tolerant](https://img.shields.io/badge/Resilience-Fault--Tolerant-success.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)]()

> Lightweight, async circuit breaker decorator with graceful fallback handling for FastAPI applications.

Prevent cascading outages when external dependencies (OpenAI, Stripe, Payment Gateways, Microservices) slow down or crash.

---

### ☕ Support My Studies / Buy Me a Coffee

Hey there! 👋 I build and open-source lightweight, focused developer tools.

If this small package helped make your microservices resilient, please consider supporting my college/tuition fund:
- ☕ **Buy Me a Coffee:** [buymeacoffee.com/yourname](https://www.buymeacoffee.com)
- 💖 **Ko-fi:** [buymeacoffee.com/kcidi4148](https://buymeacoffee.com/kcidi4148)
- ⭐ **Star this repository** to help other developers discover it!

---

## 📦 Installation

```bash
pip install git+https://github.com/me1121118/fastapi-circuit-breaker.git
```

---

## 🚀 Quick Example

```python
from fastapi import FastAPI
from fastapi_circuit_breaker import circuit_breaker

app = FastAPI()

async def cached_exchange_rates():
    return {"rates": {"USD": 1.0, "EUR": 0.92}, "source": "cached_fallback"}

@app.get("/rates")
@circuit_breaker(failure_threshold=3, recovery_timeout=30.0, fallback=cached_exchange_rates)
async def get_rates():
    # If the external bank API fails 3 times in a row, the circuit trips OPEN.
    # Subsequent calls immediately return cached_exchange_rates without hanging or crashing!
    return await call_flaky_banking_api()
```

---

## 🧪 Testing

```bash
pytest -v tests
```

---

## 📄 License

MIT License. Free for personal and commercial use.
