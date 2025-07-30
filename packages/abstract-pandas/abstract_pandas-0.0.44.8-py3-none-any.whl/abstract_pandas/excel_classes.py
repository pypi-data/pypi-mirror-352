from .excel_module import *
class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
class pathManager(metaclass=SingletonMeta):
    def __init__(self,window):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.path_tracker={}
            self.window=window
    def update_path(self,key,path):
        self.path_tracker[key]=path
    def get_path(self,key):
        return self.path_tracker[key]
    def get_display(self,key):
        return basename(self.get_path(key))
    def create_dir(self,key,file_path):
        if not isdir(dirname(file_path)):
            file_path = join(dirname(self.get_path(key)),file_path)
        self.update_path(key,file_path)
    def display_name(self,values,key):
        if self.window:
            if not values['-PATH_CHECK-']:
                self.window[key].update(basename(self.get_path(key)))
            else:
                self.window[key].update(self.get_path(key))
        return self.get_path(key)
class historyManager(metaclass=SingletonMeta):
    def __init__(self,window):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.historyTracker={}
            self.window=window
    def update_history(self,key,value):
        if key not in self.historyTracker:
            self.historyTracker[key]=[]
        self.historyTracker[key].append(value)
    def return_prior_history(self,key):
        if key not in self.historyTracker:
            self.historyTracker[key]=['']
        return self.historyTracker[key][-1]
class excelManager:
    def __init__(self,path_mgr,window,file_path):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.path_mgr=path_mgr
            self.dataframeTracker={"filePath":file_path,}
            self.initialize_data(file_path)
            self.window = window
    def get_df(self):
        return self.dataframeTracker["dataFrame"]
    def get_range(self,start_row=0,nrows=100):
        return read_excel_range(self.get_file_path(), start_row=start_row, num_rows=nrows)
    def read_excel(self, start_row=0, nrows=100):
        if start_row:
            df=self.get_range(start_row=start_row, nrows=nrows)
        else:
            df=pd.read_excel(self.get_file_path(),nrows=nrows)
        
        self.dataframeTracker['dataFrame'] = df
        self.dataframeTracker['range'] = {"start_row": start_row, "num_rows": nrows}
        return df
    def get_file_path(self):
        return self.dataframeTracker["filePath"]
    def get_headers(self):
        if "columnHeaders" not in self.dataframeTracker:
            self.dataframeTracker["columnHeaders"] = self.get_df().columns.tolist()
        return self.dataframeTracker["columnHeaders"]
    def get_dict(self):
        return self.dataframeTracker["dataDict"]
    def get_dimensions(self):
        return self.dataframeTracker['dimensions']
    def get_number_rows(self):
        return self.dataframeTracker['rows']
    def get_last_column(self):
        if "last_column" not in self.dataframeTracker:
            self.dataframeTracker['last_column'] = self.dataframeTracker["columnHeaders"][0]
        return self.dataframeTracker["last_column"]
    def read_file(self,file_path=None):
        file_path = file_path or self.path_mgr.get_path('-FILE-') or self.get_file_path()
        if file_path and file_path != self.get_file_path():
            self.initialize_data(file_path)
    def initialize_data(self,file_path):
        self.dataframeTracker["filePath"]=file_path
        self.read_excel()
        self.dataframeTracker['rows']=count_rows_in_excel(self.get_file_path())
        self.dataframeTracker["dataDict"] = self.get_df().to_dict(orient='records')
        self.dataframeTracker["columnHeaders"] = self.get_headers()
        self.dataframeTracker["columnItters"]={}
        for column in self.get_headers():
            self.dataframeTracker["columnItters"][column] = 0
    def update_range_based_on_cell_limit(self, desired_row):
        start_row=self.dataframeTracker['range']['start_row']
        end_row=self.dataframeTracker['range']['num_rows']
        if start_row<=desired_row and desired_row<=end_row:
            return 
        total_columns = len(self.get_headers())
        if total_columns == 0: return  # Prevent division by zero
        
        # Calculate the number of rows we can load based on MAX_CELLS
        num_rows = min(MAX_CELLS // total_columns, self.dataframeTracker["rows"])
        
        # Adjust start_row based on desired_row while keeping within the MAX_CELLS limit
        start_row = max(0, min(desired_row, self.dataframeTracker["rows"] - num_rows))
        
        # Read the new range of rows
        self.read_excel(start_row=start_row, nrows=num_rows)
                    
    def get_values(self,i):
        self.update_range_based_on_cell_limit(i)
        return self.get_df().iloc[i]
    def get_value(self,column,i):
        return self.get_values(i)[column]
    def update_column_itter(self,column,i):
        self.dataframeTracker["columnItters"][column] = i
        return self.get_last_column_itter(column)
    def get_column_itter(self,column):
        return self.dataframeTracker["columnItters"][column]
    def get_last_column_itter(self,column):
        i = self.get_column_itter(column)
        return self.get_value(column,i)
    def get_iter_direction(self,column,k):
        i = self.get_column_itter(column)
        if i+k>0 and i+k<self.get_number_rows():
            i=i+k
            self.update_column_itter(column,i)
        return self.get_value(column,i)
    def update_values_display(self,column=None,k=0):
        column = column or excel_mgr.get_last_column()
        self.dataframeTracker["last_column"] = column
        update = f"row:{self.get_column_itter(column)} value: {self.get_iter_direction(column,k)}"
        if self.window:
            self.window['-SAMPLE-'].update(update)
        return update
    def get_all_values_from_column(self,column):
        return get_unique_values_from_column(self.get_file_path(),column)
