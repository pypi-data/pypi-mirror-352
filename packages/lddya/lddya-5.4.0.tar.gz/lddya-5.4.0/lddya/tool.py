import datetime
import pandas as pd
import numpy as np
import os


class Clock():
    def __init__(self):
        self.start_time = 0
        self.end_time = 0

    def start(self):
        self.start_time = datetime.datetime.now()

    def end(self):
        self.end_time = datetime.datetime.now()
        self.delta_t = self.end_time - self.start_time
    
    def get_delta(self):
        return self.delta_t.seconds+self.delta_t.microseconds*(10**(-6))
    
    def show(self):
        print('The program runs for ',self.delta_t,' microsecond')

class DataOperater():
    def __init__(self):
        pass
    
    
    def save_to_excel(self, data, filename, index=False, header=False):
        '''
        Function
        ---------
        将给定数据保存到Excel文件中。
        
        Params
        -------
 
        data : list or numpy.ndarray
            要保存的数据，可以是一维或二维列表或numpy数组。一维数据将被转换为单行的二维格式。
        filename : str
            Excel文件的路径和名称，用于保存数据。
        index : bool or list of str, 默认 False
            是否写出行名。如果给出了 string 列表，则假定它是行名的别名。
        header : bool or list of str, 默认 False
            是否写出列名。如果给出了 string 列表，则假定它是列名的别名。

            
        Raises
        -------
        TypeError
            如果输入数据不是列表或numpy数组。
        
        Notes
        -------
        - 如果文件名中指定的目录不存在，将自动创建。
        - 数据在保存之前会被转换为pandas DataFrame，以确保与Excel格式兼容。
            
        Example
        --------
        >>> save_to_excel([[1, 2, 3], [4, 5, 6]], "output.xlsx", index=False, header=False)
        '''

        # 检查data类型，确保其是一个一维或二维的列表或np矩阵
        if isinstance(data, (list, np.ndarray)):
            # 将数据转换为numpy数组，以确保统一处理
            data = np.array(data)
            
            # 如果数据是一维列表或数组，转换为二维（单列）
            if data.ndim == 1:
                data = data.reshape(1, -1)
                
                # 确保目录存在，不存在则创建
            directory = os.path.dirname(filename)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # 使用pandas将数据转换为DataFrame
            df = pd.DataFrame(data)
            
            # 保存为Excel文件
            if type(index) == bool:
                df.to_excel(filename, index=index, header=header)
            else if type(index) == list:
                df.to_excel(filename, index=True, header=header, index_label=index)
            print(f"Data has been saved to {filename}")
        else:
            raise TypeError("Input data must be a list or numpy array!")
        
    def read_excel(self, filename,row_index=None,column_index=None):
        '''
        Function
        ---------
        读取 Excel 文件并将其内容转换为 NumPy 数组。

        Params
        ----------
        filename : str 
            要读取的 Excel 文件的路径。
        row_index : int, optional
            要用作索引列的行的索引。默认为 None。
        column_index : int, optional
            要用作标题的行的索引。默认为 None。

        Returns
        -------
        data: numpy.ndarray
            一个 NumPy 数组，其中包含 Excel 文件中的数据。

        Raises
        --------
        FileNotFoundError
            如果指定的文件不存在。
        Exception
            对于文件读取过程中发生的任何其他错误。

        Note
        -----
        - 此函数使用 pandas 读取 Excel 文件。
        - 如果 'header=None'，则第一行将不会被视为列名。
        '''
        try:
            # 使用pandas读取Excel文件
            df = pd.read_excel(filename,index_col=row_index, header=column_index)  # header=None表示不把第一行当作列名
            # 将DataFrame转换为numpy数组
            data = df.to_numpy()
            return data
        except FileNotFoundError:
            print(f"Error: The file {filename} does not exist.")
        except Exception as e:
            print(f"An error occurred: {e}")