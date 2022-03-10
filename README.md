# A 5v5 match simulator

## 1.Requirements

* Python 3
* numpy
* gym

## 2.Running the code
First Please create a new folder in the gym installation directory, used to store custom reinforcement learning environments.

The following is an example（in windows terminal）：

```shell
cd 'C:\ProgramData\Anaconda3\Lib\site-packages\gym\envs'
mkdir user
cp (Your download folder).\__init__.py .\user
cp (Your download folder).\matchenv_v1.py .\user
```

After Please Add the following Registration information to the gym init file.

```python
register(
    id="matchenv-v1",
    entry_point="gym.envs.user:matchenv",
    max_episode_steps=100,
)

```

Finally you can use the following code to check the result

```python
import gym
env=gym.make('matchenv-v1')
env.reset()
print(env.step(env.action))
env.render()
env.close()
```

# 5v5匹配simulator
## 1. 环境
* Python 3
* numpy
* gym
## 2.配置

1. 在gym包安装位置新建user文件夹，用于存放自定义环境
参考路径：Anaconda3/Lib/site-packages/gym/envs/

2. 将init.py 和 matchenv_v1.py 复制到user文件夹中

3. 在 anaconda3/lib/site-packages/gym/envs/__init__.py 中进行注册，在最后加入以下内容：

```python
register(
    id="matchenv-v1",
    entry_point="gym.envs.user:matchenv",
    max_episode_steps=100,
)
```
4. 用env.step()方法查看结果

## 3.结果

注：在matchenv-v1.py中有详细的代码注释

在运行之前必须要执行reset方法进行初始化

step方法需要一个参数，缺省值在action属性中已经被定义，或者可以传递一个长度为3的列表，其意义为[赢下一场比赛获得的隐藏分（输一场比赛扣除的隐藏分），赢下一场比赛获得的等级分，胜率过高（过低）补正值]


render方法会返回一个什么都没有的界面，可以使用close方法将其关闭。

以下代码可以模拟20位玩家进行50次匹配，输出为（每位玩家总战绩[win:lose]，每位玩家隐藏分，是否完成匹配，None）并且弹出一个什么都没有的弹窗，5s后关闭。

```python
import gym
import time
env=gym.make('matchenv-v1')
env.reset()
for i in range(50):
    foo=env.step(env.action)

print(foo)
env.render()
time.sleep(5)
env.close()
```