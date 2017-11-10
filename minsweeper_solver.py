# ideas:
# - when no more solution is found, guess a field with high chance of no bomb (number/surrounding 9's)
# - track which fields are already pressed --> dont press them again
# - track which fields are already recognized (number or 0) --> dont scan them again

import numpy as np
from PIL import ImageGrab
import cv2
import time
import win32api, win32con
import random
import map_generator
import map_updater

# flags
SAVE_IMAGES = 0
SHOW_PROCESSED_IMAGE = 0
SHOW_RAW_IMAGE = 0


def get_screen(x1=0,y1=0,x2=0,y2=0):
    if x2>0 and y2>0:
        screen = np.array(ImageGrab.grab(bbox=(x1,y1,x2,y2)))
    else:
        screen = np.array(ImageGrab.grab())
    
    if SHOW_RAW_IMAGE:
        cv2.imshow('color img', screen)    

    return screen

# function for plotting the map
# def print_map(result):
#     for i in range(number_fields):
#         print(result[:][i]) 

def click(x,y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)    

def click_field(x,y,calc_center):
    x_coordinate = 0
    y_coordinate = 0

    for field in calc_center:
        if field[3] == y+1 and field[2] == x+1:
            x_coordinate = field[0]
            y_coordinate = field[1]

    #print('x= ' + str(x) + ', y= ' + str(y))
    click(x_coordinate,y_coordinate)
    

# counts number of fields with specific number (searching_for) which touches the 
# y-pos/x-pos field of number_array
def count_surrounding(number_array, searching_for, x_pos, y_pos, x_fields, y_fields):
    touching_counter = len(get_touching_fields(number_array, searching_for, x_pos, y_pos, x_fields, y_fields))
    return touching_counter                    

# creates a list with x-pos/y-pos coordinates of touching fields with specific number
def get_touching_fields(number_array, searching_for, x_pos, y_pos, x_fields, y_fields):
    found_pos = []
    if y_pos>0 and x_pos>0:
        if number_array[y_pos-1][x_pos-1] == searching_for:
            found_pos.append([y_pos-1,x_pos-1])
    if x_pos>0:
        if number_array[y_pos][x_pos-1] == searching_for:
            found_pos.append([y_pos,x_pos-1])
    if y_pos<y_fields-1 and x_pos>0:
        if number_array[y_pos+1][x_pos-1] == searching_for:
            found_pos.append([y_pos+1,x_pos-1])
    if y_pos>0:
        if number_array[y_pos-1][x_pos] == searching_for:
            found_pos.append([y_pos-1,x_pos]) 
    if y_pos<y_fields-1:
        if number_array[y_pos+1][x_pos] == searching_for:
            found_pos.append([y_pos+1,x_pos])
    if y_pos>0 and x_pos<x_fields-1:
        if number_array[y_pos-1][x_pos+1] == searching_for:
            found_pos.append([y_pos-1,x_pos+1])
    if x_pos<x_fields-1:
        if number_array[y_pos][x_pos+1] == searching_for:
            found_pos.append([y_pos,x_pos+1])
    if x_pos<x_fields-1 and y_pos<y_fields-1:
        if number_array[y_pos+1][x_pos+1] == searching_for:
            found_pos.append([y_pos+1,x_pos+1])  

    return found_pos   

def check_stop_criteria(result):
    stop_crit = True
    for row in result:
        for num in row:
            if num < 9:
                stop_crit = False
                return stop_crit
    return stop_crit

def main():
    [calc_center, distance, y_fields, x_fields] = map_generator.get_centers()

    mines = [[0 for x in range(x_fields)] for y in range(y_fields)]
    not_found_bombs = [[0 for x in range(x_fields)] for y in range(y_fields)]

    x_start=random.randrange(x_fields)
    y_start=random.randrange(y_fields)
    #print('y=' + str(y_start))
    #print('x=' + str(x_start))
    click_field(x_start,y_start,calc_center)    

    counter_x = 0
    counter_y = 0

    last_time = time.time()

    solving_in_progress = True
    while(solving_in_progress):

        result = map_updater.update_map(calc_center, distance)

        print('Loop took {} seconds'.format(time.time()-last_time))
        #print('y: ' + str(counter_y) + ', x: ' + str(counter_x))
        last_time = time.time()
        

        if SHOW_PROCESSED_IMAGE:
            cv2.imshow('processed image', processed_screen)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

        # save field as png
        if SAVE_IMAGES:
            file = 'Extract_fields/field_' + str(counter_y) + '_' + str(counter_x) + '.png'
            cv2.imwrite(file,processed_screen)


        # when a shown number touches the same number of hidden fields, these fields are bombs
        # write the bombs into the result list as 10
        for y in range(y_fields):
            for x in range(x_fields):
                touching_covered_fields = get_touching_fields(result, 9, x, y, x_fields, y_fields)

                if len(touching_covered_fields) == result[y][x]:
                    for element in touching_covered_fields:
                        mines[element[0]][element[1]] = 1

        for y in range(y_fields):
            for x in range(x_fields):
                if mines[y][x] == 1:
                    result[y][x]=10


        # when shown number touches the same number of bombs, you can open all the other covered fields
        for y in range(y_fields):
            for x in range(x_fields):
                touching_bombs = count_surrounding(result, 10, x, y, x_fields, y_fields)

                if touching_bombs == result[y][x]:
                    touch_this = get_touching_fields(result, 9, x, y, x_fields, y_fields)
                    for element in touch_this:
                        click_field(element[1], element[0], calc_center)


        # Lösungsalgo 2 stimmt die ??
        # wenn zwei benachbarte zahlen
        # wenn differenz von außerhalb der schnittmenge der größeren Zahl und die größere zahl
        # minus bereits berührende bombe
        # kleiner gleich der kleineren zahl minus bereits berührender bomben
        # ist, dann öffne alle felder die außerhalb der 
        # schnittmenge der kleineren zahl


        # solving algorithm 1:
        # find neighbours which have the same number minus bombs
        # get coordinates of touching 9's
        # if coordinates of touching 9's from one field are a subset of the coordinates
        # of the touching 9's from the other field
        # all other touching fields can be opened 

        # create list with number of not discovered bombs
        found_candidates = []
        for y in range(y_fields):
            for x in range(x_fields):
                if result[y][x]<9 and result[y][x]>0:
                    not_found_bombs[y][x] = result[y][x] - count_surrounding(result, 10, x, y, x_fields, y_fields)
                else:
                    not_found_bombs[y][x] = result[y][x]

        # find candidates for this solving algo (same number - bombs)
        for y in range(y_fields):
            for x in range(x_fields):
                if not_found_bombs[y][x]<9 and not_found_bombs[y][x]>0:
                    found_candidates.append([y, x])
                    found_candidates.append(get_touching_fields(not_found_bombs, not_found_bombs[y][x], x, y, x_fields, y_fields))

        # check if touching 9's of one field is a subset of the other touching 9's
        for i in range(0,len(found_candidates),2):  
            for element_cand in found_candidates[i+1]:
                part_1 = found_candidates[i]
                part_2 = element_cand

                touching_1 = get_touching_fields(result, 9, part_1[1], part_1[0], x_fields, y_fields)
                touching_2 = get_touching_fields(result, 9, part_2[1], part_2[0], x_fields, y_fields)

                if len(touching_1) > len(touching_2):
                    bigger_touching = touching_1
                    smaller_touching = touching_2
                else:
                    bigger_touching = touching_2
                    smaller_touching = touching_1

                counter_elements = 0
                for element_touch_small in smaller_touching:
                    if element_touch_small in bigger_touching:
                        counter_elements = counter_elements + 1
                if counter_elements == len(smaller_touching):
                    for element_open in bigger_touching:
                        if element_open not in smaller_touching:
                            click_field(element_open[1], element_open[0],calc_center)

        if check_stop_criteria(result):
            solving_in_progress = False


if __name__ == "__main__":
    main()        