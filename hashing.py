import hashlib
from uuid import uuid4



def hashed(text: str) -> str: 
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


print("admin: ", hashed("admin"))
print("tech: ", hashed("tech"))
print("neighbor: ", hashed("neighbor"))
print("juan: ", hashed("juan"))
print("test: ", hashed("test"))
print("generated id: ", str(uuid4().hex))
print("generated id: ", str(uuid4()))
