from .excel_module import *
def find_matching_rows(rows_as_dicts, criteria_dict):
    """
    Find rows that match the given criteria.
    :param rows_as_dicts: List of dictionaries representing the rows.
    :param criteria_dict: A dictionary where each key-value pair is a condition to match.
    :return: A list of dictionaries (rows) that match all criteria.
    """
    matching_rows = []
    for row in rows_as_dicts:
        if all(row.get(key) == value for key, value in criteria_dict.items()):
            matching_rows.append(row)
    return matching_rows
def append_new_data(df,new_data):
    # No matching row, append new data as a new row
    new_index = len(df)
    for key, value in new_data.items():
        if key in df.columns and value not in [None, '']:
            df.at[new_index, key] = value
    return df
def append_unique_to_excels(df,new_data,file_path=None, search_column= None, search_value=None,print_it=False):
    """
    Updates or appends data in an Excel file based on the contents of a specified column.

    Parameters:
    - file_path: str, the path including filename of the Excel file.
    - new_data: dict, data to update or append.
    - search_column: str, the name of the column to search for the search_value.
    - search_value: str, the value to search for in the search_column.
    """
    # If the Excel file doesn't exist, create a new DataFrame from new_data and save it
    if file_path and not os.path.isfile(file_path):
        new_df = pd.DataFrame([new_data])
        safe_excel_save(new_df,file_path,index=False, engine='openpyxl')
        print("Excel file created with new data.")
        return new_df
    if isinstance(df,str) and os.path.isfile(df):
        file_path=df
    # Load the existing DataFrame from the Excel file
    df = get_df(df)

    # Standardize data types for existing columns based on new_data types
    for key, value in new_data.items():
        if key in df.columns:
            # Determine desired column data type based on the new value's type
            if isinstance(value, str):
                df[key] = df[key].astype(str, errors='ignore')
            elif isinstance(value, float):
                df[key] = df[key].astype(float, errors='ignore')
            elif isinstance(value, int):
                # If value is integer but fits in float without losing precision, consider converting to float
                # This is because pandas uses NaN (a float value) to represent missing data for numeric columns
                df[key] = df[key].astype(float, errors='ignore')

    # Find if there's a row that matches the search_value in search_column
    match = None
    if search_column and search_value:
        match = df[df[search_column] == search_value]
        if not match.empty:
            # There's a matching row, update only if new data is not None or ''
            row_index = match.index[0]  # Assuming the first match should be updated
            for key, value in new_data.items():
                if key in df.columns:
                    # Check if value is not None or empty string
                    if value not in [None, '']:
                        # Determine the column data type
                        column_dtype = df[key].dtype
                        
                        # If the column is of integer type but the value is a string that represents an integer,
                        # explicitly cast the value to int. Otherwise, keep it as string.
                        if pd.api.types.is_integer_dtype(column_dtype) and value.isdigit():
                            df.at[row_index, key] = int(value)
                        elif pd.api.types.is_float_dtype(column_dtype) and is_number(value):
                            # For floating-point numbers
                            df.at[row_index, key] = float(value)
                        else:
                            # For other types, including cases where casting to int/float isn't appropriate
                            df.at[row_index, key] = value
            if print_it:
                print(f"Updated row where {search_column} matches {search_value}.")
        else:
            append_new_data(df,new_data)
    else:
        append_new_data(df,new_data)
        if print_it:
            print(f"Appended new data since no matching {search_column} found for {search_value}.")

    # Save the updated DataFrame back to the Excel file
    if file_path:
        safe_excel_save(df,file_path)
    return df
def append_unique_to_excel(file_path, new_data_list, key_columns=None):
    """
    Append new data to an Excel file, ensuring no duplicate rows are added.
    
    :param file_path: Path to the Excel file.
    :param new_data_list: List of dictionaries representing the rows to add.
    :param key_columns: Optional list of columns to use for identifying duplicates. If None, all columns are used.
    """
    # Convert new_data_list to DataFrame and convert all columns to string type
    new_data_df = pd.DataFrame(new_data_list).astype(str)
    
    if not os.path.isfile(file_path):
        # If the Excel file doesn't exist, save the new DataFrame directly
        new_data_df.to_excel(file_path, index=False, engine='openpyxl')
    else:
        # If the Excel file exists, load it and append the new data
        existing_df = pd.read_excel(file_path, engine='openpyxl').astype(str)

        # Concatenate the existing data with the new data
        combined_df = pd.concat([existing_df, new_data_df], ignore_index=True)
        
        # Drop duplicates. If key_columns is not specified, all columns are considered
        if key_columns is None:
            combined_df = combined_df.drop_duplicates(keep='first')
        else:
            combined_df = combined_df.drop_duplicates(subset=key_columns, keep='first')
        
        # Save the updated DataFrame back to the Excel file
        combined_df.to_excel(file_path, index=False, engine='openpyxl')
    return combined_df
def get_column_values(df,heads=10):
    df=read_excel_input(df)
    return {col: df[col].head(heads).dropna().tolist() for col in df.columns}
def filter_rows_based_on_keywords(df, column_names, keywords):
    """
    Filter rows in a DataFrame based on the presence or absence of specified keywords in given columns.

    Parameters:
    - df (pd.DataFrame): The DataFrame to filter.
    - column_names (list): The names of the columns to search for the keywords.
    - keywords (list): The keywords to search for in the specified columns.

    Returns:
    - pd.DataFrame: A DataFrame filtered based on the specified criteria.
    """
    # Create a mask initialized to False for each row
    mask = pd.Series([False] * len(df))
    
    for column_name in column_names:
        if column_name in df.columns:
            # Update the mask to include rows where the column contains any of the keywords
            for keyword in keywords:
                mask = mask | df[column_name].astype(str).str.contains(keyword, case=False, na=False)
    
    # Invert the mask to filter out rows that match the keywords
    return df[~mask]
def identify_common_rows(df_1,df_2):
    # Find the indices of rows that are common in both battery_df and solar_panel_df
    return df_1.index.intersection(df_2.index)
def filter_by_queries_in_column(df,column,queries):
    return df[df[column].isin(queries)]
