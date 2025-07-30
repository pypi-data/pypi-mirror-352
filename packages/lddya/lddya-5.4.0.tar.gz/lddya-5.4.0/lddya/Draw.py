import matplotlib.pyplot as plt
import matplotlib.patches as pat
import matplotlib.ticker as ticker
import numpy as np




class ShanGeTu():
    def __init__(self,map_data,x_label = '',y_label = '',x_major=1, y_major=1,obs_color = "k",edge_color = 'k') -> None:
        self.map_size = np.array([*map_data.shape])  # 获取地图的尺寸
        default_size = np.array([7, 7])  # 默认图形大小
        self.fig = plt.figure(figsize=default_size*(self.map_size[::-1]/max(self.map_size[::-1])))
        self.ax1 = self.fig.add_subplot(1,1,1)
        self.ax1.set_xbound(0,len(map_data))
        self.ax1.set_ybound(0,len(map_data))
        rect_pat = []
        for ki,i in enumerate(map_data):
            for kj,j in enumerate(i):
                if j == 1:
                    rect_pat.append(pat.Rectangle((kj,ki),1,1,color = obs_color))
                else:
                    rect_pat.append(pat.Rectangle((kj,ki),1,1,fill = False,edgecolor =edge_color,linewidth = 1))
        for i in rect_pat:
            self.ax1.add_patch(i)
        self.ax1.set_xlabel(x_label)
        self.ax1.set_ylabel(y_label)
        # 显示刻度标签
        self.ax1.set_xticks(np.array([1] + list(np.arange(x_major, map_data.shape[1] + 1, x_major)))-0.5)
        self.ax1.set_yticks(np.array([1] + list(np.arange(y_major, map_data.shape[0] + 1, y_major)))-0.5)
        # 显示刻度标签，从 1 开始，后续为指定间隔的倍数
        self.ax1.set_xticklabels([1] + list(np.arange(x_major, map_data.shape[1] + 1, x_major)))
        self.ax1.set_yticklabels([1] + list(np.arange(y_major, map_data.shape[0] + 1, y_major)))
        self.show_legend = False



    def draw_way(self, way_data, style_dict):
        """
        绘制路径，接受所有 plt.plot 支持的参数，通过字典解包方式传入。

        Parameters
        ----------
        way_data : list or np.ndarray
            路径点坐标，格式为[y, x]。
        style_dict : dict
            所有 plt.plot 支持的参数，例如 color、linestyle、marker、label、linewidth 等。
        """
        way_data = np.array(way_data)

        if 'label' in style_dict:
            self.show_legend = True

        self.ax1.plot(
            way_data[:, 1] + 0.5,
            way_data[:, 0] + 0.5,
            **style_dict
        )
    
    

    def add_obstacles(self, positions, color):
        """
        添加自定义障碍物，可指定颜色和图例名称。

        Parameters:
        -----------
        positions: List of [y, x] 坐标
        color: 填充颜色
        label: 图例文字（可选）
        """
        for pos in positions:
            y, x = pos
            self.ax1.add_patch(pat.Rectangle((x, y), 1, 1, color=color)) 
 
    def show(self):
        if self.show_legend:
            self.ax1.legend()
        plt.show()
    
    def save(self,filename = 'figure.jpg'):
        if self.show_legend:
            self.ax1.legend()
        plt.savefig(filename)
    

class IterationGraph():
    def __init__(self, data_list, style_dict_list, point_interval=1) -> None:
        '''
            Function
            --------
            绘制迭代图。
            
            Params
            -------
            data_list     : 迭代数据列表，列表中的数据为一维数组。
            style_dict_list : 线条样式列表，每个元素皆为字典，支持plot原生参数如color、linestyle、marker、label、linewidth 等。
            point_interval : 点间隔，默认1。

            Return
            ------
            None
        '''
        self.fig, self.ax = plt.subplots()
        self.data_list = data_list  # 存储数据以供后续使用
        
        for i in range(len(data_list)):
            x_values = range(len(data_list[i])) 
            self.ax.plot(
                x_values[::point_interval],
                data_list[i][::point_interval],
                **style_dict_list[i])


    def set_x_axis(self, label='x', start=None, major=1, offset=0):
        '''
            Function
            --------
            设置 x 轴的标签和刻度。
            
            Params
            -------
            xlabel     : x轴标签，默认“x”。
            x_start    : x轴起始值，默认None,即自动。
            x_major    : x轴主刻度间隔，默认1，当x_start不为None时生效。
            x_offset   : x轴偏移量，默认0，当x_start不为None时生效。

            Return
            ------
            None
        '''
        self.ax.set_xlabel(label)
        if start != None:   
            #self.ax.set_xticks(list(np.arange(start, len(self.data_list[0]), major)))
            self.ax.set_xticks([start]+list(np.arange(major-offset, len(self.data_list[0]), major)))
            self.ax.set_xticklabels([start+offset]+list(np.arange(major, len(self.data_list[0])+offset, major)))

    def set_y_axis(self, label='y', start=None, major=1, offset=0):
        '''
            Function
            --------
            设置 y 轴的标签和刻度。
            
            Params
            -------
            ylabel     : y轴标签，默认“y”。
            y_start    : y轴起始值，默认0。
            y_major    : y轴主刻度间隔，默认1默认1，当x_start不为None时生效。
            y_offset   : y轴偏移量，默认0，当x_start不为None时生效。。

            Return
            ------
            None
        '''
        self.ax.set_ylabel(label)
        
        # 设置 y 轴刻度（根据数据动态调整）
        if start != None:   
            self.ax.set_yticks(list(np.arange(start, len(self.data_list[0]), major)))
            self.ax.set_yticklabels(list(np.arange(start, len(self.data_list[0]), major) + offset))


    def show(self):
        plt.show()

    def save(self, figname='figure.jpg'):
        self.fig.savefig(figname)


class PlotStyleGenerator:
    def __init__(self):
        # 可直接用于 plt.plot 的参数组合
        self.styles = [
            {"color": "red",         "linestyle": "-", "marker": "o"},
            {"color": "black",       "linestyle": "-", "marker": "<"},
            {"color": "magenta",     "linestyle": "-", "marker": "."},
            {"color": "blue",        "linestyle": "-", "marker": "d"},
            {"color": "olive",       "linestyle": "-", "marker": "*"},
            {"color": "teal",        "linestyle": "-", "marker": ">"},
            {"color": "saddlebrown", "linestyle": "-", "marker": "s"},
            {"color": "lime",        "linestyle": "-", "marker": "p"},
            {"color": "gray",        "linestyle": "-", "marker": "h"},
            {"color": "deeppink",    "linestyle": "-", "marker": "^"},
            {"color": "cyan",        "linestyle": "-", "marker": "v"},
            {"color": "turquoise",   "linestyle": "-", "marker": ">"},
            {"color": "darkviolet",  "linestyle": "-", "marker": "v"},
            {"color": "peru",        "linestyle": "-", "marker": ">"},
            {"color": "tomato",      "linestyle": "-", "marker": "s"},
            {"color": "maroon",      "linestyle": "-", "marker": "^"},
        ]

    def get_styles(self, n=None, shuffle=True):
        """
        返回前n个（或全部16）plot() 兼容样式组合，如：
        {'color': 'red', 'linestyle': '-', 'marker': 'o'}
        """
        styles = self.styles.copy()
        if shuffle:
            np.random.shuffle(styles)
        if n is None or n > len(styles):
            return styles
        return styles[:n]