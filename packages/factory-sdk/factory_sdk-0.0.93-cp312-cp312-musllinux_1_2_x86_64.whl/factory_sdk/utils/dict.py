from typing import Dict


def clean_dict(d: Dict) -> Dict:
    """
    Remove None values from a dictionary.
    """
    return {k: v for k, v in d.items() if v is not None}
