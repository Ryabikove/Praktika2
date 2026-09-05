import io
import pandas as pd

df = pd.read_csv('dataset.csv')
filename = 'report.txt'
numeric_cols = ['age', 'ejection fraction', 'creatinine phosphokinase', 'ejection fraction.1']
categorical_columns = ['anaemia', 'diabetes', 'high bp']

def displayData(data: list[str], file: str) -> None:
    with (open(file, 'a', newline='', encoding='utf-8')) as file:
        for line in data:
            file.write(line + '\n')
            print(line)


class DatasetAnalysis:
    dataset: pd.DataFrame

    def __init__(self, dataset: pd.DataFrame) -> None:
        self.dataset = dataset.reset_index()

    def RowsNColumnsNumb(self) -> list[str]:
        return [str(self.dataset.shape)]

    def ColumnsNTypes(self) -> list[str]:
        buffer = io.StringIO()
        self.dataset.info(verbose=True, memory_usage=False, buf=buffer)

        return [str(buffer.getvalue())]

    def EmptyRows(self) -> list[str]:
        return [str(self.dataset.isna().sum())]

    def AvgMedStandDevVal(self, numeric_columns : list[str]) -> list[str]:
        temp_dataset = self.dataset[numeric_columns]
        stats = temp_dataset.agg(['mean', 'median', 'std']).T
        stats = stats.round(2)

        return [str(stats)]

    def ListValNFreq(self) -> list[str]:
        result=[]
        for col in categorical_columns:
            result.append(str(self.dataset[col].value_counts()))

        return result

if __name__ == '__main__':
    analysis = DatasetAnalysis(df)

    displayData(analysis.RowsNColumnsNumb(), filename)
    displayData([""], filename)

    displayData(analysis.ColumnsNTypes(), filename)
    displayData([""], filename)

    displayData(analysis.EmptyRows(), filename)
    displayData([""], filename)

    displayData(analysis.AvgMedStandDevVal(numeric_cols), filename)
    displayData([""], filename)

    displayData(analysis.ListValNFreq(), filename)
