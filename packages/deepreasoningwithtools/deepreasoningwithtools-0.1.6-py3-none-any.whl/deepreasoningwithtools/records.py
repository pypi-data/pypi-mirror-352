from pydantic import BaseModel

class StreamingResponseTokenT(BaseModel):
    text: str
    error_code: int
    num_tokens: int
    token_ids: list[int]
    last_token_id: int
    last_token: str