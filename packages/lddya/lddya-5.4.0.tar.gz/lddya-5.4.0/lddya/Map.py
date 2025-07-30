import pygame as pg
import numpy as np
import time
import os
from typing import Union, List

class Map():
    def __init__(self) -> None:
        self.data = []    # map中的数据
        self.size = 0     # map尺寸

    def load_map_file(self,fp):
        '''
        从map文件中读取地图数据。
        '''
        with open(fp,'r') as f:
                a_1 = f.readlines()
        for i in range(len(a_1)):
            a_1[i] = list(a_1[i].strip('\n'))
        self.data = np.array(a_1).astype(np.int64)
        self.size = self.data.shape[0]
        

    def map_reverse(self,fp='map.dll'):
        '''
        自动读取map地图文件，并翻转数据再储存于原文件中。
        '''
        with open(fp,'r') as f:
            data = f.readlines()
        data.reverse()
        with open(fp,'w') as f:
            f.writelines(data)
    def get_obs_site(self):
        '''
        获取地图中障碍物的坐标。
        '''
        obs_list = np.array(np.where(self.data==1)).T
        return obs_list

    def recognition(self,fig_path,size):
        pg.init()
        pic = pg.image.load(fig_path)
        screen = pg.display.set_mode(pic.get_size())
        print('请点击栅格图的四个顶点！')
        screen.blit(pic,[0,0])
        pg.display.flip()
        dingdian = []   #四个顶点的坐标
        running = True
        while running:
            for i in pg.event.get():
                if i.type == pg.MOUSEBUTTONDOWN:
                    dingdian.append(i.pos)
                    if len(dingdian) == 4:
                        running = False
                        break
                    else:
                        pg.draw.circle(screen,[255,0,0],i.pos,3)
                        pg.display.flip()
        abs_x = max([abs(dingdian[i][0] - dingdian[i+1][0]) for i in range(0,3)])
        abs_y = max([abs(dingdian[i][1] - dingdian[i+1][1]) for i in range(0,3)])
        left_up_pos = dingdian[np.argmin([dingdian[i][0]+dingdian[i][1] for i in range(4)])]
        pg.draw.rect(screen,[0,255,0],[left_up_pos[0],left_up_pos[1],abs_x,abs_y],width=2)
        pg.display.flip()
        self.data = []
        self.record = []
        for y in range(size):    #row
            l1 = []
            l2 = []
            for x in range(size):   #column
                pos_1 = [left_up_pos[0]+(x/size)*abs_x+(abs_x/size)/2,left_up_pos[1]+(y/size)*abs_y+(abs_y/size)/2]
                neigh_pos = [                    [pos_1[0],pos_1[1]-2],
                            [pos_1[0]-2,pos_1[1]],                     [pos_1[0]+2,pos_1[1]],
                                                 [pos_1[0],pos_1[1]+2],
                ]
                key = 1  
                for i in neigh_pos:   
                    r,b,g,a = screen.get_at([int(i[0]),int(i[1])])
                    if max(r,g,b) <60:
                        continue
                    else:
                        key= 0
                        break
                if key == 1:
                    pg.draw.circle(screen,[0,0,255],pos_1,3)
                    l1.append(1)
                else:
                    pg.draw.circle(screen,[255,0,0],pos_1,3)
                    l1.append(0)
                l2.append(pos_1)
                pg.display.flip()
            self.data.append(l1)
            self.record.append(l2)
        print('识别完毕！\n')
        print('请观察界面中的识别结果(红色可通行，蓝色不可通行)，若识别错误请点击目标位置进行修改!\n确认完毕请关闭界面！')
        running = True
        while running:
            for i in pg.event.get():
                if i.type == pg.QUIT:
                    running = False
                elif i.type == pg.MOUSEBUTTONDOWN:
                    self._change(i.pos,screen)


    def _change(self,i_pos,screen):
        print('修改行为:',end=' ')
        dis = 9999
        best_pos = []
        for i in range(len(self.record)):
            for j in range(len(self.record[i])):
                pos_1= self.record[i][j]
                if (pos_1[0]-i_pos[0])**2+(pos_1[1]-i_pos[1])**2<dis:
                    dis = (pos_1[0]-i_pos[0])**2+(pos_1[1]-i_pos[1])**2
                    best_pos = [i,j]
        print('目标位置:',best_pos,end=' ')
        if self.data[best_pos[0]][best_pos[1]] == 0:
            self.data[best_pos[0]][best_pos[1]] = 1 
            pg.draw.circle(screen,[0,0,255],self.record[best_pos[0]][best_pos[1]],3)
            print('结果: 变蓝')
        else:
            self.data[best_pos[0]][best_pos[1]] = 0
            pg.draw.circle(screen,[255,0,0],self.record[best_pos[0]][best_pos[1]],3)
            print('结果: 变红')
        pg.display.flip()

    def path_Identification(self,fig_path:np.ndarray, size:Union[int,List], show_length=False, continuous_path=False,Smoothing_factor=0.5):
        '''
        Function
        --------
        识别图片上的路径数据，结果存于self.data中。
        
        Params
        ------
        fig_path: 栅格图的路径。\n
        size: 栅格图的尺寸，若为int则为正方形栅格图，若为list则为[行数,列数]。\n
        show_length: 是否显示路径长度，默认为False。
        continuous_path: 是否添加连续型路径，默认为False。
        Smoothing_factor: 平滑因子，默认为0.5(sf>=0)。(注意:该参数仅在continuous_path为True时且≠0有效)
        
        Returns
        -------
        None
        '''
        self.map_size = [size,size] if type(size)== int else size
        self.data = []
        pg.init()
        pic = pg.image.load(fig_path)
        screen = pg.display.set_mode(pic.get_size())
        print('请点击栅格图的四个顶点！')
        screen.blit(pic,[0,0])
        pg.display.flip()
        self.dingdian = []   #四个顶点的坐标
        running = True
        while running:
            for i in pg.event.get():
                if i.type == pg.MOUSEBUTTONDOWN:
                    self.dingdian.append(list(i.pos))
                    if len(self.dingdian) == 4:
                        running = False
                        break
                    else:
                        pg.draw.circle(screen,[255,0,0],i.pos,3)
                        pg.display.flip()
        self.abs_x = max([abs(self.dingdian[i][0] - self.dingdian[i+1][0]) for i in range(0,3)])
        self.abs_y = max([abs(self.dingdian[i][1] - self.dingdian[i+1][1]) for i in range(0,3)])
        left_up_pos = self.dingdian[np.argmin([self.dingdian[i][0]+self.dingdian[i][1] for i in range(4)])]
        pg.draw.rect(screen,[0,255,0],[left_up_pos[0],left_up_pos[1],self.abs_x,self.abs_y],width=2)
        pg.display.flip()
        self.record = []
        for y in range(self.map_size[0]):    #row
            l1 = []
            l2 = []
            for x in range(self.map_size[1]):   #column
                pos_1 = [left_up_pos[0]+(x/self.map_size[1])*self.abs_x+(self.abs_x/self.map_size[1])/2,left_up_pos[1]+(y/self.map_size[0])*self.abs_y+(self.abs_y/self.map_size[0])/2]
                neigh_pos = [                    [pos_1[0],pos_1[1]-2],
                            [pos_1[0]-2,pos_1[1]],                     [pos_1[0]+2,pos_1[1]],
                                                 [pos_1[0],pos_1[1]+2],
                ]
                key = 1  
                for i in neigh_pos:   
                    r,b,g,a = screen.get_at([int(i[0]),int(i[1])])
                    if max(r,g,b) <60:
                        continue
                    else:
                        key= 0
                        break
                if key == 1:
                    pg.draw.circle(screen,[0,0,255],pos_1,3)
                else:
                    pg.draw.circle(screen,[255,0,0],pos_1,3)
                l2.append(pos_1)
                pg.display.flip()
            self.record.append(l2)
        print('请点击路径上的节点：')
        running = True
        while running:
            for i in pg.event.get():
                if i.type == pg.QUIT:
                    if (Smoothing_factor > 0) and continuous_path:
                        self.data = self._smooth_path(np.array(self.data), Smoothing_factor)
                    print('Path:',self.data)
                    if show_length == True:
                        self.data = np.array(self.data)
                        length = np.linalg.norm((self.data[1:]-self.data[:-1]),axis=1).sum()
                        print('Length:',length)
                    running = False
                elif i.type == pg.MOUSEBUTTONDOWN:
                    self._add_point(np.array([*i.pos]),screen, continuous_path)


    def _add_point(self,i_pos,screen, continuous_path=False):
        if continuous_path:
            delta_site = i_pos-self.dingdian[np.linalg.norm(self.dingdian,axis=1).argmin()]
            best_pos = (delta_site/np.array([self.abs_y,self.abs_x]))*self.map_size-[0.5,0.5]
            self.data.append(best_pos[::-1])    # 因为测试发现栅格图绘制的路径列表是[x,y]的形式
            print('添加连续型节点:',best_pos[::-1])
            pg.draw.circle(screen,[0,254,0],i_pos,3)
        else:
            dis = 9999
            best_pos = []
            for i in range(len(self.record)):
                for j in range(len(self.record[i])):
                    pos_1= self.record[i][j]
                    if (pos_1[0]-i_pos[0])**2+(pos_1[1]-i_pos[1])**2<dis:
                        dis = (pos_1[0]-i_pos[0])**2+(pos_1[1]-i_pos[1])**2
                        best_pos = [i,j]
            print('添加节点:',best_pos)
            self.data.append(best_pos)
            pg.draw.circle(screen,[0,254,0],self.record[best_pos[0]][best_pos[1]],3)
        pg.display.flip()
        
    def _smooth_path(self, path, smoothing_factor=0.5):
        x = path[:, 0]
        y = path[:, 1]
        # 使用参数化样条插值，s 是平滑因子，数值越大越光滑
        tck, u = splprep([x, y], s=smoothing_factor)  # 调整 s=0~10 之间试试
        u_fine = np.linspace(0, 1, 300)  # 重采样300个点
        x_smooth, y_smooth = splev(u_fine, tck)
        new_path = np.column_stack((x_smooth, y_smooth))
        return new_path
    def _change(self,i_pos,screen):
        print('修改行为:',end=' ')
        dis = 9999
        best_pos = []
        for i in range(len(self.record)):
            for j in range(len(self.record[i])):
                pos_1= self.record[i][j]
                if (pos_1[0]-i_pos[0])**2+(pos_1[1]-i_pos[1])**2<dis:
                    dis = (pos_1[0]-i_pos[0])**2+(pos_1[1]-i_pos[1])**2
                    best_pos = [i,j]
        print('目标位置:',best_pos,end=' ')
        if self.data[best_pos[0]][best_pos[1]] == 0:
            self.data[best_pos[0]][best_pos[1]] = 1 
            pg.draw.circle(screen,[0,0,255],self.record[best_pos[0]][best_pos[1]],3)
            print('结果: 变蓝')
        else:
            self.data[best_pos[0]][best_pos[1]] = 0
            pg.draw.circle(screen,[255,0,0],self.record[best_pos[0]][best_pos[1]],3)
            print('结果: 变红')
        pg.display.flip()
    
    def save(self, fp='map.dll', create_dir=True):
        # 如果开启自动新建目录
        if create_dir:
            dir_path = os.path.dirname(fp)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
        
        # 构造保存数据
        str_data = []
        for i in self.data:
            s = ''
            for j in i:
                s += str(j)
            s += '\n'
            str_data.append(s)

        # 写入文件
        with open(fp, 'w') as f:
            f.writelines(str_data)
            
            
    def gen_random_map(self,p=0.1,size = 20):
        p = 1-p
        self.data = np.random.rand(size,size)
        self.data[self.data<=p] = 0
        self.data[self.data>p] = 1
        self.data[0,0] = 0
        self.data[-1,-1] = 0
        self.data = self.data.astype(np.int64)
        self.size = size



    








