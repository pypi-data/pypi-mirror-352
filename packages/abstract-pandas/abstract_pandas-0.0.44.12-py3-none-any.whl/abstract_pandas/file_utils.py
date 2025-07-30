from odf.table import Table, TableRow, TableCell
from odf.opendocument import load
import pandas as pd
import geopandas as gpd
from .proj_tools import *
from abstract_utilities import *
from odf import text, teletype
from datetime import datetime
from openpyxl import load_workbook, utils
from difflib import get_close_matches
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import tempfile,shutil,os,ezodf,inspect,logging,logging
from .general_functions import split_and_clean_lines,make_type,convert_column,return_float_or_int,safe_get,get_number
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
def source_ext(typ=None):
    source_js = {'.parquet':'pyarrow','.txt':'python','.xlsx':'openpyxl','.xls':'openpyxl','.xlsb':'pyxlsb','.ods':'odf','.geojson':'GeoJSON'}
    if typ:
        source_js = source_js.get(typ)
    return source_js
def is_file(file_path):
    if file_path not in ['',' ',None,'None'] and isinstance(file_path, str) and os.path.isfile(file_path):
        return os.path.splitext(file_path)[-1]
def isDataFrame(obj):
    return isinstance(obj, pd.DataFrame)
def create_dataframe(new_data=None,columns=None):
    if isDataFrame(new_data):
        return new_data
    new_data = new_data or {}
    if isinstance(new_data,dict):
        new_data=[new_data]
        if columns == None:
            columns=[]
            for datas in new_data:
                if isinstance(datas,dict):
                    columns=list(set(columns+list(datas.keys())))
        if columns ==False:
            columns=None
    if isinstance(new_data,list):
        return pd.DataFrame(new_data,columns=columns)
def read_ods_file(file_path):
    doc = ezodf.opendoc(file_path)
    sheets = {}
    
    for sheet in doc.sheets:
        data = []
        for row in sheet.rows():
            row_data = []
            for cell in row:
                if cell.value_type == 'date':
                    # Explicitly handle date cells
                    date_obj = convert_date_string(str(cell.value))
                    row_data.append(date_obj)
                else:
                    # Append other types of cells directly
                    row_data.append(cell.value)
            data.append(row_data)
        df = pd.DataFrame(data)
        sheets[sheet.name] = df
        print(f"Processed sheet: {sheet.name}")
    return sheets
def read_ods(file_path,xlsx_path=None):
    ods_to_xlsx(file_path,xlsx_path)
    return pd.read_excel(xlsx_path)
def filter_df(df, nrows=None, condition=None, indices=None):
    """
    Apply filtering to a DataFrame based on specified criteria.

    Parameters:
    - df (DataFrame): The DataFrame to filter.
    - nrows (int, optional): Number of rows to return from the start.
    - condition (pd.Series, optional): Boolean series for row filtering.
    - indices (list of int, optional): Row indices to select.

    Returns:
    - DataFrame: Filtered DataFrame.
    """
    if nrows is not None:
        df = df.head(nrows)
    if condition is not None:
        df = df[condition]
    if indices is not None:
        df = df.iloc[indices]
    return df
def read_shape_file(source):
    file_ext = is_file(source)
    if file_ext:
        if file_ext in ['.shp', '.cpg', '.dbf', '.shx','.geojson']:
            df = gpd.read_file(source,driver=source_ext(file_ext))
            return df
        elif file_ext in ['.prj']:
            df = read_from_file(source)
            return df
    return False
def get_df(source=None, nrows=None, skiprows=None, condition=None, indices=None):
    """
    Load a DataFrame from various sources with optional filtering.

    Parameters:
    - source (str, pd.DataFrame, gpd.GeoDataFrame, dict, list, FileStorage): Source of the data.
    - nrows (int, optional): Number of rows to load.
    - header (int, list of int, 'infer', optional): Row(s) to use as the header.
    - skiprows (list-like, int, optional): Rows to skip at the beginning.
    - condition (pd.Series, optional): Condition for filtering rows.
    - indices (list of int, optional): Indices of rows to select.

    Returns:
    - pd.DataFrame or gpd.GeoDataFrame: Loaded and optionally filtered data.
    """
    if isinstance(source, (pd.DataFrame, gpd.GeoDataFrame)):
        #logging.info("Data is already loaded as a DataFrame/GeoDataFrame.")
        return filter_df(source, nrows=nrows, condition=condition, indices=indices)

    if source is None:
        logging.error("No source provided for loading data.")
        return None

    if isinstance(source, str) and os.path.isfile(source):
        file_ext = os.path.splitext(source)[-1].lower()
        try:
            logging.info(f"Loading data from file with extension: {file_ext}")
            if file_ext in ['.csv', '.tsv', '.txt']:
                sep = {'csv': ',', 'tsv': '\t'}.get(file_ext.strip('.'), None)
                df = pd.read_csv(source,  skiprows=skiprows, sep=sep, nrows=nrows)
            elif file_ext in ['.ods', '.xlsx', '.xls', '.xlsb']:
                engine = {'ods': 'odf', 'xlsx': 'openpyxl', 'xls': 'xlrd', 'xlsb': 'pyxlsb'}.get(file_ext.strip('.'))
                df = pd.read_excel(source,  skiprows=skiprows, engine=engine, nrows=nrows)
            elif file_ext == '.json':
                df = pd.read_json(source, nrows=nrows)
            elif file_ext == '.parquet':
                df = pd.read_parquet(source, nrows=nrows)
            elif file_ext in ['.shp', '.cpg', '.dbf', '.shx','.geojson','.prj']:
                df = read_shape_file(source)
            else:
                try:
                    df = read_from_file(source)
                except:                
                    raise logging.info(f"Unsupported file extension: {file_ext}")
            if not isinstance(df, (dict, list,FileStorage)):
                return filter_df(df, nrows=nrows, condition=condition, indices=indices)
            source = df
        except Exception as e:
            logging.error(f"Failed to read file: {e}")
            return None

    if isinstance(source, FileStorage):
        try:
            logging.info(f"Reading from FileStorage: {secure_filename(source.filename)}")
            df = pd.read_excel(source.stream, nrows=nrows)
            return filter_df(df, nrows=nrows, condition=condition, indices=indices)
        except Exception as e:
            logging.error(f"Failed to read from FileStorage: {e}")
            return None

    if isinstance(source, (dict, list)):
        logging.info("Creating DataFrame from in-memory data structure.")
        df = pd.DataFrame(source)
        return filter_df(df, nrows=nrows, condition=condition, indices=indices)

    logging.error("Invalid data source type provided.")
    return None
def save_df(df,file_path,index=None,suffix=None,engine=None):
    df = get_df(df)
    suffix = suffix or os.path.splitext(file_path)[-1] or '.xlsx'
    logging.info(f"saving df with suffix {suffix} to {file_path}")
    try:
        if suffix in ['.ods','.xlsx', '.xls','.xlsb']:
            df.to_excel(file_path,  engine=engine or source_ext(suffix))
            
        elif suffix in ['.csv','.tsv','.txt']:
            df.to_csv(file_path,  engine=engine or source_ext(suffix))
        elif suffix in [".shp", ".cpg", ".dbf", ".shx",'.geojson']:
            df.to_file(file_path,driver=source_ext(suffix))
        elif suffix in ['.prj']:
            save_valid_crs(df, file_path=file_path)
        elif suffix == '.parquet':
            df.to_parquet(file_path, engine=engine or source_ext(suffix))
        else:
            logging.info(f"could not find appropriate file type, attempting generic file save")
            try:
                save_to_file(df,file_path)
                logging.info(f"file save for file path {file_path} succesful")
                return True
            except Exception as e:
                logging.info(f"file save for file path {file_path} unsuccesful:\n {e}")
                return False
        logging.info(f"file save for file path {file_path} succesful")
        return True
    except Exception as e:
        logging.info(f"Failed to read file: {e}")
        return False
    return True
    
def safe_excel_save(df,original_file_path,index=False,suffix=None,engine=None):
    suffix = suffix or os.path.splitext(original_file_path)[-1] or '.xlsx'
    result = None
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        temp_file_name = tmp.name
        result = save_df(df,temp_file_name,index=index,suffix=suffix,engine=engine)  # Save your DataFrame to the temp file
        logging.info(f"{temp_file_name} {os.path.isfile(temp_file_name)},{os.path.getsize(temp_file_name)}")
    if result and os.path.getsize(temp_file_name) > 0:
        shutil.move(temp_file_name, original_file_path)
    else:
       logging.info("Temporary file is empty or wasn't written correctly. Original file is unchanged.")
    # Cleanup: Ensure the temporary file is deleted if it hasn't been moved
    if os.path.exists(temp_file_name):
        os.remove(temp_file_name)
def move_excel_file(current_path, target_path):
    """
    Moves an Excel file from the current_path to the target_path.
    
    Parameters:
    - current_path: str, the current path including filename of the Excel file.
    - target_path: str, the target path including filename where the Excel file should be moved.
    
    Returns:
    - bool: True if the file was successfully moved, False otherwise.
    """
    try:
        # Check if the current file exists
        if not os.path.isfile(current_path):
            print(f"The file {current_path} does not exist.")
            return False

        # Move the file
        shutil.move(current_path, target_path)
        print(f"File moved successfully from {current_path} to {target_path}")
        return True
    except Exception as e:
        print(f"Error moving the file: {e}")
        return False
def unique_name(base_path, suffix='_', ext='.xlsx'):
    """
    Generates a unique file path by appending a datetime stamp or incrementing a suffix.
    
    Parameters:
    - base_path (str): Base path of the file without extension.
    - suffix (str): Suffix to append for uniqueness.
    - ext (str): File extension.
    
    Returns:
    - str: A unique file path.
    """
    # Generate initial path with datetime suffix
    datetime_suffix = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_path = f"{base_path}{suffix}{datetime_suffix}{ext}"
    
    # Check if this path exists, if it does, increment an index until a unique name is found
    counter = 1
    while os.path.isfile(unique_path):
        unique_path = f"{base_path}{suffix}{datetime_suffix}_{counter}{ext}"
        counter += 1
    
    return unique_path

def get_new_excel_path(source=None):
    """
    Derives a new non-conflicting Excel file path based on the input source.
    
    Parameters:
    - source (str, pd.DataFrame, or bytes): Original source which can be a path or DataFrame.
    
    Returns:
    - str: A unique file path for a new Excel file.
    """
    default_filename = "new_excel.xlsx"

    # Handle DataFrame directly
    if isinstance(source, pd.DataFrame):
        return unique_name(os.path.splitext(default_filename)[0])

    # Handle source as a string path or bytes (assuming bytes can be decoded to a path)
    elif isinstance(source, (str, bytes)):
        if isinstance(source, bytes):
            try:
                source = source.decode('utf-8')
            except UnicodeDecodeError:
                print("Error: Bytes source could not be decoded to a string.")
                return unique_name(os.path.splitext(default_filename)[0])

        if os.path.isfile(source):
            base_path, _ = os.path.splitext(source)
            return unique_name(base_path)
        else:
            return source  # Return the source itself if it's a non-existent file path

    # Handle None or any other type that doesn't fit the above categories
    else:
        return unique_name(os.path.splitext(default_filename)[0])
def ods_to_xlsx(ods_path, xlsx_path):
    doc = load(ods_path)
    data_frames = []

    for table in doc.spreadsheet.getElementsByType(Table):
        rows = []
        for row in table.getElementsByType(TableRow):
            cells = []
            for cell in row.getElementsByType(TableCell):
                repeat = cell.getAttribute("numbercolumnsrepeated")
                if not repeat:
                    repeat = 1
                cell_data = teletype.extractText(cell) or ""
                cells.extend([cell_data] * int(repeat))
            if cells:
                rows.append(cells)
        df = pd.DataFrame(rows)
        data_frames.append(df)

    # Assuming you want to save the first sheet as an example
    if data_frames:
        data_frames[0].to_excel(xlsx_path, index=False)

def get_caller_path():
    """ Returns the absolute directory path of the script that calls this function. """
    stack = inspect.stack()
    caller_frame = stack[1]
    caller_path = os.path.abspath(caller_frame.filename)
    return os.path.dirname(caller_path)

def mkdir(base_path, subfolder):
    """ Ensure a subdirectory exists in the given base path and return its path. """
    full_path = os.path.join(base_path, subfolder)
    if not os.path.exists(full_path):
        os.makedirs(full_path, exist_ok=True)
    return full_path

def get_excels_dir(abs_dir=None):
    """ Get or create a directory named 'excels' in the specified or caller's directory. """
    abs_dir = abs_dir or get_caller_path()
    return mkdir(abs_dir, 'excels')

def get_filtered_dir():
    """ Get or create a directory named 'filtered' inside the 'excels' directory. """
    return mkdir(get_excels_dir(), 'filtered')

def get_original_dir():
    """ Get or create a directory named 'original' inside the 'excels' directory. """
    return mkdir(get_excels_dir(), 'original')

def get_path_pieces(file_path):
    directory = os.path.dirname(file_path)
    baseName = os.path.basename(file_path)
    fileName,ext = os.path.splitext(baseName)
    return baseName,fileName,ext
def get_filtered_file_path(file_path,filter_type='filtered'):
    baseName,fileName,ext = get_path_pieces(file_path)
    return os.path.join(get_filtered_dir(), f"{fileName}_{filter_type}{ext}")
def get_original_file_path(file_path):
    baseName,fileName,ext = get_path_pieces(file_path)
    return os.path.join(get_original_dir(), baseName)
def save_original_excel(file_path,original_dir=None):
    df = get_df(file_path)
    original_dir = original_dir or os.getcwd()
    original_file_path = get_original_file_path(file_path)
    safe_excel_save(df,original_file_path)
    return original_file_path
def save_filtered_excel(df,file_path,filter_type='filtered'):
    df = get_df(df)
    filtered_file_path = get_filtered_file_path(file_path,filter_type=filter_type)
    safe_excel_save(df,filtered_file_path)
    return filtered_file_path
