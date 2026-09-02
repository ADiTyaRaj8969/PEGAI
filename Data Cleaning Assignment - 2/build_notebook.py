"""
Builds Data_Cleaning_Assignment.ipynb by actually executing each cleaning
step against titanic.csv and embedding the real printed output as the
cell's result, so the notebook already shows genuine before/after results.
"""
import io
import json
import contextlib

PROMPTS = []

def add(prompt_md, code):
    PROMPTS.append((prompt_md.strip(), code.strip("\n")))


# ---------------------------------------------------------------------------
add("""### Prompt 1: Load the dataset and inspect its basic structure
Load `titanic.csv` (downloaded from
https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv)
into a pandas DataFrame and display its shape, column names, data types and
the first few rows.""", """
import pandas as pd
import numpy as np

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 120)

df = pd.read_csv('titanic.csv')
original_df = df.copy()  # keep an untouched copy for before/after comparison

print("Shape (rows, columns):", df.shape)
print("\\nColumn names:", list(df.columns))
print("\\nData types:\\n", df.dtypes)
print("\\nFirst 5 rows:\\n", df.head())
""")

# ---------------------------------------------------------------------------
add("""### Prompt 2: Get an overall summary / profile of the dataset
Use `.info()` and `.describe()` to understand numeric ranges, counts and
possible data quality issues before cleaning anything.""", """
print(df.info())
print("\\nNumeric summary:\\n", df.describe())
print("\\nCategorical summary:\\n", df.describe(include=['object']))
""")

# ---------------------------------------------------------------------------
add("""### Prompt 3: Detect missing values in every column
Compute the count and percentage of missing values per column and identify
which columns need attention.""", """
missing_count = df.isnull().sum()
missing_pct = (missing_count / len(df) * 100).round(2)
missing_report = pd.DataFrame({'missing_count': missing_count,
                                'missing_pct': missing_pct})
missing_report = missing_report[missing_report['missing_count'] > 0] \\
                    .sort_values('missing_count', ascending=False)
print(missing_report)
""")

# ---------------------------------------------------------------------------
add("""### Prompt 4: Impute missing 'Age' values intelligently
Instead of a single global mean, fill missing `Age` using the median age of
each `Pclass`/`Sex` group, which is more representative than one overall
statistic.""", """
print("Missing Age before:", df['Age'].isnull().sum())

df['Age'] = df.groupby(['Pclass', 'Sex'])['Age'] \\
              .transform(lambda s: s.fillna(s.median()))

print("Missing Age after:", df['Age'].isnull().sum())
print("\\nAge summary after imputation:\\n", df['Age'].describe())
""")

# ---------------------------------------------------------------------------
add("""### Prompt 5: Impute missing 'Embarked' values using the mode
`Embarked` only has a couple of missing values, so fill them with the most
frequent port of embarkation.""", """
print("Missing Embarked before:", df['Embarked'].isnull().sum())
print("Value counts before:\\n", df['Embarked'].value_counts(dropna=False))

mode_embarked = df['Embarked'].mode()[0]
df['Embarked'] = df['Embarked'].fillna(mode_embarked)

print("\\nFilled missing Embarked with mode:", mode_embarked)
print("Missing Embarked after:", df['Embarked'].isnull().sum())
""")

# ---------------------------------------------------------------------------
add("""### Prompt 6: Handle the heavily-missing 'Cabin' column
`Cabin` is missing for ~77% of passengers, so instead of imputing a fake
value, engineer a useful binary feature `Has_Cabin` and a `Deck` feature
(first letter of the cabin code, 'Unknown' if missing).""", """
print("Missing Cabin before:", df['Cabin'].isnull().sum(),
      f"({df['Cabin'].isnull().mean()*100:.2f}%)")

df['Has_Cabin'] = df['Cabin'].notnull().astype(int)
df['Deck'] = df['Cabin'].str[0].fillna('Unknown')

print("\\nHas_Cabin value counts:\\n", df['Has_Cabin'].value_counts())
print("\\nDeck value counts:\\n", df['Deck'].value_counts())
""")

# ---------------------------------------------------------------------------
add("""### Prompt 7: Detect and remove duplicate rows
Check whether the dataset contains fully duplicated rows or duplicated
passenger identifiers, and remove them.""", """
full_dupes = df.duplicated().sum()
id_dupes = df['PassengerId'].duplicated().sum()
print("Fully duplicated rows:", full_dupes)
print("Duplicated PassengerId values:", id_dupes)

before_rows = len(df)
df = df.drop_duplicates()
print(f"\\nRows before: {before_rows}, rows after drop_duplicates: {len(df)}")
""")

# ---------------------------------------------------------------------------
add("""### Prompt 8: Standardize inconsistent text formatting
Strip stray whitespace and normalize the case of text/categorical columns
(`Name`, `Sex`, `Embarked`) so values compare and group correctly.""", """
print("Sex categories before:", df['Sex'].unique())
print("Embarked categories before:", df['Embarked'].unique())

df['Name'] = df['Name'].str.strip()
df['Sex'] = df['Sex'].str.strip().str.lower()
df['Embarked'] = df['Embarked'].str.strip().str.upper()

print("\\nSex categories after:", df['Sex'].unique())
print("Embarked categories after:", df['Embarked'].unique())
""")

# ---------------------------------------------------------------------------
add("""### Prompt 9: Extract a 'Title' feature from the 'Name' text field
Parse each passenger's honorific title (Mr, Mrs, Miss, etc.) out of the
free-text `Name` column and collapse rare titles into an 'Other' bucket.""", """
df['Title'] = df['Name'].str.extract(r',\\s*([^.]*)\\.')[0].str.strip()
print("Raw title counts:\\n", df['Title'].value_counts())

common_titles = {'Mr', 'Mrs', 'Miss', 'Master'}
df['Title'] = df['Title'].apply(lambda t: t if t in common_titles else 'Other')

print("\\nCleaned title counts:\\n", df['Title'].value_counts())
""")

# ---------------------------------------------------------------------------
add("""### Prompt 10: Convert columns to appropriate data types
`Survived`, `Pclass`, `Sex`, `Embarked`, `Title` and `Deck` are categorical
in nature even though some are stored as integers/strings — convert them to
pandas `category` dtype to save memory and make intent explicit.""", """
print("Memory usage before:\\n", df.memory_usage(deep=True).sum(), "bytes")

cat_cols = ['Survived', 'Pclass', 'Sex', 'Embarked', 'Title', 'Deck']
for col in cat_cols:
    df[col] = df[col].astype('category')

print("\\nDtypes after conversion:\\n", df.dtypes)
print("\\nMemory usage after:", df.memory_usage(deep=True).sum(), "bytes")
""")

# ---------------------------------------------------------------------------
add("""### Prompt 11: Detect outliers in 'Fare' using the IQR method
Compute Q1, Q3 and the interquartile range to flag fares that fall far
outside the typical range.""", """
Q1 = df['Fare'].quantile(0.25)
Q3 = df['Fare'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

outliers = df[(df['Fare'] < lower_bound) | (df['Fare'] > upper_bound)]
print(f"Q1={Q1:.2f}, Q3={Q3:.2f}, IQR={IQR:.2f}")
print(f"Valid range: [{lower_bound:.2f}, {upper_bound:.2f}]")
print(f"Number of Fare outliers: {len(outliers)} ({len(outliers)/len(df)*100:.2f}%)")
print("\\nSample outlier fares:\\n", outliers['Fare'].sort_values(ascending=False).head())
""")

# ---------------------------------------------------------------------------
add("""### Prompt 12: Treat 'Fare' outliers by capping (winsorizing)
Rather than deleting outlier rows and losing data, cap extreme fares at the
IQR bounds computed in the previous step.""", """
print("Fare stats before capping:\\n", df['Fare'].describe())

df['Fare'] = df['Fare'].clip(lower=lower_bound, upper=upper_bound)

print("\\nFare stats after capping:\\n", df['Fare'].describe())
""")

# ---------------------------------------------------------------------------
add("""### Prompt 13: Detect outliers in 'Age' using the Z-score method
Use standard scores to flag passengers whose age is more than 3 standard
deviations from the mean.""", """
z_scores = (df['Age'] - df['Age'].mean()) / df['Age'].std()
age_outliers = df[z_scores.abs() > 3]

print(f"Mean age: {df['Age'].mean():.2f}, Std: {df['Age'].std():.2f}")
print(f"Number of Age outliers (|z|>3): {len(age_outliers)}")
print("\\nOutlier ages:\\n", age_outliers['Age'].sort_values(ascending=False))
""")

# ---------------------------------------------------------------------------
add("""### Prompt 14: Validate logical/range constraints
Confirm that `Age`, `Fare`, `SibSp` and `Parch` never hold impossible
negative values, and flag/fix any row that violates the constraint.""", """
constraints = {
    'Age': df['Age'] < 0,
    'Fare': df['Fare'] < 0,
    'SibSp': df['SibSp'] < 0,
    'Parch': df['Parch'] < 0,
}
for col, mask in constraints.items():
    n_invalid = mask.sum()
    print(f"{col}: {n_invalid} invalid (negative) values")
    if n_invalid:
        df.loc[mask, col] = np.nan

print("\\nAll range constraints satisfied:",
      all((df[c] >= 0).all() for c in constraints))
""")

# ---------------------------------------------------------------------------
add("""### Prompt 15: Engineer 'FamilySize' and 'IsAlone' features
Combine `SibSp` and `Parch` into a single family-size measure and derive a
boolean flag for passengers travelling alone — useful, analysis-ready
features that don't exist in the raw data.""", """
df['FamilySize'] = df['SibSp'] + df['Parch'] + 1
df['IsAlone'] = (df['FamilySize'] == 1).astype(int)

print(df[['SibSp', 'Parch', 'FamilySize', 'IsAlone']].head(10))
print("\\nIsAlone distribution:\\n", df['IsAlone'].value_counts())
""")

# ---------------------------------------------------------------------------
add("""### Prompt 16: Encode categorical variables for modeling
Apply label encoding to the binary `Sex` column and one-hot encoding to the
multi-class `Embarked` column so the dataset is ready for machine-learning
use.""", """
df['Sex_encoded'] = df['Sex'].map({'male': 0, 'female': 1})

embarked_dummies = pd.get_dummies(df['Embarked'], prefix='Embarked')
df = pd.concat([df, embarked_dummies], axis=1)

print(df[['Sex', 'Sex_encoded']].drop_duplicates())
print("\\nOne-hot encoded Embarked columns:\\n",
      df[list(embarked_dummies.columns)].head())
""")

# ---------------------------------------------------------------------------
add("""### Prompt 17: Drop irrelevant / redundant columns
Remove identifier and free-text columns (`PassengerId`, `Ticket`, `Name`,
`Cabin`) that carried no direct analytical value once their useful
information (Title, Deck, Has_Cabin) has already been extracted.""", """
cols_to_drop = ['PassengerId', 'Ticket', 'Name', 'Cabin']
print("Columns before drop:", list(df.columns))

df = df.drop(columns=cols_to_drop)

print("\\nColumns after drop:", list(df.columns))
print("New shape:", df.shape)
""")

# ---------------------------------------------------------------------------
add("""### Prompt 18: Reduce skewness in 'Fare' with a log transform
Right-skewed monetary values like `Fare` distort statistics and models —
compare skewness before and after applying `log1p` and keep the
transformed version as a new column.""", """
skew_before = df['Fare'].skew()
df['Fare_log'] = np.log1p(df['Fare'])
skew_after = df['Fare_log'].skew()

print(f"Skewness of Fare before log transform: {skew_before:.3f}")
print(f"Skewness of Fare after log1p transform: {skew_after:.3f}")
print("\\n", df[['Fare', 'Fare_log']].describe())
""")

# ---------------------------------------------------------------------------
add("""### Prompt 19: Rename columns to a consistent snake_case convention
Standardize column naming across the whole DataFrame so downstream code and
SQL exports don't have to juggle mixed CamelCase / PascalCase names.""", """
import re

def to_snake_case(name):
    name = re.sub(r'(?<!^)(?=[A-Z])', '_', name)
    return name.lower()

print("Columns before renaming:\\n", list(df.columns))

df.columns = [to_snake_case(c) for c in df.columns]

print("\\nColumns after renaming:\\n", list(df.columns))
""")

# ---------------------------------------------------------------------------
add("""### Prompt 20: Final validation and export the cleaned dataset
Run a last missing-value / duplicate check, compare the cleaned dataset
against the original raw file, and save the result to
`titanic_cleaned.csv`.""", """
print("=== FINAL VALIDATION ===")
print("Remaining missing values:\\n", df.isnull().sum()[df.isnull().sum() > 0])

feature_dupes = df.duplicated().sum()
print(f"\\nRows sharing identical values across all remaining feature columns: {feature_dupes}")
print("These are NOT re-run duplicates of Prompt 7 (which found 0 exact-row")
print("duplicates on the raw data). They appear only now because Prompt 17")
print("dropped the identifying columns (PassengerId, Name, Ticket, Cabin) -")
print("distinct real passengers can legitimately share the same Pclass/Sex/")
print("Age/Fare/etc. profile, so these rows are kept rather than dropped.")

print("\\n=== BEFORE vs AFTER SUMMARY ===")
print(f"Original shape : {original_df.shape}")
print(f"Cleaned shape  : {df.shape}")
print(f"Original missing values (total): {original_df.isnull().sum().sum()}")
print(f"Cleaned missing values (total) : {df.isnull().sum().sum()}")
print(f"Original memory usage: {original_df.memory_usage(deep=True).sum()} bytes")
print(f"Cleaned memory usage : {df.memory_usage(deep=True).sum()} bytes")

df.to_csv('titanic_cleaned.csv', index=False)
print("\\nSaved cleaned dataset to 'titanic_cleaned.csv'")
""")


def run_and_build():
    namespace = {}
    cells = [{
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# Data Cleaning Assignment 2 — 20 Prompts and Results\n",
            "\n",
            "**Dataset:** Titanic passenger dataset, downloaded from\n",
            "[datasciencedojo/datasets](https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv)\n",
            "(`titanic.csv`, 891 rows x 12 columns).\n",
            "\n",
            "Each numbered prompt below states a data-cleaning task; the code cell\n",
            "immediately under it performs the task on a *live* DataFrame (state\n",
            "carries over from one prompt to the next) and the printed output shows\n",
            "the real before/after result."
        ]
    }]

    for prompt_md, code in PROMPTS:
        cells.append({
            "cell_type": "markdown",
            "metadata": {},
            "source": [line + "\n" for line in prompt_md.split("\n")][:-1] + [prompt_md.split("\n")[-1]]
        })

        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                exec(compile(code, "<cell>", "exec"), namespace)
        except Exception as e:
            buf.write(f"\n[ERROR while executing this cell]: {type(e).__name__}: {e}\n")

        output_text = buf.getvalue()
        source_lines = code.split("\n")
        source = [line + "\n" for line in source_lines[:-1]] + [source_lines[-1]]

        cells.append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [{
                "output_type": "stream",
                "name": "stdout",
                "text": [line + "\n" for line in output_text.split("\n")[:-1]] +
                        ([output_text.split("\n")[-1]] if output_text.split("\n")[-1] else [])
            }] if output_text else [],
            "source": source
        })

    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.11.9"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

    with open("Data_Cleaning_Assignment.ipynb", "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=1)

    print("Notebook written: Data_Cleaning_Assignment.ipynb")


if __name__ == "__main__":
    run_and_build()
