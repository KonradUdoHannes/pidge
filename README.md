# pidge

pidge helps with the creation of mappings for tabular string data. The primary use cases for
this are data cleaning and data categorization.

pidge consists out of two parts:

1. An interactive UI to help with the creation of mappings and assessing their completeness
2. Library functionality to apply mappings inside of data pipelines, after they have been exported from the UI


## Usage

1. install `pidge`

        pip install pidge

1. Launch the UI in a notebook

    ```python
    from pidge import pidge_ui
    import panel as pn

    pn.extensions('tabulator','jsoneditor')

    pidge_ui(my_input_dataframe)
    ```

1. Create and export a mapping named `pidge_mapping.json`

1. In your data pipeline import `pidge` and apply the mapping

    ```python
    from pidge import pidge

    transformed_data = pidge(my_input_dataframe,rule_file= 'pidge_mapping.json')
    ```

### The web-ui outside of Jupyter

Pidge can also run the UI as a standalone web server outside of jupyter, using the command.

> python -m pidge

This starts up the UI in a local web server, which is primarily intended for illustration purposes.
Therefore it starts up with example data already loaded. However new data can be loaded and the
predefined rules can easily be reset. The main limitation at this moment, however, is the
constraint on the upload format for data. It only supports `.csv` and reads it with default
`pandas.read_csv` settings.

## Mapping Logic

Pidge mappings map a source string column to a newly created target string column. The logic can
be broken down as follows.

1. One defines a possible value, a category, for the target column.
1. One associates one or more patterns with that category.
1. When a value of the source column matches one of the category's patterns, that category is chosen.
1. Pattern matching checks whether the pattern is part of the source string. It is case insensitive
    and allows for regular expressions.
1. This is repeated for as many categories as desired.


## Contribution

Pidge is in an early MVP stage. At this stage the following is particularly appreciated

1. Any feedback regarding, bugs, issues usability feature requests etc. Ideally this can be done directly
    as github issues.
1. Any sharing of the project to potentially help with the previous point.

## Known Limitations

There are a few known limitations particularly due to the MVP stage of the project. These
will be prioritized according to feedback and general usage of the project.

- Mapping is not optimized for speed at all and might slow down for large dataframes
- Patterns do not check for multiple inconsistent matches and simply the first applicable pattern
    is chosen
- the web-ui does only support small file uploads (around < 10Mb).
- file uploads can only read in the data with `pandas.read_csv` default settings
- The rule name used for the .json export can currently not be changed in the UI.
