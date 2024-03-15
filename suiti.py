'''
Author: Mr.Car
Date: 2024-01-07 17:34:41
'''
from inner import *
import pandas as pd
import geopandas as gpd
import os
import fire
import warnings
from alive_progress import alive_bar

# 忽略 FutureWarning
warnings.simplefilter(action='ignore', category=FutureWarning)

# 指定包含 CSV 文件的文件夹路径
folder_path = os.path.join(os.path.dirname(__file__), 'config')

# 初始化
# 初始化一个空字典，用于存储读取的 CSV 数据
csv_data = {}
# 遍历文件夹中的所有文件
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)  # 获取文件的完整路径
        dataframe = pd.read_csv(file_path)  # 读取 CSV 文件为 Pandas DataFrame
        dataframe.set_index('name', inplace=True)
        csv_data[os.path.splitext(filename)[0]] = dataframe # 使用文件名（不包含扩展名）作为字典的键，并将 DataFrame 存储为值

cfg_pair = csv_data['cfg_pair']
cfg_level = csv_data['cfg_level']
cfg_level_suitibility = csv_data['cfg_level_suitibility']
cfg_level_sub_level = csv_data['cfg_level_sub_level']
# 将行列标签都转为字符串
cfg_level.columns = cfg_level.columns.astype(str)
cfg_level.index = cfg_level.index.astype(str)
# 将列标签都转为字符串, 将所有值都转为字符串, 便于测试
cfg_level_suitibility.columns = cfg_level_suitibility.columns.astype(str)
cfg_level_sub_level = cfg_level_sub_level.astype(str)
cfg_index = csv_data['cfg_index'].index.tolist()
# print(cfg_index)

def pair_origin_to_target(origin_value, origin_name):
    '''
        pair origin data to target data
    '''
    try:
        cfg = cfg_pair.loc[origin_name]
        sub_table = cfg['sub_table']
        deal_func_name = cfg['deal_func_name']
        
        rule_strs = csv_data[sub_table]
        result_value = globals()[deal_func_name](origin_value, rule_strs)
        # if value_type == 0:
        #     origin_sub_value = csv_data[sub_table].loc[origin_value]['inner_name']
        #     result_value = globals()[deal_func_name](origin_sub_value)
        # elif value_type == 1:
        #     result_value = globals()[deal_func_name](origin_value)
        return result_value

    except KeyError as e:
        raise KeyError(f"{origin_name} 或 {origin_value} 缺少 '{str(e)}' 相关配置")
    except TypeError as e:
        raise TypeError('检查', origin_name, str(e))

def pair_all(df):
    for index in cfg_index:
        df[index + '_new'] = df[index].apply(pair_origin_to_target, args=[index])
    return df

def calc_level(row):
    '''
    计算最高限制因素的等级与其个数，查表计算适宜类等级
    '''

    max_level = 0
    max_level_num = 0
    result = None
    for index in cfg_index:
        if row[index + '_new'] > max_level: max_level = row[index + '_new']
    for index in cfg_index:
        if row[index + '_new'] == max_level: max_level_num += 1
    if max_level <= 2:
        result = 0
    elif max_level > 2 and max_level <= 5:
        if max_level_num > 4:
            result = cfg_level.loc[str(max_level), '>4']
        else:
            result = cfg_level.loc[str(max_level), str(max_level_num)]
    return result

def get_max_limit_str(row):
    index_names = [each+'_new' for each in cfg_index]
    index_alias = [cfg_pair.loc[each]['alias'] for each in cfg_index]
    index_values = row[index_names]
    max_value = max(index_values)
    max_names_string = ','.join([index_alias[i] for i, v in enumerate(index_values) if v == max_value])
    return max_names_string

def calc_sub_level(row):
    '''
    根据适宜类等级，划分适宜类子等级，高度适宜，中度适宜，勉强适宜等
    '''
    def find_column_name(row, value):
        for column_name, cell_value in row.items():
            if cell_value == value:
                return column_name
        return None
    sub_level_name = cfg_level_suitibility.loc['suitibility'][str(row['s_level'])]
    num_over_three = 0
    result = None

    for index in cfg_index:
        if row[index + '_new'] >= 3: num_over_three += 1
    if sub_level_name == "宜耕":
        result_range = cfg_level_sub_level.loc['宜耕']
        result = find_column_name(result_range, str(num_over_three))
    elif sub_level_name == "宜园":
        result_range = cfg_level_sub_level.loc['宜园']
        if num_over_three >= 3:
            result = find_column_name(result_range, ">=3")           
        else:
            result = find_column_name(result_range, str(num_over_three)) 
    elif sub_level_name == "宜林":
        result_range = cfg_level_sub_level.loc['宜林']
        if num_over_three >= 3:
            result = find_column_name(result_range, ">=3")
        else:
            result = find_column_name(result_range, str(num_over_three))
    elif sub_level_name == "宜草":
        result_range = cfg_level_sub_level.loc['宜草']
        if num_over_three >= 4:
            result = find_column_name(result_range, ">=4")
        else:
            result = find_column_name(result_range, str(num_over_three))
    else:
        result = None

    # 获取最大限制因素字符串
    max_limit_str = ''
    if result in ['II', 'III']:
        max_limit_str = get_max_limit_str(row)
    return [sub_level_name, result, max_limit_str]

def calc_level_all(df):
    df['s_level'] = df.apply(calc_level, axis=1)
    return df

def calc_sub_level_all(df):
    retrun_df = df.apply(calc_sub_level, axis=1, result_type='expand')
    df['s_name'] = retrun_df[0]
    df['s_s_level'] = retrun_df[1]
    df['s_limit'] = retrun_df[2]
    return df

def read_data(file_pth, option_type="csv"):
    if option_type == "shp":
        the_file = gpd.read_file(file_pth)
    else:
        the_file = pd.read_csv(file_pth)
    return the_file

def save_data(file, file_pth, option_type="csv"):
    if option_type == 'shp':
        the_file = file.to_file(file_pth, driver='ESRI Shapefile', encoding='utf-8')
    else:
        the_file = file.to_csv(file_pth, index=False)

def main(file_pth, option_type="shp", out_file_pth=None):
    """
    option_type 默认为shp，可选为csv
    out_file_pth 默认为输入文件同名目录下，文件名为 suiti_result.shp
    """
    
    total_steps = 3  # 总共需要执行的函数数量
    with alive_bar(total_steps) as bar:  # 初始化进度条
        if option_type == "shp":
            the_file = read_data(file_pth, "shp")
        if option_type == "csv":
            the_file = read_data(file_pth, "csv")
        bar()
        
        the_file = pair_all(the_file)
        the_file = calc_level_all(the_file)
        the_file = calc_sub_level_all(the_file)
        # 指定要保存文件的路径
        if not out_file_pth:
            if option_type == "shp":
                new_folder = os.path.join(os.path.dirname(file_pth), 'suiti_result')
                if not os.path.exists(new_folder):
                    os.makedirs(new_folder)
                output_file_path_shp = os.path.join(new_folder, 'suiti_result.shp')
                out_file_pth = output_file_path_shp
            if option_type == "csv":
                output_file_path_csv = os.path.join(os.path.dirname(file_pth), 'suiti_result.csv')
                out_file_pth = output_file_path_csv
        bar()
        
        # 保存处理后的数据到新文件
        save_data(the_file, out_file_pth, option_type=option_type)
        bar()
    return 'done!'

if __name__ == "__main__":
    main('./test_data/适宜性评价/适宜性评价.shp', 'shp')
    # fire.Fire(main)