# 基于Q-Learning 的FlappyBird AI

在[birdbot](https://github.com/willz/birdbot)实现的FlappyBird基础上训练AI，这个FlappyBird的实现对游戏进行了简单的封装，可以很方便得到游戏的状态来辅助算法实现。同时可以显示游戏界面方便调试，能够看到算法实现的效果。也可以选择关闭游戏界面以及声音，这样游戏仍然能正常运行，一般用于训练阶段，可以减少CPU的占用

实现参考的是SarvagyaVaish的[Flappy Bird RL](http://sarvagyavaish.github.io/FlappyBirdRL/)

## Q-Learning

Q-Learning是强化学习算法中value-based的算法

Q即为Q（s,a）就是在某一时刻的 s 状态下(s∈S)，采取 动作a (a∈A)动作能够获得收益的期望，环境会根据agent的动作反馈相应的回报reward，所以算法的主要思想就是将State与Action构建成一张Q-table来存储Q值，然后根据Q值来选取能够获得最大的收益的动作

| Q-Table | a1       | a2       |
| ------- | -------- | -------- |
| s1      | q(s1,a1) | q(s1,a2) |
| s2      | q(s2,a1) | q(s2,a2) |
| s3      | q(s3,a1) | q(s3,a2) |

### 算法流程

![在这里插入图片描述](https://img-blog.csdnimg.cn/2020122703554185.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzMyODE1ODA3,size_16,color_FFFFFF,t_70)


在更新的过程中，引入了学习速率alpha，控制先前的Q值和新的Q值之间有多少差异被保留

γ为折扣因子，0<= γ<1，γ=0表示立即回报，γ趋于1表示将来回报，γ决定时间的远近对回报的影响程度

详细的Q-Learning过程可以参考下面这篇

[A Painless Q-learning Tutorial (一个 Q-learning 算法的简明教程)](https://blog.csdn.net/itplus/article/details/9361915)

## FlappyBird中应用

### 状态空间

- 从下方管子开始算起的垂直距离
- 从下一对管子算起的水平距离
- 鸟：死或生

![img](https://img-blog.csdnimg.cn/img_convert/213ef34c9129af22c9bb1af354c6569f.png)

### 动作

每一个状态，有两个可能的动作

- 点击一下
- 啥也不干

### 奖励

奖励的机制完全基于鸟是否存活

- **+1**，如果小鸟还活着
- **-1000**，如果小鸟死了

### 流程

伪代码

```
初始化 Q = {};
while Q 未收敛：
    初始化小鸟的位置S，开始新一轮游戏
    while S != 死亡状态：
        使用策略π，获得动作a=π(S) 
        使用动作a进行游戏，获得小鸟的新位置S',与奖励R(S,a)
        Q[S,A] ← (1-α)*Q[S,A] + α*(R(S,a) + γ* max Q[S',a]) // 更新Q
        S ← S'
```

1. 观察Flappy Bird处于什么状态，并执行最大化预期奖励的行动。然后继续运行游戏，接着获得下一个状态s’

2. 观察新的状态s’和与之相关的奖励：+1或者-1000

3. 根据Q Learning规则更新Q阵列

   Q[s,a] ← Q[s,a] + α (r + γ*V(s') - Q[s,a])

4. 设定当前状态为s’，然后重新来过

![在这里插入图片描述](https://img-blog.csdnimg.cn/20201227035602587.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzMyODE1ODA3,size_16,color_FFFFFF,t_70)

## 代码

```python
import pyglet
import random
import pickle
import atexit
import os
from pybird.game import Game

class Bot:
    def __init__(self, game):
        self.game = game
        # constants
        self.WINDOW_HEIGHT = Game.WINDOW_HEIGHT
        self.PIPE_WIDTH = Game.PIPE_WIDTH
        # this flag is used to make sure at most one tap during
        # every call of run()
        self.tapped = False
        
        self.game.play()

        # variables for plan
        self.Q = {}
        self.alpha = 0.7
        self.explore = 100
        self.pre_s = (9999, 9999)
        self.pre_a = 'do_nothing'

        self.absolute_path = os.path.split(os.path.realpath(__file__))[0]
        self.memo = self.absolute_path + '/memo'

        if os.path.isfile(self.memo):
            _dict = pickle.load(open(self.memo))
            self.Q = _dict["Q"]
            self.game.record.iters = _dict.get("iters", 0)
            self.game.record.best_iter = _dict.get("best_iter", 0)

        def do_at_exit():
            _dict = {"Q": self.Q,
                     "iters": self.game.record.iters,
                     "best_iter": self.game.record.best_iter}
            pickle.dump(_dict, open(self.memo, 'wb'))

        atexit.register(do_at_exit)

    # this method is auto called every 0.05s by the pyglet
    def run(self):
        if self.game.state == 'PLAY':
            self.tapped = False
            # call plan() to execute your plan
            self.plan(self.get_state())
        else:
            state = self.get_state()
            bird_state = list(state['bird'])
            bird_state[2] = 'dead'
            state['bird'] = bird_state
            # do NOT allow tap
            self.tapped = True
            self.plan(state)
            # restart game
            print 'iters:',self.game.record.iters,' score:', self.game.record.get(), 'best: ', self.game.record.best_score
            self.game.record.inc_iters()
            self.game.restart()
            self.game.play()

    # get the state that robot needed
    def get_state(self):
        state = {}
        # bird's position and status(dead or alive)
        state['bird'] = (int(round(self.game.bird.x)), \
                int(round(self.game.bird.y)), 'alive')
        state['pipes'] = []
        # pipes' position
        for i in range(1, len(self.game.pipes), 2):
            p = self.game.pipes[i]
            if p.x < Game.WINDOW_WIDTH:
                # this pair of pipes shows on screen
                x = int(round(p.x))
                y = int(round(p.y))
                state['pipes'].append((x, y))
                state['pipes'].append((x, y - Game.PIPE_HEIGHT_INTERVAL))
        return state

    # simulate the click action, bird will fly higher when tapped
    # It can be called only once every time slice(every execution cycle of plan())
    def tap(self):
        if not self.tapped:
            self.game.bird.jump()
            self.tapped = True

    # That's where the robot actually works
    # NOTE Put your code here
    def plan(self, state):
        x = state['bird'][0]
        y = state['bird'][1]
        if len(state['pipes']) == 0:
            if y < self.WINDOW_HEIGHT / 2:
                self.tap()
            return
        h, v = 9999, 9999
        reward = -1000 if state['bird'][2] == 'dead' else 1
        for i in range(1, len(state['pipes']), 2):
            p = state['pipes'][i]
            if x <= p[0] + self.PIPE_WIDTH:
                h = p[0] + self.PIPE_WIDTH - x
                v = p[1] - y
                break
        scale = 10
        h /= scale
        v /= scale
        self.Q.setdefault((h, v), {'tap': 0, 'do_nothing': 0})
        self.Q.setdefault(self.pre_s, {'tap': 0, 'do_nothing': 0})
        tap_v = self.Q[(h, v)]['tap']
        nothing_v = self.Q[(h, v)]['do_nothing']
        self.Q[self.pre_s][self.pre_a] += self.alpha * (reward + max(tap_v, nothing_v) - self.Q[self.pre_s][self.pre_a])
        self.pre_s = (h, v)
        if random.randint(0, self.explore) > 100:
            self.pre_a = "do_nothing" if random.randint(0, 1) else "tap"
        else:
            tap_v = self.Q[self.pre_s]['tap']
            nothing_v = self.Q[self.pre_s]['do_nothing']
            self.pre_a = "do_nothing" if tap_v <= nothing_v else "tap"
        if self.pre_a == 'tap':
            self.tap()
        else:
            pass  

if __name__ == '__main__':
    show_window = True
    enable_sound = False
    game = Game()
    game.set_sound(enable_sound)
    bot = Bot(game)
    def update(dt):
        game.update(dt)
        bot.run()
    pyglet.clock.schedule_interval(update, Game.TIME_INTERVAL)

    if show_window:
        window = pyglet.window.Window(Game.WINDOW_WIDTH, Game.WINDOW_HEIGHT, vsync = False)
        @window.event
        def on_draw():
            window.clear()
            game.draw()
        pyglet.app.run()
    else:
        pyglet.app.run()

```

全部代码见[github仓库](https://github.com/BENULL/FlappyBirdBot)

## 参考

- [Flappy Bird RL](http://sarvagyavaish.github.io/FlappyBirdRL/)
- [如何用简单例子讲解 Q - learning 的具体过程？ - 牛阿的回答 - 知乎]( https://www.zhihu.com/question/26408259/answer/123230350)
- [Q-Learning算法详解](https://blog.csdn.net/qq_30615903/article/details/80739243)