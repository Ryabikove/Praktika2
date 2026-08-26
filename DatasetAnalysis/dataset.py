import pandas as pd

df = pd.read_csv('dataset.csv')


def displayData(data: str, filename: str) -> None:
    print(data)
    with (open(filename, 'a', newline='', encoding='utf-8')) as file:
        file.write(data + '\n')


class DatasetAnalysis:
    dataset: pd.DataFrame
    def __init__(self, dataset: pd.DataFrame) -> None:
        self.dataset = dataset.reset_index()

    def RowsNColumnsNumb(self) -> None:
        displayData(str(self.dataset.shape), 'report.txt')


if __name__ == '__main__':
    analysis = DatasetAnalysis(df)
    analysis.RowsNColumnsNumb()