import hashlib
import pickle

def generate_checksum_from_obj(document: dict) -> str:
        try:
            document.pop("_id")
            document.pop("updated_at")
        except Exception:
            pass
        return hashlib.md5(pickle.dumps(sorted(document.items()))).hexdigest()
