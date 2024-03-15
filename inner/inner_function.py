'''
Author: Mr.Car
Date: 2024-01-07 23:07:27
'''
def auto_transfer(x, rule_strs):
    try:
        for name, row in rule_strs.iterrows():
            if eval(name,{'x' : x}):
                return row["inner_name"]
        return 0 # 这里要好好考虑一下
    except TypeError as e:
        raise TypeError(x, name, '数据与规则不匹配') from e