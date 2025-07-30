class BaseHashTokenConfig():
    def __init__(self):
        self._hash_token:dict[tuple, str] = {}

    def get_token(self, base_url:str)->str|None:
        ...
    
    def add_token(self, base_url:str, token:str)->bool:
        ...