import random
import math
import pyglet
import bird
from pipe import *
from record import *
import resource

class Game:
    # constants
    WINDOW_WIDTH = resource.bg_day.width
    WINDOW_HEIGHT = resource.bg_day.height
    PIPE_WIDTH = resource.pipe_up.width
    PIPE_HEIGHT = resource.pipe_up.height
    PIPE_WIDTH_INTERVAL = 175
    PIPE_HEIGHT_INTERVAL = 100
    PIPE_HEIGHT_OFFSET = PIPE_HEIGHT + PIPE_HEIGHT_INTERVAL
    LAND_HEIGHT = resource.land.height
    TIME_INTERVAL = 0.02

    sound = True

    def __init__(self):
        self.record = Record()

        # sprites
        self.background = pyglet.sprite.Sprite(resource.bg_day, 0, 0)
        self.logo = pyglet.sprite.Sprite(resource.title, 60, 320)
        self.button_play = pyglet.sprite.Sprite(resource.button_play, 20, 140)
        self.button_score = pyglet.sprite.Sprite(resource.button_score, 150, 140)
        self.text_ready = pyglet.sprite.Sprite(resource.text_ready, 50, 350)
        self.tutorial = pyglet.sprite.Sprite(resource.tutorial, 90, 200)
        self.game_over = pyglet.sprite.Sprite(resource.text_game_over, 45, 360)
        self.score_panel = pyglet.sprite.Sprite(resource.score_panel, 28, 220)

        # create land
        self.land = pyglet.sprite.Sprite(resource.land, 0, 0)
        
        self.__setup()

    def __setup(self):
        # create a bird
        self.bird = bird.Bird(resource.bird_gif, 140, 270)
        # create pipes
        self.pipes = []
        y = self.__gen_pipe_pos_y()
        p = Pipe(resource.pipe_up, 350, y)
        self.pipes.append(p)
        p = Pipe(resource.pipe_down, 350, y + Game.PIPE_HEIGHT_OFFSET)
        self.pipes.append(p)

        self.state = 'INIT'
        self.record.reset()

    def set_sound(self, flag):
        Game.sound = flag

    def restart(self):
        self.__setup()

    def play(self):
        self.bird.x = 100
        self.state = 'PLAY'

    def draw(self):
        # draw background
        self.background.draw()
        if self.state == 'INIT':
            # add logo
            self.logo.draw()
            self.button_play.draw()
            self.button_score.draw()
            self.bird.draw()
            self.land.draw()
        elif self.state == 'READY':
            self.text_ready.draw()
            self.tutorial.draw()
            self.bird.set_position(85, 250)
            self.bird.draw()
            self.land.draw()
        elif self.state == 'PLAY' or self.state == 'FAILING':
            self.__draw_pipes()
            self.land.draw()
            self.bird.draw()
            # show current score
            img = Record.get_num_image(self.record.get(), resource.big_nums)
            score = pyglet.sprite.Sprite(img, (Game.WINDOW_WIDTH - img.width) / 2, 400)
            score.draw()
        elif self.state == 'FAILED':
            self.__draw_pipes()
            self.land.draw()
            # show game over
            self.game_over.draw()
            # show score panel
            self.score_panel.draw()
            # show score (right align)
            img = Record.get_num_image(self.record.get(), resource.small_nums)
            x = 240 - img.width
            score = pyglet.sprite.Sprite(img, x, 290)
            score.draw()
            img = Record.get_num_image(self.record.best_score, resource.small_nums)
            x = 240 - img.width
            score = pyglet.sprite.Sprite(img, x, 250)
            score.draw()
            # show buttons
            self.button_play.draw()
            self.button_score.draw()

    def __draw_pipes(self):
        for i in range(0, len(self.pipes), 2):
            pipe = self.pipes[i]
            if pipe.x + pipe.width > 0 and pipe.x <= Game.WINDOW_WIDTH:
                self.pipes[i].draw()
                self.pipes[i + 1].draw()

    def update(self, dt):
        # set the delta to constant, otherwise the game might be unstable due
        # to high CPU load etc.
        dt = Game.TIME_INTERVAL

        # delete the pipe move out of window
        pipe = self.pipes[0]
        if pipe.x + pipe.width < 0:
            self.pipes.pop(0)
            self.pipes.pop(0)
        # always keep 3 pair of pipes
        if len(self.pipes) < 6:
            x = self.pipes[-1].x + Game.PIPE_WIDTH_INTERVAL
            y = self.__gen_pipe_pos_y()
            pipe = Pipe(resource.pipe_up, x, y)
            self.pipes.append(pipe)
            pipe = Pipe(resource.pipe_down, x, y + Game.PIPE_HEIGHT_OFFSET)
            self.pipes.append(pipe)

        if self.state == 'INIT' or self.state == 'READY':
            # move the land
            self.land.x = 0 if self.land.x else -10
        elif self.state == 'PLAY':
            self.bird.update(dt)
            # update pipes
            [pipe.update(dt) for pipe in self.pipes]
            # move the land
            self.land.x = 0 if self.land.x else -10
            self.__calc_score()
            if self.__is_collide():
                if Game.sound:
                    resource.hit_sound.play()
                self.state = 'FAILING'
                self.record.save()
        elif self.state == 'FAILING':
            # the bird is dead, but still need to play the animation
            # that the bird sliding to land
            if self.bird.y > Game.LAND_HEIGHT + 15:
                self.bird.update(dt)
            else:
                self.state = 'FAILED'

    def __calc_score(self):
        for i in range(1, len(self.pipes), 2):
            p = self.pipes[i]
            if (not p.scored) and self.bird.x > p.x:
                self.record.inc()
                p.scored = True
                if Game.sound:
                    resource.point_sound.play()
                return


    def __is_collide(self):
        HALF_BIRD_SIZE = self.bird.height / 2
        # hit the land
        if self.bird.y < Game.LAND_HEIGHT + 15:
            self.bird.y = Game.LAND_HEIGHT + 15
            return True
        # hit the pipe
        for i in range(1, len(self.pipes), 2):
            p = self.pipes[i]
            if self.bird.x <= p.x + Game.PIPE_WIDTH + 15 and \
                self.bird.x + 15 >= p.x and \
                (self.bird.y + 10 >= p.y or \
                self.bird.y <= p.y - Game.PIPE_HEIGHT_INTERVAL + 15):
                return True
        return False

    def __gen_pipe_pos_y(self):
        return random.randint(-120, 30)
