from .excel_module import get_df,create_dataframe,get_row,get_cell_value
from .functions import haversine
class abstractLandManager:
    def __init__(self,directory_js=None,default_polygon=None,column=None,value=None,default_index=1):
        directory_js = directory_js or {}
        if landManager._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            landManager._instance = self
        self.file_manager={}
        self.closest_points={}
        self.default_polygon= default_polygon
        for directory_name,directory_path in directory_js.items():
            self.file_manager[directory_name] = {} 
            self.ext_js = {"shp":'.shp', "prj":'.prj', "cpg":'.cpg', "dbf":'.dbf', "shx":'.shx'}

            for file_item in os.listdir(directory_path):
                item_path = os.path.join(directory_path,file_item)
                self.file_manager[directory_name][os.path.splitext(file_item)[-1][1:]] = item_path
        if self.default_polygon == None:
            gdf=get_file_path(file_type='shp')
            if gdf:
                self.default_polygon = get_polygon(gdf,column=column,value=value,index=index)
    @staticmethod
    def get_instance(directory_js=None):
        if landManager._instance is None:
            landManager(directory_js)
        return landManager._instance
    def get_polygon(self,gdf,column=None,value=None,index=1):
        if isinstance(gdf,Polygon) or isinstance(gdf,MultiPolygon):
            return gdf
        gdf = get_df(gdf)
        polygon = get_cell_value(gdf,'geometry',index)
        if polygon:
            return polygon
        if column or value:
            gdf,index = get_row(target_value=value,column_name=column,index_value=index,df=gdf)
        if gdf:
            return get_cell_value(gdf,'geometry',index)
    def get_file_path(self,dir_name,file_type):
        if dir_name == None:
            dir_name = list(self.file_manager.keys())
            if dir_name:
                dir_name = dir_name[0]
            else:
                return None
        file_path = self.file_manager.get(dir_name,{}).get(file_type)
        if file_path and os.path.isfile(file_path):
            return file_path
    def get_contents(self,dir_name,file_type):
        if os.path.isfile(file_type):
            file_path = file_type
        else:
            file_path = self.get_file_path(dir_name,file_type)
        if file_path:
            try:
                data = get_df(file_path)
                return data
            except Exception as e:
                print(f"{e}")
def get_proj(dir_name=None,file_path="prj"):
    land_mgr = landManager.get_instance()
    proj_string = land_mgr.get_contents(dir_name,file_path)
    return proj_string
def get_dbf(dir_name=None,file_path="dbf"):
    land_mgr = landManager.get_instance()
    proj_string = land_mgr.get_contents(dir_name,file_path)
    return proj_string
def get_shp(dir_name=None,file_path="shp"):
    land_mgr = landManager.get_instance()
    return land_mgr.get_contents(dir_name,file_path)
def get_cpg(dir_name=None,file_path="cpg"):
    land_mgr = landManager.get_instance()
    return land_mgr.get_contents(dir_name,file_path)
def get_dbf(dir_name=None,file_path="dbf"):
    land_mgr = landManager.get_instance()
    return land_mgr.get_contents(dir_name,file_path)
def get_shx(dir_name=None,file_path="shx"):
    land_mgr = landManager.get_instance()
    return land_mgr.get_contents(dir_name,file_path)
def get_bp(bp,column=None,value=None,index=1):
    if isinstance(bp,Polygon) or isinstance(bp,MultiPolygon):
        return bp
    land_mgr = landManager.get_instance()
    gdf = get_shp(dir_name=dir_name,file_path="shp")
    bp = land_mgr.get_polygon(gdf,column=column,value=value,index=index) 
    return bp
