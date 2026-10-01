from typing import Annotated

from pydantic import BeforeValidator

# Oracle stores empty strings as NULL, so optional text columns can come back as None.
NullableStr = Annotated[str, BeforeValidator(lambda v: "" if v is None else v)]
