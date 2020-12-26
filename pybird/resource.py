import pyglet
import os

dir = os.path.split(os.path.realpath(__file__))[0]
pyglet.resource.path = [os.path.join(dir, 'res')]
pyglet.resource.reindex()

atlas_file = pyglet.resource.file('atlas.txt', 'rb')
res_img = pyglet.resource.image('atlas.png')

for line in atlas_file:
    cols = line.split(' ')
    x = int(round(res_img.width * float(cols[3])))
    # pyglet's y axis is from down to up
    y = res_img.height - int(round(res_img.height * float(cols[4]))) -int(cols[2])
    vars()[cols[0]] = res_img.get_region(x, y, int(cols[1]), int(cols[2]))

def center_image_anchor(img):
    img.anchor_x = img.width / 2
    img.anchor_y = img.height / 2
    return img

bird_seq = [center_image_anchor(img) for img in [bird0_0, bird0_1, bird0_2]]
bird_gif = pyglet.image.Animation.from_image_sequence(bird_seq, 0.2)

# group the big digit picture to a list
# NOTE the digit picture in the list should be the ImageData type instead of
#      TextureRegion, for TextureRegion CANNOT blit into a larger image
big_nums = [vars()['font_0' + str(48 + i)].get_image_data() for i in range(10)]
small_nums = [vars()['number_score_0' + str(i)].get_image_data() for i in range(10)]

# sound file
tap_sound = pyglet.resource.media('sfx_wing.wav', streaming = False)
point_sound = pyglet.resource.media('sfx_point.wav', streaming = False)
hit_sound = pyglet.resource.media('sfx_hit.wav', streaming = False)
