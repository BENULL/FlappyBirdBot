import pyglet

class Pipe(pyglet.sprite.Sprite):
    SPEED = 110 
    def __init__(self, *args, **kwargs):
        super(Pipe, self).__init__(*args, **kwargs)
        self.scored = False

    def update(self, dt):
        # bird only moves up and down, so the speed is the y speed
        self.x -= Pipe.SPEED * dt
