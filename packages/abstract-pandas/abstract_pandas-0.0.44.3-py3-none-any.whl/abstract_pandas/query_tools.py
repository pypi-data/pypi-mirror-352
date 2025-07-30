from .file_utils import *
def is_inverse(series,inverse=False):
    if inverse:
        series = ~series
    return series
def update_excel(df,header,query):
    df = get_df(df)
    query = make_type(query,[str])
    df = convert_column(df,header,[str])
    return df,query
def merge_dataframes(dataframes):
    merged_df = pd.concat(dataframes, ignore_index=True)
    return merged_df
def excel_to_dict(df):
    # Read the Excel file
    df = get_df(df)
    # Convert each row to a dictionary with column headers as keys
    rows_as_dicts = df.to_dict(orient='records')
    return rows_as_dicts
def get_headers(df):
    df = get_df(df)
    column_names = df.columns.tolist()
    return column_names
def get_row_as_list(df,index=0):
    df=get_df(df)
    if get_row_number(df)>index:
        return df.loc[index].astype(str).tolist()
def get_row_number(df):
    df=get_df(df)
    return len(df)
def get_int_from_column(obj,column):
    headers = get_headers(obj)
    return get_itter(headers,column)
def get_column_from_int(obj,i):
    headers = get_headers(obj)
    column = safe_itter_get(headers,i)
    # Return the column headers
    return column
def find_row_with_matching_cell(excel_datas,search_column='',search_value=''):
    matching_row = [excel_data for excel_data in excel_datas if isinstance(excel_data,dict) and excel_data.get(search_column) == search_value]
    if matching_row and isinstance(matching_row,list) and len(matching_row)>0:
        return matching_row[0]
    return {}
def get_itter(list_obj,target):
    for i,string in enumerate(list_obj):
        if string == target:
            return i
    return None
def safe_itter_get(list_obj,i):
    if len(list_obj)>i:
        return list_obj[i]
def get_expected_headers(df,*expected_headers):
    df = get_df(df)
    if isinstance(expected_headers,tuple or set):
        expected_headers=list(expected_headers)
    else:
        expected_headers=make_list(expected_headers)
    expected_headers = {expected_header:"" for expected_header in expected_headers}
    return get_closest_headers(df,expected_headers)
def get_closest_headers(df,expected_headers={}):
    actual_headers = get_headers(df)  # Extract the actual headers from the DataFrame
    # Mapping actual headers to expected headers based on closest match
    for expected_header in expected_headers:
        # Using get_close_matches to find the closest match; returns a list
        close_matches = get_close_matches(expected_header, actual_headers, n=1, cutoff=0.6)
        if close_matches:
            expected_headers[expected_header] = close_matches[0]
        else:
            # If no close matches found, leave as empty string which signifies no match found
            expected_headers[expected_header] = ""
    return expected_headers
def find_closest_header(df,header):
    df = get_df(df)
    df_headers= df.columns.tolist()
    header_lower = header.lower()
    for df_header in df_headers:
        df_header_lower = df_header.lower()
        if df_header_lower in header_lower or header_lower in df_header_lower:
            js={header_lower:df_header}
            return js
def get_first_for_each(df,headers,queries,new_file_path=None):
    df=get_df(df)
    headers = get_expected_headers(df,headers).values()
    # Filter the DataFrame to only include rows with ZIP codes that are in the 'zips' list
    df=filter_and_deduplicate_df(df, headers, queries, dedup_columns=None)
    # Save the filtered and deduplicated DataFrame to a new Excel file
    return df
def get_cell_value(df, column_header, row_index=1):
    """
    Retrieves the value from a specified cell in the GeoDataFrame.
    
    :param df: GeoDataFrame or filepath to the shapefile.
    :param column_header: The header of the column from which to retrieve the value.
    :param row_index: The index of the row from which to retrieve the value.
    :return: The value located at the specified column and row.
    """
    df = get_df(df)
    # Check if the column header is in the GeoDataFrame
    if column_header not in df.columns:
        raise ValueError(f"The column header '{column_header}' does not exist in the GeoDataFrame.")
    
    # Check if the row index is within the bounds of the GeoDataFrame
    if not (0 <= int(row_index) < len(df)):
        raise ValueError(f"The row index {row_index} is out of bounds for the GeoDataFrame.")
    
    # Retrieve and return the value from the specified cell
    return df.iloc[row_index][column_header]
def count_rows_columns(df):
    """
    Counts the number of rows and columns in a pandas DataFrame.

    Parameters:
    - df (DataFrame): The pandas DataFrame whose dimensions will be counted.

    Returns:
    - tuple: A tuple containing two elements, the number of rows and the number of columns in the DataFrame.
    """
    rows, columns = df.shape  # df.shape returns a tuple (number of rows, number of columns)
    return rows, columns
def count_rows_in_excel(data_source, sheet_name=None):
    """
    Count rows in a given Excel sheet or pandas DataFrame.

    Parameters:
    - data_source (str or pd.DataFrame): The file path of the Excel file or a pandas DataFrame.
    - sheet_name (str, optional): The name of the sheet to count rows in. Used only if data_source is a file path.

    Returns:
    - int: Number of rows in the Excel sheet or DataFrame.
    """
    if isinstance(data_source, pd.DataFrame):
        # If data_source is a DataFrame, simply return the number of rows
        return len(data_source)
    elif isinstance(data_source, str):
        # Assume data_source is a file path to an Excel file
        try:
            wb = load_workbook(filename=data_source, read_only=True)
            if sheet_name and sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
            else:
                ws = wb[wb.sheetnames[0]]

            row_count = ws.max_row
            if row_count == 1 and ws.max_column == 1:
                if ws.cell(row=1, column=1).value is None:
                    row_count = 0
            
            wb.close()
            return row_count
        except utils.exceptions.InvalidFileException:
            print("Failed to open the file. It may be corrupted or the path is incorrect.")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    else:
        print("Invalid input. Please provide a valid file path or pandas DataFrame.")
        return None
def read_excel_range(df, start_row, num_rows):
    # Skip rows up to start_row, not including the header if it's the first row.
    # Adjust start_row by 1 if your Excel file has headers and you want to include them.
    # start_row is 0-indexed in Python, but 1-indexed in Excel, so adjust accordingly.
    skip = start_row - 1 if start_row > 0 else None
    
    # Read the specified range of rows
    df = get_df(df, skiprows=skip, nrows=num_rows, header=None if skip is None else 0)
    
    return df
def get_row(target_value,column_name=None,index_value=None,df=None):
    # Use the `.str.contains` method directly in the indexing to filter rows
    df = get_df(df)
    column_names = make_list(column_name or df.columns.tolist())
    for i,column in enumerate(column_names):
        search_column(target_value,column_name=None,column_index=0,df=None,exact_match=True)
        value = df[column][index_value]
        if value.lower() == target_value.lower():
            return df,i
    return None,None
def search_column(target_value,column_name=None,column_index=0,df=None,exact_match=True):
    df = get_df(df)
    headers = df.columns.tolist()
    if not column in headers and column_index >len(headers):
        return
    column_values = df[column].tolist()
    if target_value in column_values:
        return get_itter(column_values=column_values,target_value=target_value,exact_match=exact_match)
    if not exact_match:
        if [val for val in column_values if str(target_value) in str(val)]:
           return get_itter(column_values=column_values,target_value=target_value,exact_match=exact_match)
    column_names = make_list(column_name or headers)
    return column_names
def convert_value(value, column_dtype):
    """ Convert the value to the column data type if possible, handling string representations of numbers. """
    if pd.api.types.is_numeric_dtype(column_dtype):
        try:
            return float(value)
        except ValueError:
            return value  # Return the original value if conversion fails
    return value













