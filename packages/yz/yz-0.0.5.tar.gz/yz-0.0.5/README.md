# yz
Includes various adwords elements diagnosis functions

To install:	```pip install yz```

## Overview
The `yz` package provides a collection of functions designed to assist in diagnosing and analyzing data related to AdWords and other similar datasets. The functions in this package help in understanding the structure and characteristics of data frames, performing statistical analysis, and formatting output for reporting and inspection.

## Features
- **Data Diagnostics**: Analyze data frames to extract information about columns, such as data types, unique values, and non-null counts.
- **Comparison and Filtering**: Functions to filter and compare data based on specified conditions.
- **Statistical Analysis**: Aggregate and normalize data for detailed statistical insights.

## Functions

### `diag_df(df)`
Analyzes a DataFrame to provide a summary of each column including data type, a non-null example value, count of unique values, non-zero values, and non-NaN values.

#### Usage Example:
```python
import pandas as pd
df = pd.DataFrame({
    'A': [1, 2, None, 4],
    'B': ['a', 'b', 'b', 'c']
})
summary = diag_df(df)
print(summary)
```

### `numof(logical_series)`
Counts the number of `True` values in a logical series.

#### Usage Example:
```python
import pandas as pd
data = pd.Series([True, False, True, True])
count = numof(data)
print(count)  # Output: 3
```

### `pr_numof(data, column=None, op=ge, comp_val=0, str_format='sparse', op2str=None)`
Prints the number of elements in a specified column of a DataFrame that meet a comparison condition.

#### Usage Example:
```python
import pandas as pd
df = pd.DataFrame({'Age': [25, 30, 35, 40]})
pr_numof(df, column='Age', op=ge, comp_val=30)
```

### `cols_that_are_of_the_type(df, type_spec)`
Returns a list of columns where the type of the first element matches the specified type or meets a condition defined by a function.

#### Usage Example:
```python
import pandas as pd
df = pd.DataFrame({
    'name': ['Alice', 'Bob'],
    'age': [25, 30]
})
cols = cols_that_are_of_the_type(df, int)
print(cols)  # Output: ['age']
```

### `get_unique(d, cols=None)`
Returns a DataFrame with unique rows based on specified columns.

#### Usage Example:
```python
import pandas as pd
df = pd.DataFrame({
    'A': [1, 1, 2],
    'B': [2, 2, 2]
})
unique_df = get_unique(df)
print(unique_df)
```

### `print_unique_counts(d)`
Prints the count of unique values for each column in the DataFrame.

#### Usage Example:
```python
import pandas as pd
df = pd.DataFrame({
    'A': [1, 1, 2],
    'B': ['x', 'y', 'x']
})
print_unique_counts(df)
```

### `mk_fanout_score_df(df, fromVars, toVars, statVars=None, keep_statVars=False)`
Creates a DataFrame that scores fan-out relationships between variables.

#### Usage Example:
```python
import pandas as pd
df = pd.DataFrame({
    'Company': ['A', 'A', 'B'],
    'Product': ['X', 'Y', 'X'],
    'Sales': [100, 150, 200]
})
score_df = mk_fanout_score_df(df, fromVars=['Company'], toVars=['Product'])
print(score_df)
```

## Installation
To install the `yz` package, run the following command:
```bash
pip install yz
```

This package is essential for data scientists and analysts working with complex datasets, providing tools to simplify data diagnostics and analysis.