import pyglet
import os

class Record:
    def __init__(self):
        # score
        self.best_score = 0
        self.cur_score = 0
        self.best_image = os.path.split(os.path.realpath(__file__))[0] + '/best_image.png'
        self.iters = 1
        self.best_iter = 0

    def get(self):
        return self.cur_score

    def inc(self):
        self.cur_score += 1

    def reset(self):
        self.cur_score = 0

    def save(self):
        if self.cur_score > self.best_score:
            self.best_score = self.cur_score
            self.best_iter = self.iters
            pyglet.image.get_buffer_manager().get_color_buffer().save(self.best_image)

    def inc_iters(self):
        self.iters += 1

    # draw a number image using the digit images. imgs[i] should
    # correspond to digit i
    @staticmethod
    def draw_num(num, imgs, x, y):
        if num == 0:
            s = pyglet.sprite.Sprite(imgs[0], x, y)
            s.draw()
        w = imgs[0].width
        vals = []
        while num:
            r = num % 10
            vals.insert(0, r)
            num /= 10
        seq = []
        batch = pyglet.graphics.Batch()
        for i in range(len(vals)):
            s = pyglet.sprite.Sprite(imgs[vals[i]], x + i * w, y, batch = batch)
            seq.append(s)
        batch.draw()

    @staticmethod
    def get_num_image(num, imgs):
        if num == 0:
            return imgs[0]
        seq = []
        width = 0
        while num:
            r = num % 10
            seq.insert(0, imgs[r])
            width += imgs[r].width
            num /= 10
        ret_img = pyglet.image.Texture.create(width, imgs[0].height)
        w = 0
        for img in seq:
            ret_img.blit_into(img, w, 0, 0)
            w += img.width
        return ret_img

        
