from .query_tools import *
def add_data_point(df, data_point,header=None):
    """
    Adds a data point and its header to the next available column in the Excel file.

    Parameters:
        file_path (str): The path to the Excel file.
        header (str): The header for the data point.
        data_point (str or numeric): The data point to add.
    
    Returns:
        None: The function updates the Excel file directly.
    """
    # Ensure the file exists or create a new DataFrame if it doesn't
    df = get_df(df)
    # Check if the header already exists
    if header in df.columns:
        # Find first empty row in the existing column
        empty_row = df[header].isna().idxmax() if not df[header].dropna().empty else 0
        df.at[empty_row, header] = data_point
    else:
        # Add new column with the header and place the data point at the first row
        df[header] = pd.Series([data_point] + [None] * (len(df) - 1))
    
    # Save the updated DataFrame back to the Excel file
    return df
def add_or_update_headers(df, column_name, default_value=None):
    """
    Add a new column to a DataFrame with a default value if it does not already exist.

    Parameters:
    df (DataFrame): The DataFrame to modify.
    column_name (str): The name of the column to add.
    default_value (Any, optional): The default value to assign to the new column. Defaults to None.

    Returns:
    DataFrame: The modified DataFrame with the new column added if it didn't exist.
    """
    if column_name not in df.columns:
        df[column_name] = default_value
    else:
        print(f"Column '{column_name}' already exists in the DataFrame. No changes made.")

    return df
def does_not_equal_in_list(obj,list_objs):
    for list_obj in list_objs:
        if obj == list_obj:
            return False
    return True
def update_or_append_data(df_new_data=None, df_existing_data=None, search_column=None, search_value=None, clear_duplicates=False):
    df_new = get_df(df_new_data)
    df_existing = get_df(df_existing_data)
    
    if df_existing.empty:
        return df_new

    # Ensure new data columns exist in the existing dataframe, add if not
    for col in df_new.columns:
        if col not in df_existing.columns:
            df_existing[col] = pd.NA  # Use pd.NA for missing data

    if search_column and search_value:
        if isinstance(search_column, list) and isinstance(search_value, list):
            mask = pd.Series(True, index=df_existing.index)
            for col, val in zip(search_column, search_value):
                mask &= (df_existing[col] == val)
        else:
            mask = (df_existing[search_column] == search_value)

        if does_not_equal_in_list(mask,['',' ',[],None,'none','None']):
            # Update existing rows based on mask
            for col in df_new.columns:
                df_existing.loc[mask, col] = df_new.loc[df_new.index[0], col]
            print(f"Updated rows where {search_column} matches {search_value}.")
        else:
            # Append new data if no matching row is found
            df_existing = pd.concat([df_existing, df_new], ignore_index=True)
            print(f"Appended new data as no existing match found for {search_value}.")

        # Handle duplicates update
        if not clear_duplicates:
            first_indices = df_existing.drop_duplicates(subset=search_column, keep='first').index
            update_mask = ~df_existing.index.isin(first_indices)
            for col in df_existing.columns:
                df_existing.loc[update_mask, col] = df_existing.loc[df_existing[df_existing[search_column] == df_existing.loc[update_mask, search_column]].index[0], col]

            print("Updated duplicates to match the first occurrence.")
    else:
        df_existing = pd.concat([df_existing, df_new], ignore_index=True)
        print("Appended new data as no search criteria provided.")

    if clear_duplicates:
        df_existing = df_existing.drop_duplicates()
        print("Duplicates removed after update/append.")

    return df_existing
def get_min_max_from_query(query):
    query = [return_float_or_int(obj) for obj in make_list(query) if is_number(obj)]
    query.sort()
    minimum = get_number(safe_get(query,0))
    maximum = get_number(safe_get(query,-1))
    minimum = minimum if len(query) > 0 and minimum is not None else 0
    maximum = maximum if len(query) > 1 and maximum is not None else 900
    return minimum,maximum

def search_df_for_values(df, column_name, query_list, type_dependent=False):
    """
    Search DataFrame column for rows matching any items in query_list with optional type-dependent matching.

    Parameters:
    - df (pd.DataFrame): The DataFrame to search.
    - column_name (str): The name of the column to search.
    - query_list (list or single value): A list of values or a single value to search for in the column.
    - type_dependent (bool): Whether to enforce type matching.

    Returns:
    - pd.DataFrame: A DataFrame of rows where the column values match any item in the query_list.
    """
    df = pd.DataFrame(df)  # Ensure it is a DataFrame
    query_list = make_list(query_list)

    if type_dependent:
        # Enforcing exact type matching
        mask = df[column_name].apply(lambda x: any([x == item and type(x) == type(item) for item in query_list]))
    else:
        # Attempt to convert query values to the column data type for accurate comparison
        column_dtype = df[column_name].dtype
        converted_query_list = [convert_value(item, column_dtype) for item in query_list]
        mask = df[column_name].isin(converted_query_list)

    return df[mask]

def search_df_with_condition(df, column_name, condition_func):
    """
    Search DataFrame column to find rows where condition_func returns True.

    Parameters:
    - df (pd.DataFrame): The DataFrame to search.
    - column_name (str): The column to apply the condition on.
    - condition_func (function): A function that takes a single value and returns True or False.

    Returns:
    - pd.DataFrame: A DataFrame of rows where the column values satisfy the condition_func.
    """
    df=get_df(df)
    # Applying the condition function vectorized
    mask = df[column_name].apply(condition_func)
    return df[mask]
def query_dataframe(df, query_string):
    """
    Use DataFrame.query() to filter rows based on a query string.

    Parameters:
    - df (pd.DataFrame): The DataFrame to query.
    - query_string (str): The query string to evaluate.

    Returns:
    - pd.DataFrame: The filtered DataFrame.
    """
    return df.query(query_string)
def filter_and_deduplicate_df(df, filter_columns, filter_values, dedup_columns=None):
    """
    Filters a DataFrame based on specified values in given columns and removes duplicates.

    Parameters:
    - df (pd.DataFrame): The DataFrame to filter and deduplicate.
    - filter_columns (list of str): Column names to apply the filters on.
    - filter_values (list of list): Lists of values to include for each column in filter_columns.
    - dedup_columns (list of str, optional): Columns to consider for dropping duplicates. If not specified,
      duplicates will be dropped based on all columns.

    Returns:
    - pd.DataFrame: The filtered and deduplicated DataFrame.
    """
    # Ensure the input integrity
    assert len(filter_columns) == len(filter_values), "Each filter column must correspond to a list of filter values."

    # Apply filters based on the columns and corresponding values
    mask = pd.Series([True] * len(df))
    for col, vals in zip(filter_columns, filter_values):
        mask &= df[col].isin(vals)

    filtered_df = df[mask]

    # Drop duplicates based on specified columns
    if dedup_columns:
        deduplicated_df = filtered_df.drop_duplicates(subset=dedup_columns)
    else:
        deduplicated_df = filtered_df.drop_duplicates()

    return deduplicated_df
async def get_range(df, column,query,inverseOption=False,caseOption=False,substringOption=False):
    """
    Filters the DataFrame based on numeric ranges specified in query.
    Optionally inverts the filter to exclude the specified range.
    
    :param df: DataFrame or path to DataFrame
    :param column: Column name to apply the range filter on
    :param query: List or tuple containing the minimum and maximum values as strings
    :param invert: If True, the range is inverted (excludes the range specified)
    :return: Filtered DataFrame
    """
    if not isinstance(query,list):
        query = split_and_clean_lines(query)
    logging.info(f"get_range processing")
    temp_df = df.copy()
    logging.info(f"temp_df created with type {type(temp_df)}")
    minimum,maximum = get_min_max_from_query(query)
    logging.info(f"minimum,maximum : {minimum},{maximum}")
    temp_df[column] = pd.to_numeric(temp_df[column], errors='coerce')  # Coerce errors in case of non-numeric data
    # Create a condition for values within the specified range
    condition = temp_df[column].between(minimum,maximum , inclusive='both')
    # Filter the original DataFrame using the condition from the temporary DataFrame
    series = is_inverse(condition,inverse=inverseOption)
    return df[series]
async def filter_dataframe(df, column,query,caseOption=False,substringOption=False,inverseOption=False,splitQuery=False):
    """
    Filters a DataFrame based on a comparison between a column's values and a list.

    Parameters:
    - df: Pandas DataFrame.
    - column: Column name as a string where the comparisons are to be made.
    - compare_list: List of strings to compare against the DataFrame's column.
    - substring_match: Boolean, if True performs substring matching, otherwise exact matching.
    - case_sensitive: Boolean, if False converts both column and list_obj to lowercase.

    Returns:
    - filtered_df: DataFrame containing only the rows that meet the condition.
    """
    if not isinstance(query,list):
        if splitQuery:
            
            if not isinstance(splitQuery,bool) and str(splitQuery) in str(query):
                logging.info(f"splitQuery chosen; splitting query with general {splitQuery}...")                
                query = clean_list(query.split(splitQuery))
            else:
                logging.info(f"splitQuery chosen; splitting query with general split...")
                query = split_and_clean_lines(query)
    compare_list=make_list(query)
    
    if not caseOption:
        logging.info(f"caseOption not chosen; normalizing case...")
        compare_list = [str(item).lower() for item in compare_list]
        df[column] = df[column].astype(str).str.lower()

    if substringOption:
        logging.info(f"substringOption chosen; searching for values in query object")
        condition = df[column].apply(lambda x: any(str(item) in str(x) for item in compare_list))
    else:
        logging.info(f"substringOption not chosen; searching for values == to query object")
        condition = df[column].apply(lambda x: any(str(item) == str(x) for item in compare_list))
    series = is_inverse(condition,inverse=inverseOption)
    return df[series]

async def filter_excel(df,column,query,range_option=False,caseOption=False,substringOption=False,inverseOption=False,distanceOption=False,geo_location_refference=None):
    logging.info(f"recieved excel: parsing for column={column},range_option={range_option},caseOption={caseOption},substringOption={substringOption},inverseOption={inverseOption},distanceOption={distanceOption},geo_location_refference={geo_location_refference}")
    df = get_df(df)
    logging.info(f"query came as {query}")
    if not isinstance(query,list):
        query = split_and_clean_lines(query)
    query=make_list(query)
    logging.info(f"query started as  as {query}")
    if distanceOption:
        logging.info(f"distanceOption selected")
        column=column or 'ZIP'
        query = await distance_within_range(distance=query,geo_location_refference=geo_location_refference)
        logging.info(f"query is now  as {query}")
    if range_option:
        logging.info(f"rangeOption selected")
        df = await get_range(df,column,query,inverseOption=inverseOption,caseOption=caseOption,substringOption=substringOption)
    else:
        df = await filter_dataframe(df,column,query,caseOption=caseOption,substringOption=substringOption,inverseOption=inverseOption)
    return df
