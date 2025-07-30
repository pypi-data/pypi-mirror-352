import json
from typing import Type

class Serialization:
	def Encoder(obj, indent:str|None = None) -> str:
		if hasattr(obj, '__json__') and callable(obj.__json__):
			return json.dumps(obj.__json__(), indent=indent)
		else:
			return json.dumps(obj.__dict__, indent=indent)

	def Decoder(obj:dict, toType:Type):
		returnValue: any = None
		if (toType is not None):
			returnValue = toType()
			for key, value in obj.items():
				setattr(returnValue, key, value)
		return returnValue

__all__ = ["Serialization"]
