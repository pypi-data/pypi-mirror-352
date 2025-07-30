from ...Application.Abstractions.base_hash_token_config import BaseHashTokenConfig


class HashTokenConfig(BaseHashTokenConfig):
    
    def get_token(self, base_url:str)->str|None:
        if base_url in self._hash_token:
            return self._hash_token[base_url]
        else:
            return None
    
    def add_token(self, base_url:str, token:str)->bool:
        if base_url not in self._hash_token:
            self._hash_token[base_url] = token

            return True
        else:
            return False