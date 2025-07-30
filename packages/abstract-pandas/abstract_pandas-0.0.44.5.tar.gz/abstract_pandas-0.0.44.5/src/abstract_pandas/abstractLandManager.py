from .excel_module import get_df,get_row,get_cell_value,gpd,eatAll
from .file_utils import safe_excel_save
from shapely.geometry import Polygon,MultiPolygon
import os
class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
def get_project_name(filePath):
    directory = os.path.dirname(filePath)
    baseName = os.path.basename(filePath)
    fileName,ext = os.path.splitext(baseName)
    return directory,fileName,ext
def create_file_name(filePath,suffix):
    suffix = eatAll(suffix,'.')
    directory,fileName,ext=get_project_name(filePath)
    return os.path.join(directory,f"{fileName}.{suffix}")
def update_file(df,compFilePath,suffix):
    suffix = eatAll(suffix,'.')
    filePath = create_file_name(compFilePath,suffix)
    safe_excel_save(df,filePath)
    return filePath
class landManager(metaclass=SingletonMeta):
    def __init__(self,directory_js=None,default_polygon=None,column=None,value=None,epsg=4326,index=1):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            directory_js = directory_js or {}
            self.file_manager={}
            self.closest_points={}
            self.default_polygon= default_polygon
            for directory_name,directory_path in directory_js.items():
                self.file_manager[directory_name] = {} 
                self.ext_js = {"shp":'.shp', "prj":'.prj', "cpg":'.cpg', "dbf":'.dbf', "shx":'.shx','geojson':'.geojson'}
                for file_item in os.listdir(directory_path):
                    item_path = os.path.join(directory_path,file_item)
                    self.file_manager[directory_name][os.path.splitext(file_item)[-1][1:]] = item_path
                if self.default_polygon == None:
                    gdf=self.get_contents(directory_name,file_type='shp')
                    if isinstance(gdf,gpd.GeoDataFrame):
                        self.default_polygon = self.get_polygon(gdf,column=column,value=value,index=index)
                self.check_geo_json(directory_name,epsg=epsg)
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
            gdf,index = get_row(target_value=value,column_name=column,df=gdf)
        if isinstance(gdf,gpd.GeoDataFrame):
            return get_cell_value(gdf,'geometry',index)
    def check_geo_json(self,dir_name,epsg=4326):
        geoJsonPath = self.file_manager.get(dir_name,{}).get('geojson')
        if geoJsonPath == None or not os.path.isfile(geoJsonPath):
            gdf = self.get_contents(dir_name,'shp')
            geoJsonPath = self.update_file(gdf,dir_name,'geojson')
        return geoJsonPath
    def update_file(self,df,dir_name,suffix):
        file_path = self.get_file_path(dir_name,'shp')
        if file_path and os.path.isfile(file_path):
            filePath = update_file(df,file_path,suffix)
            if filePath:
                self.file_manager[dir_name][suffix] = filePath
            return filePath
        return file_path
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
    def get_contents(self,dir_name,file_type,update=None):
        if update is not None and not isinstance(update,bool):
            file_path = self.update_file(update,dir_name,file_type)
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
def get_proj(dir_name=None,file_path="prj",update=False):
    land_mgr = landManager.get_instance()
    return land_mgr.get_contents(dir_name,file_path,update=update)
def get_dbf(dir_name=None,file_path="dbf",update=False):
    land_mgr = landManager.get_instance()
    return land_mgr.get_contents(dir_name,file_path,update=update)
def get_shp(dir_name=None,file_path="shp",update=False):
    land_mgr = landManager.get_instance()
    return land_mgr.get_contents(dir_name,file_path,update=update)
def get_cpg(dir_name=None,file_path="cpg",update=False):
    land_mgr = landManager.get_instance()
    return land_mgr.get_contents(dir_name,file_path,update=update)
def get_dbf(dir_name=None,file_path="dbf",update=False):
    land_mgr = landManager.get_instance()
    return land_mgr.get_contents(dir_name,file_path,update=update)
def get_shx(dir_name=None,file_path="shx",update=False):
    land_mgr = landManager.get_instance()
    return land_mgr.get_contents(dir_name,file_path,update=update)
def get_geojson(dir_name=None,file_path="geojson",update=False):
    land_mgr = landManager.get_instance()
    return land_mgr.get_contents(dir_name,file_path,update=update)
def get_bp(bp,column=None,value=None,index=1):
    if isinstance(bp,Polygon) or isinstance(bp,MultiPolygon):
        return bp
    land_mgr = landManager.get_instance()
    gdf = get_shp(dir_name=dir_name,file_path="shp")
    bp = land_mgr.get_polygon(gdf,column=column,value=value,index=index) 
    return bp
