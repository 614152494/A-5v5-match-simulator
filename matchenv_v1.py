# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 19:44:28 2022

@author: SSJ
"""
import numpy as np
import itertools
import time
#先定义一些函数
from gym.envs.classic_control import rendering
import gym
import time
def choice_player_type(): #此函数用于生成玩家种类
    type_list=[1,2,3,4,5]
    k=np.random.choice(type_list,p=[0.6,0.1,0.28,0.01,0.01])
    return k
    
def Combinations(alist,a): # 这里输入一个列表，可以求其所有排列组合的值
    C=list(itertools.combinations(alist,a)) 
    return C
    
def list_diff(minuend,subtractor): #求两个列表的差值
    diff = list(set(minuend) - set(subtractor))
    return diff

class matchenv(gym.Env):
    def player_type(self,i):
        # type 1 玩家 休闲玩家，不关心胜负
        # type 2 玩家 以提升自己段位为目标
        # type 3 玩家 有着较强的胜负欲,输了就不玩了
        # type 4 玩家 修罗牌浪，大概率赢
        # type 5 玩家 演员，每次都会大概率输
        type_list=list()
        for j in range(i):
            type_list.append(choice_player_type())
        return type_list
    def __init__(self):
        #初始化环境
        np.random.seed(1)
        self.playernum=20
        self.player=list(range(self.playernum)) # 按顺序生成玩家
        self.hidden_points=list(np.random.randn(self.playernum)) # 随机生成隐藏分，其服从正态分布
        self.player_level=list(np.random.randint(low=-50,high=50,size=20))#随机生成等级分
        self.result=[] #保存每个player赢和输的总次数
        self.player_type=[]#给每个player生成种类
        for i in range(self.playernum):
            k=[0,0] #[win,lose]
            self.result.append(k)
            self.player_type.append(choice_player_type())
        self.dic_level=dict(zip(self.player,self.player_level))
        self.dic_points=dict(zip(self.player,self.hidden_points))
        
        
        #这里是可以调节的预设定参数
        
        self.action=[0.005,0.7,200]

        
        self.viewer=None
        
    def get_min_level_Team(self,player,dic_level):#获取等级分最小的一个队伍
        all_C=list(Combinations(player,5))
        all_level=list()
        for i in all_C:
            rate=sum(list(map(lambda x:dic_level[x],list(i))))
            all_level.append(rate)
        team=list(all_C[all_level.index(min(all_level))])
        return team
    #在现实中大概率也是等级分低的两只队伍匹配
    
    
    # 获取匹配结果序列，用于计算胜负
    def get_match_list(self,player):
        match_list=[]
        flag=0
        while True:
            if flag==self.playernum:
                break
            else:
                a=self.get_min_level_Team(player,self.dic_level)
                match_list.append(a)
                player=list_diff(player,a)
                flag=flag+5
        return match_list
    
    def hiddenscore_revision(self):
        low_position=list() #这里用表格记录被修改隐藏分玩家
        high_position=list()
        for k in self.hidden_points:
            if k<-1:# 隐藏分太低
                po=self.hidden_points.index(k)
                low_position.append(po)
                self.player_level[po]=self.player_level[po]+self.correction_pts
                self.dic_level[po]=self.dic_level[po]+self.correction_pts
            if k>1.5:#隐藏分太高
                po=self.hidden_points.index(k)
                high_position.append(po)
                self.player_level[po]=self.player_level[po]-self.correction_pts
                self.dic_level[po]=self.dic_level[po]-self.correction_pts
        return low_position,high_position
    
    def hiddenscore_recovery(self,low_position,high_position):
        for i in high_position:
            self.player_level[i]=self.player_level[i]+self.correction_pts
            self.dic_level[i]=self.dic_level[i]+self.correction_pts
        for j in low_position:
            self.player_level[j]=self.player_level[j]-self.correction_pts
            self.dic_level[j]=self.dic_level[j]-self.correction_pts
    
    
    def step(self,action):
        #action 这里设置为一个列表
        #state : 现有玩家进行一次匹配，计算胜负结果
        #先获取matchlist
        
        self.hidden_pts=action[0]
        self.level_pts=action[1]
        self.correction_pts=action[2]
        
        matchlist=self.get_match_list(self.player)
        isFinish=True
        
        #如果匹配人数不能被5整除
        
        if len(self.player)%5 !=0:
            isFinish=False
            raise ValueError
        
        while len(matchlist):
            
            # 这里要先进行胜率平衡设置
            
            low_position,high_position=self.hiddenscore_revision()
            
            #在胜率平衡之后，进行match，计算胜负
            
            a=matchlist.pop(0)#弹出列表的第一个值
            b=matchlist.pop(0)
            
            
            
            a_rate=sum(list(map(lambda x:self.dic_level[x],a)))
            b_rate=sum(list(map(lambda x:self.dic_level[x],b)))
            
            
            #将平衡后的各项分值修正
            
            self.hiddenscore_recovery(low_position,high_position)
            
            #计算胜负概率，并随机抽取胜负，认为等级分高的队伍获胜概率比较大
            
            pa=abs(a_rate)/(abs(a_rate)+abs(b_rate))
            pb=1-pa
            
            #这里重新设计随机数来抽样
            np.random.seed(int(time.time()))
            
            a_win=np.random.choice([1,0],p=(pa,pb))
            #以下为胜负奖励
            if a_win:
                for i in a:
                    self.dic_points[i]=self.dic_points[i]+self.hidden_pts
                    self.hidden_points[i]=self.hidden_points[i]+self.hidden_pts
                    self.dic_level[i]=self.dic_level[i]+self.level_pts
                    self.player_level[i]=self.player_level[i]+self.level_pts
                    self.result[i][0]=self.result[i][0]+1
                for i in b:
                    self.dic_points[i]=self.dic_points[i]-self.hidden_pts
                    self.hidden_points[i]=self.hidden_points[i]-self.hidden_pts
                    self.dic_level[i]=self.dic_level[i]-self.level_pts
                    self.player_level[i]=self.player_level[i]-self.level_pts
                    self.result[i][1]=self.result[i][1]+1
            else:
                for i in b:
                    self.dic_points[i]=self.dic_points[i]+self.hidden_pts
                    self.hidden_points[i]=self.hidden_points[i]+self.hidden_pts
                    self.dic_level[i]=self.dic_level[i]+self.level_pts
                    self.player_level[i]=self.player_level[i]+self.level_pts
                    self.result[i][0]=self.result[i][0]+1
                for i in a:
                    self.dic_points[i]=self.dic_points[i]-self.hidden_pts
                    self.hidden_points[i]=self.hidden_points[i]-self.hidden_pts
                    self.dic_level[i]=self.dic_level[i]-self.level_pts
                    self.player_level[i]=self.player_level[i]-self.level_pts
                    self.result[i][1]=self.result[i][1]+1
        
        # 返回执行一次动作结果，反馈float值，match是否执行成功，info
        return self.result,self.hidden_points,isFinish,None
    
    
    
    #重置环境
    def reset(self):
        np.random.seed(1) 
        self.playernum=20
        self.player=list(range(self.playernum)) # 按顺序生成玩家
        self.hidden_points=list(np.random.randn(self.playernum)) # 随机生成隐藏分，其服从正态分布
        self.player_level=list(np.random.randint(low=-50,high=50,size=20))#随机生成等级分
        self.result=[] #保存每个player赢和输的总次数
        self.player_type=[]#给每个player生成种类
        for i in range(self.playernum):
            k=[0,0] #[win,lose]
            self.result.append(k) 
            self.player_type.append(choice_player_type())
        self.dic_level=dict(zip(self.player,self.player_level))
        self.dic_points=dict(zip(self.player,self.hidden_points))
        
    def render(self,mode='human'):
        screen_width=600
        screen_height=600
        if self.viewer is None:
            self.viewer = rendering.Viewer(screen_width,screen_height)
            #rendering.make_circle(40)
            time.sleep(5)
            #self.viewer.close()
        return self.viewer.render(return_rgb_array= mode =='rgb_array')
    
    def close(self):
        if self.viewer:
            self.viewer.close()

# env=matchenv()
# print(env.player_type)