#state_schema.py
# ✅ state_schema.py
from pydantic import BaseModel
from typing import Optional

class MyStateSchema(BaseModel):
    input: str
    output: Optional[str] = None  # <--- ligne clé

