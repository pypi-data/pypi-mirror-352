import pandas as pd
from bs4 import BeautifulSoup

from .hyperpattern import HyperPatternHunter


def find_and_create_hyperframes(html: str) -> list[pd.DataFrame]:
    soup = BeautifulSoup(html, "lxml")
    hyperpatterns = HyperPatternHunter(soup).yield_hyperpatterns()
    return [hyperpattern.get_hyperframe() for hyperpattern in hyperpatterns]
