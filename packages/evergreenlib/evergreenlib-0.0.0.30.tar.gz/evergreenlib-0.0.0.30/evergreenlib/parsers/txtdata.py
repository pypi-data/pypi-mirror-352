import pandas as pd
import time
import chardet
from pathlib import Path
from evergreenlib.clean.cleaner import DataframeCleaner

pd.options.display.width = None


class TxtParser:
    def __init__(self, filepath: str = None, idx_value: str = None):
        self.filepath = filepath
        self.idx_value = idx_value
        self.dataframe = None

    def read_data(self):
        start = time.perf_counter()

        # Определение кодировки файла
        with open(self.filepath, 'rb') as file:
            rawdata = file.read()
            result = chardet.detect(rawdata)
            detected_encoding = result['encoding']
        print(f"Определенная кодировка: {detected_encoding}")

        # Чтение файла с использованием обнаруженной кодировки
        self.dataframe = pd.read_csv(self.filepath, encoding=detected_encoding, sep='\t', dtype=str)
        self.dataframe = self.dataframe.iloc[:, 0].str.split("|", expand=True)

        cleaner = DataframeCleaner(self.dataframe)
        cleaner.adj_by_row_index(value=self.idx_value)
        cleaner.remove_duplicated_cols()

        end = time.perf_counter()
        print(
            f'Reading file {Path(self.filepath).name} '
            f'from file: {Path(__file__).__fspath__()} took {round((end - start), 2)} seconds'
        )
        return cleaner.df


if __name__ == '__main__':
    x = TxtParser(
        r'V:\Findep\Work\FINDEP HMCIS\ARAP\2025\03_March\Accounting Data\AR_03m2025.txt','AccTy')

    x.read_data().to_clipboard()
