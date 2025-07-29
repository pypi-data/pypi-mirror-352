import re
from collections import defaultdict
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from dateparser import parse
from pandas.tseries.offsets import MonthEnd

from evergreenlib import ExcelParser


def find_details(target_date: date, amount_in_lc: float) -> pd.DataFrame:
    eom_date = (target_date + MonthEnd(0)).date()

    base_dir = r'V:\Accounting\Work\ОТДЕЛ ЗАТРАТ\Билялова\Аренда Mobility_ФЛ\Аренда ФЛ'

    pattern = re.compile(r'2023\b|2024\b')

    def exclude_fragment(txt: str):
        lower_txt = txt.lower()
        pattern = re.compile(r'маша|куличенков|ч.2|report|final_2|final_ч2|ч2')
        if not pattern.search(lower_txt):
            return True
        return False

    latest_modified_per_month = defaultdict(lambda: (None, 0))
    latest_modified_per_file = defaultdict(lambda: (None, 0))
    for yearfolder in Path(base_dir).glob("*"):
        if pattern.search(yearfolder.name):
            for monthfolder in yearfolder.glob("*"):
                for folder in monthfolder.glob("*"):
                    if folder.is_dir():
                        mod_time = folder.stat().st_mtime
                        if mod_time > latest_modified_per_month[str(monthfolder)][1]:
                            latest_modified_per_month[str(monthfolder)] = (folder.name, mod_time)

    for month, (latest_folder, mod_time) in latest_modified_per_month.items():
        if latest_folder:
            for file in (Path(month) / latest_folder).rglob("*.xlsx"):
                if exclude_fragment(file.name) and file.name not in ['Кантри_июль 2023.xlsx',
                                                                     'Фридом_июль 2023.xlsx']:
                    mod_time_2 = file.stat().st_mtime
                    # print(mod_time_2)
                    if mod_time_2 > latest_modified_per_file[str(file)][1]:
                        latest_modified_per_file[str(file)] = (month, latest_folder, file.name)

    total_df = pd.DataFrame()
    for k, v in latest_modified_per_file.items():
        month_identificator = v[0].split("\\")[-1]
        year_identificator = v[0].split("\\")[-2]
        custom_date = (parse(month_identificator + " " + year_identificator, languages=['ru']) + MonthEnd(0)).date()
        if custom_date == eom_date:
            file_path = '\\'.join(v)
            print(f'Reading {file_path}')
            df = ExcelParser(file_path, sheet_name=r'Детальный Отчет',
                                               index_value='№ п/п').read_data()
            df.columns = df.columns.str.replace("\xa0", "").str.replace("\n", " ")

            nms = pd.Series(df.columns).str.replace("\n", " ")
            nms1 = pd.Series(df.iloc[0, :]).str.replace("\n", " ")
            nms2 = pd.Series(df.iloc[1, :]).str.replace("\n", " ")

            conds = [
                pd.isna(nms1) & pd.isna(nms2),
                pd.isna(nms.values) & pd.isna(nms1),
                pd.isna(nms.values) & pd.isna(nms2),
                pd.notna(nms.values) & pd.notna(nms1),
                pd.notna(nms1) & pd.notna(nms2),
            ]

            choices = [
                nms,
                nms2,
                nms1,
                nms1,
                nms2
            ]

            output = np.select(conds, choices)

            df.columns = output
            df.rename(columns={df.columns[1]: 'ID начисления'}, inplace=True)
            df = df[pd.notna(df['ID начисления'])]
            df['Дата начисления'] = df['Дата начисления'].map(
                lambda x: parse(x, languages=['ru']).date() if not pd.isna(x) else None)
            df['Дата и время начала сессии'] = df['Дата и время начала сессии'].map(
                lambda x: parse(x, languages=['ru']).date() if not pd.isna(x) else None)
            df['Дата и время окончания сессии'] = df['Дата и время окончания сессии'].map(
                lambda x: parse(x, languages=['ru']).date() if not pd.isna(x) else None)
            df['Дата оплаты'] = df['Дата оплаты'].map(
                lambda x: parse(x, languages=['ru']).date() if x not in [None, ""] else None)
            df['Дата оплаты (мск)'] = df['Дата оплаты (мск)'].map(
                lambda x: parse(x, languages=['ru']).date() if x not in [None, ""] else None)
            df['Source'] = file_path
            total_df = pd.concat([total_df, df])
            total_df = total_df[(total_df['Дата начисления'] == target_date) &
                                (total_df['Сумма начисления за отчетный период, руб.'] == amount_in_lc) &
                                (pd.isna(total_df['Дата оплаты (мск)']))

                                ]
            # print(df.shape)
            # print(total_df.shape)
    return total_df
