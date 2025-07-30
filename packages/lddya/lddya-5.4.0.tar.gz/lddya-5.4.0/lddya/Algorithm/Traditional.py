import numpy as np
import pandas as pd
import copy
import heapq
from abc import ABC,abstractmethod


class basedTraAlgorithm(ABC):
    def __init__(self,map_data,start ,end) -> None:
        ####   问题类参数  #####
        self.map_data = np.array(map_data).copy()   # 地图数据
        self.map_size = self.map_data.shape[0]      # 地图大小
        self.start =    np.array(start) if start!=None else np.array([0,0])                                # 任务起点
        self.end =      np.array(end)   if end!=None else np.array([self.map_size-1,self.map_size-1])      # 任务终点
        ### 统计类参数   ####
        self.best_way_len = -1     # 最优路径长度
        self.best_way_data = []    # 最优路径节点数据
    
    @abstractmethod
    def run(self):
        pass


################################################## 1 A*算法路径规划 ###########################################
class AStar(basedTraAlgorithm):
    def __init__(self, map_data, start=None, end=None):
        super().__init__(map_data,start,end)
        self.start = tuple(self.start)
        self.end = tuple(self.end)
        self.distance_matrix = np.array([1, 1, 1, 1, 2**0.5, 2**0.5, 2**0.5, 2**0.5])
        self.directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    def heuristic(self, a, b):
        return np.linalg.norm(np.array(a)-b)

    def run(self):
        open_set = []
        heapq.heappush(open_set, (0, self.start))
        came_from = {}
        g_score = {self.start: 0}
        f_score = {self.start: self.heuristic(self.start, self.end)}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == self.end:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(self.start)
                path.reverse()
                self.best_way_len = g_score[self.end]
                self.best_way_data = path
                return path, g_score[self.end]

            for index, direction in enumerate(self.directions):
                neighbor = (current[0] + direction[0], current[1] + direction[1])
                if 0 <= neighbor[0] < self.map_size and 0 <= neighbor[1] < self.map_size and self.map_data[neighbor[0]][neighbor[1]] == 0:
                    tentative_g_score = g_score[current] + self.distance_matrix[index]
                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, self.end)
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None, None
################################################## 2 动态规划算法路径规划 ###########################################

class Dynamic_Programing(basedTraAlgorithm):
    def __init__(self,map_data,start=None,end=None) -> None:
        '''
            Function
            --------
            parameter initilization

            Parameter
            --------
            map_data : 栅格地图数据，   2d矩阵
            start    : 起点坐标，      1*2向量 [y,x]
            end      : 终点坐标，      1*2向量 [y,x]

            Return
            ------
            None
        '''
        super().__init__(map_data,start,end)
        self.relation_matrix = np.zeros_like(self.map_data,dtype = np.int16)   #关系矩阵，标记方向
        self.relation_code_zhi = np.array([1,3,5,7])          #回溯方向代码，放入关系矩阵中
        self.relation_code_xie = np.array([2,4,6,8])
        self.dynamic_matrix  = np.zeros_like(self.map_data)   #动态矩阵，标记需要处理的母节点
        self.dynamic_matrix[self.end[0],self.end[0]] = 1   #初始时，母节点仅有终点
        self.static_matrix   = self.dynamic_matrix.copy()   #静态矩阵，冻结的节点(不进行任何操作)

    
    def run(self):
        while True:
            self.relation_matrix_temp = np.zeros_like(self.relation_matrix)
            self.dynamic_matrix_temp  = np.zeros_like(self.dynamic_matrix) 
            # step 1: 由需要处理的母节点进行扩散
            self.task_matrix = np.zeros_like(self.map_data)
            #self.task_2_matrix = np.zeros(shape=np.array(self.map_data.shape)+2)    #扩大点，就不用考虑边界了，task
            y_1,x_1 = np.where(self.dynamic_matrix==1)
            for k,i in enumerate(y_1):      #直线方向上的更新
                y = y_1[k]
                x = x_1[k]
                neighbours = np.array([
                    [y-1,x],
                    [y,x+1],
                    [y+1,x],
                    [y,x-1],
                ])
                cond_1 = np.logical_and(neighbours[:,0]>=0,neighbours[:,0]<self.map_size)
                cond_2 = np.logical_and(neighbours[:,1]>=0,neighbours[:,1]<self.map_size)
                allowed_index = np.logical_and(cond_1,cond_2)          #约束1：坐标范围
                allowed_rela_code = self.relation_code_zhi[allowed_index]
                allowed_neigh = neighbours[allowed_index]
                allowed_rela_code = allowed_rela_code[self.map_data[allowed_neigh[:,0],allowed_neigh[:,1]]==0] #约束2的code，因为allowed_neigh下一步变了，故要提前处理code，约束3的同理
                allowed_neigh = allowed_neigh[self.map_data[allowed_neigh[:,0],allowed_neigh[:,1]]==0]     #约束2 ： 空白栅格
                allowed_rela_code = allowed_rela_code[self.static_matrix[allowed_neigh[:,0],allowed_neigh[:,1]]==0]
                allowed_neigh = allowed_neigh[self.static_matrix[allowed_neigh[:,0],allowed_neigh[:,1]]==0]  #约束3： 不能是static
                
                a_1 = self.relation_matrix[allowed_neigh[:,0],allowed_neigh[:,1]] == 0  # 没更新的地方,需要判断吗？
                self.relation_matrix_temp[allowed_neigh[a_1][:,0],allowed_neigh[a_1][:,1]] = allowed_rela_code[a_1]
                self.relation_matrix[self.relation_matrix_temp!=0] = self.relation_matrix_temp[self.relation_matrix_temp!=0]
                self.dynamic_matrix_temp[self.relation_matrix_temp!=0] = 1 
            
            self.relation_matrix_temp = np.zeros_like(self.relation_matrix)
            for k,i in enumerate(y_1):      #斜线方向上的更新
                y = y_1[k]
                x = x_1[k]
                neighbours = np.array([
                    [y-1,x+1],
                    [y+1,x+1],
                    [y+1,x-1],
                    [y-1,x-1]
                ])
                cond_1 = np.logical_and(neighbours[:,0]>=0,neighbours[:,0]<self.map_size)
                cond_2 = np.logical_and(neighbours[:,1]>=0,neighbours[:,1]<self.map_size)
                allowed_index = np.logical_and(cond_1,cond_2)
                allowed_rela_code = self.relation_code_xie[allowed_index]
                allowed_neigh = neighbours[allowed_index]
                allowed_rela_code = allowed_rela_code[self.map_data[allowed_neigh[:,0],allowed_neigh[:,1]]==0] #约束2的code，因为allowed_neigh下一步变了，故要提前处理code，约束3的同理
                allowed_neigh = allowed_neigh[self.map_data[allowed_neigh[:,0],allowed_neigh[:,1]]==0]     #约束2 ： 空白栅格
                allowed_rela_code = allowed_rela_code[self.static_matrix[allowed_neigh[:,0],allowed_neigh[:,1]]==0]
                allowed_neigh = allowed_neigh[self.static_matrix[allowed_neigh[:,0],allowed_neigh[:,1]]==0]  #约束3： 不能是static
                a_1 = self.relation_matrix[allowed_neigh[:,0],allowed_neigh[:,1]] == 0  # 没更新的地方,需要判断吗？
                self.relation_matrix_temp[allowed_neigh[a_1][:,0],allowed_neigh[a_1][:,1]] = allowed_rela_code[a_1] 
                self.relation_matrix[self.relation_matrix_temp!=0] = self.relation_matrix_temp[self.relation_matrix_temp!=0]
                self.dynamic_matrix_temp[self.relation_matrix_temp!=0] = 1 
            
            
            self.dynamic_matrix = self.dynamic_matrix_temp.copy()   #更新下一轮的母节点(动态矩阵)
            self.static_matrix[self.dynamic_matrix!=0] = 1   #本轮的母节点全部冻结
            if self.static_matrix[self.start[0],self.start[1]] !=0:
                print('路径规划完成！')
                self._translate()
                break


    def _translate(self):
        grid = self.start.copy()
        self.best_way_data.append(grid)
        while True:
            change_matrix = np.array([
                [1,0],
                [1,-1],
                [0,-1],
                [-1,-1],
                [-1,0],
                [-1,1],
                [0,1],
                [1,1]
            ])

            grid = grid+change_matrix[self.relation_matrix[grid[0],grid[1]]-1]
            if 0 in change_matrix[self.relation_matrix[grid[0],grid[1]]-1].tolist():
                self.best_way_len += 1
            else:
                self.best_way_len += 2**0.5
            self.best_way_data.append(grid)
            if (grid == self.end).all():
                self.best_way_data = np.array(self.best_way_data)
                break
        
