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
        # if self.explore:
        #     self.explore -= 1
        

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
