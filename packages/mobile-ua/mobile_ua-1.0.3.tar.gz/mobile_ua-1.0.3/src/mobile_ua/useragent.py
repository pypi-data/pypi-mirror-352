import os
import pandas as pd
import numpy as np
current_path = os.path.dirname(os.path.abspath(__file__))
ua_array = pd.read_pickle(current_path + "/UA.pkl")
def random_ua():
    """
    获取随机的ua
    """
    ua_ls = np.random.choice(ua_array,1)
    return ua_ls[0]

def get_ua(index=0):
    """
    获取指定索引的ua
    """
    ua_ls = np.random.choice(ua_array, index)
    return ua_ls[0]

if __name__ == '__main__':
    ua = random_ua()
    print(ua)