# utils/resources.py

import json
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple


def load_qwerty_map(path: Path = Path(__file__).parent.parent / "data" / "qwerty_map.json") -> Dict[str, str]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_slang_csv(path: Path = Path(__file__).parent.parent / "data" / "slang.csv") -> Tuple[Dict[str, str], Dict[str, str]]:
    df = pd.read_csv(path)
    df.columns = ["acronym", "expansion"]
    s2l = dict(zip(df.acronym.str.lower(), df.expansion.str.lower()))
    return s2l, {v: k for k, v in s2l.items()}
