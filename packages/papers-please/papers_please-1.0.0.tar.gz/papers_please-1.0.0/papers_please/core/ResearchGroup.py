from .Researcher import Researcher

import pandas as pd

class ResearchGroup():
    def __init__(self, researchers:list[Researcher]):
        self._researchers = researchers
        self._papers = None

        
    @property
    def papers(self) -> pd.DataFrame:
        if self._papers is not None:
            return self._papers
        
        df = pd.DataFrame()
        for researcher in self.researchers:
            df = pd.concat([df, researcher.papers])

        return df.drop_duplicates(subset=['doi'])

    @property
    def researchers(self) -> list[Researcher]:
        return self._researchers