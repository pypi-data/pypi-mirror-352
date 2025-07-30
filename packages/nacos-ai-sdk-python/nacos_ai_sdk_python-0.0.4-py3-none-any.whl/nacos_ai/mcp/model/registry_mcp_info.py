from typing import Optional

from pydantic import BaseModel


class Repository(BaseModel):
	pass

class ServerVersionDetail(BaseModel):
	version: Optional[str]
	release_date: Optional[str]
	is_latest: Optional[bool]