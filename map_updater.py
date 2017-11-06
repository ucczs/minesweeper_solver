# done: get infos about center points of map elements (map generator)

# done: get a screen shot

# done: extract field by field

# identify number with contours, approxPolyDP, arcLenght (?)

# generate list of map which represents all numbers

import cv2
import map_generator

SAVE_FIELD = 1

def update_map():
    counter = 0
    
    [calc_center, distance] = map_generator.get_centers()
    
    screen = map_generator.get_screen()

    for center in calc_center:
        top_corner_x = int(center[0]+0.25*distance)
        top_corner_y = int(center[1]+0.325*distance)
        bottom_corner_x = int(center[0]-0.25*distance)
        bottom_corner_y = int(center[1]-0.325*distance)

        part_screen = screen[bottom_corner_y:top_corner_y, bottom_corner_x:top_corner_x]



        if SAVE_FIELD:
            counter = counter +1
            filename = 'D:/GitHub/minesweeper_solver/DEBUG/part_pic_' + str(counter) + '.jpg'
            cv2.imwrite(filename,part_screen)



if __name__ == "__main__":
    update_map()