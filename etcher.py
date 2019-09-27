from token import _main

from PIL import Image
import numpy as np

# Parameters

img_path = "2channel_crop.png"
output_name = "2channel_crop"

# (x, y)
offset = (5, 5)
engrave_width = 10

# mm/min
engrave_speed = 300
move_speed = 3000

# Higher resolutions will result in longer gcode and possibly longer time
image_resolution = ()

# row/mm
row_density = 5

# Commands

# G1 F(mm/min) X(mm) Y(mm) Z(mm)
move = "G1 F%d " % engrave_speed

# usually interpreted as an alias for G1, still requires changing speed with F
quick_move = "G0 F%d " % move_speed

# Turn fan on at power S
set_power = "M106 "
laser_off = "M107"

with open("opening.gcode", 'r') as f:
    opening = f.read()

with open("ending.gcode", 'r') as f:
    ending = f.read()


def image_to_gcode():
    gcode = opening

    # Open Image
    im = Image.open(img_path)

    resize_ratio = im.width/engrave_width
    new_size = (int(im.width/resize_ratio), int(im.height/resize_ratio))

    #im = im.resize(new_size, resample=Image.LANCZOS)

    # Rotate to move horizontally rather than vertically
    # im = im.rotate(90, expand=True)

    pixels = np.array(im)

    print(pixels.shape)

    row_dist = 1/row_density

    # Generate g-code
    for y, row in enumerate(pixels):

        for r in range(row_density):
            # Move to next row
            # ToDo snake
            gcode += laser_off + '\n'
            previous_pow = -1

            # next row is at height offset + y pixel
            gcode += quick_move + "X%d Y%f \n" % (offset[0], offset[1] + y + row_dist * r)

            for x, pixel in enumerate(row):
                pow = np.mean(pixel)

                # Init row
                if x == 0:
                    previous_pow = pow
                    continue

                # Wait for a change in power or end of row to issue new commands
                if pow != previous_pow or x == len(row) - 1:

                    # Skip if blank, ie pow == 0
                    if pow > 0:
                        # Move to previous position with previous power
                        gcode += set_power + "S%d \n" % previous_pow
                        gcode += move + "X%d \n" % (offset[0] + x-1)

                    previous_pow = pow





    gcode += ending

    return gcode


if __name__ == "__main__":
    gcode = image_to_gcode()

    with open(output_name + ".gcode", 'w') as outfile:
        outfile.write(gcode)

    print(len(gcode))