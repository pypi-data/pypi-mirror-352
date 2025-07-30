import json
from typing import Type
from collections.abc import Iterable
from collections import UserList

class Serialization:
	@staticmethod
	def Encoder(obj, indent:str|None = None) -> str|None:
		jsonSerializable:dict|list|None = None
		if (isinstance(obj, Iterable)):
			jsonSerializable = list()
			for item in obj:
				if (hasattr(item, '__json__') and callable(item.__json__)):
					jsonSerializable.append(item.__json__())
				else:
					jsonSerializable.append(item.__dict__())
		else:				
			if (hasattr(obj, '__json__') and callable(obj.__json__)):
				jsonSerializable = obj.__json__()
			else:
				jsonSerializable = obj.__dict__
		if (jsonSerializable is not None):
			return json.dumps(jsonSerializable, indent=indent)
		else:
			return None

	@staticmethod
	def Decoder(obj:dict|list[dict], toType:Type, toChildType:Type|None=None):
		returnValue: any = None
		if (toType is not None):
			returnValue = toType()
			if (isinstance(obj, list)
	   			and toChildType is None):
				raise TypeError(f"toChildType must be specified for obj of list.")
			if (isinstance(toType, Iterable)
	   			and not hasattr(returnValue, 'append')):
				raise TypeError(f"Object of type {toType.__name__} does not have a method named append")
			if (not isinstance(obj, list) and not isinstance(toType, Iterable)):
				for key, value in obj.items():
					setattr(returnValue, key, value)
			elif (isinstance(obj, list)
				and hasattr(returnValue, 'append')
				and toChildType is not None):
				for item in obj:
					returnValueChild = toChildType()
					for key, value in item.items():
						setattr(returnValueChild, key, value)
					returnValue.append(returnValueChild)
		return returnValue

__all__ = ["Serialization"]
