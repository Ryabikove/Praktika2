import pandas as pd

df = pd.read_csv('dataset.csv')

def displayData(data, filename):
    print(data)
    with (open(filename, 'a', newline='', encoding='utf-8')) as file:
        file.write("\n" + data)

if __name__ == '__main__':
    displayData(df.columns.values[1], 'report.txt')