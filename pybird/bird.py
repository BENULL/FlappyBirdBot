import pyglet
import resource

class Bird(pyglet.sprite.Sprite):
    GRAVITY_ACC = 700
    ANGULAR_ACC = 350

    def __init__(self, *args, **kwargs):
        super(Bird, self).__init__(*args, **kwargs)
        self.speed = 0
        self.ang_speed = 0
        self.jumped = False

    def update(self, dt):
        from game import Game
        # bird only moves up and down, so the speed is the y speed
        self.speed += Bird.GRAVITY_ACC * dt
        self.ang_speed += Bird.ANGULAR_ACC * dt
        if self.jumped:
            self.speed = -200
            self.ang_speed = -400
            if Game.sound:
                resource.tap_sound.play()
        self.y -= self.speed * dt
        self.rotation += self.ang_speed * Game.TIME_INTERVAL
        if self.y > Game.WINDOW_HEIGHT:
            self.y = Game.WINDOW_HEIGHT
            self.speed = 0
        if self.rotation < -20:
            self.rotation = -20
            self.ang_speed = 0
        if self.rotation > 90:
            self.rotation = 90
        self.jumped = False

    def rotate(self, dt):
        self.rotation += self.ang_speed * dt

    # tapping the screen, the bird will jump up
    def jump(self):
        self.jumped = True


        

