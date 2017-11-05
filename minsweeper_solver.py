# optimierung:
# bessere Lösungsalgorithmen
# wenn es gar nicht mehr geht raten
# performance verbessern (gesamtes feld scannen und daraus infos extrahieren)
# verschiedene spielfeldgrößen möglich
# desktop automatisch scannen nach spielfeld
# größe dynamischer machen


import numpy as np
from PIL import ImageGrab
import cv2
import time
import win32api, win32con
import random

# flags
SAVE_IMAGES = 0
SHOW_PROCESSED_IMAGE = 0
SHOW_RAW_IMAGE = 0

field_x1 = 227
field_x2 = 285
field_y1 = 155
filed_y2 = 214

x_size = 56.5
y_size = 56.5

number_fields = 9
correlation_res_1 = [[0 for x in range(number_fields)] for y in range(number_fields)] 
correlation_res_2 = [[0 for x in range(number_fields)] for y in range(number_fields)] 
correlation_res_3 = [[0 for x in range(number_fields)] for y in range(number_fields)] 
correlation_res_4 = [[0 for x in range(number_fields)] for y in range(number_fields)] 
correlation_res_5 = [[0 for x in range(number_fields)] for y in range(number_fields)] 

result = [[0 for x in range(number_fields)] for y in range(number_fields)] 
mines = [[0 for x in range(number_fields)] for y in range(number_fields)]
not_found_bombs = [[0 for x in range(number_fields)] for y in range(number_fields)]

def get_screen(x1=0,y1=0,x2=0,y2=0):
    if x2>0 and y2>0:
        screen = np.array(ImageGrab.grab(bbox=(x1,y1,x2,y2)))
    else:
        screen = np.array(ImageGrab.grab())
    
    if SHOW_RAW_IMAGE:
        cv2.imshow('color img', screen)    

    return screen

# function for plotting the map
def print_map(result):
    for i in range(number_fields):
        print(result[:][i]) 

# process image:
# convert colour space and define if the field is hidden or already opened
# process image with Canny operator
def process_img(original_img):
    processed_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)

    # get color value and decide if field is open or closed
    color_value = processed_img[int(y_size/2),int(x_size/4)]
    if color_value[-1] < 200:
        field_type = 9
    else:
        field_type = 0

    if SHOW_RAW_IMAGE:
        cv2.imshow('color img', processed_img)

    processed_img = cv2.Canny(processed_img, threshold1=50, threshold2=500)
    return processed_img, field_type

def click(x,y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)    

def click_field(x,y):
    y_coordinate = int(field_y1+15+y_size*y)
    x_coordinate = int(field_x1+15+x_size*x)
    click(x_coordinate,y_coordinate)
    print('x= ' + str(x) + ', y= ' + str(y))
    #time.sleep(1)

# counts number of fields with specific number (searching_for) which touches the 
# y-pos/x-pos field of number_array
def count_surrounding(number_array, searching_for, x_pos, y_pos):
    touching_counter = len(get_touching_fields(number_array, searching_for, x_pos, y_pos))
    return touching_counter                    

# creates a list with x-pos/y-pos coordinates of touching fields with specific number
def get_touching_fields(number_array, searching_for, x_pos, y_pos):
    found_pos = []
    if y_pos>0 and x_pos>0:
        if number_array[y_pos-1][x_pos-1] == searching_for:
            found_pos.append([y_pos-1,x_pos-1])
    if x_pos>0:
        if number_array[y_pos][x_pos-1] == searching_for:
            found_pos.append([y_pos,x_pos-1])
    if y_pos<number_fields-1 and x_pos>0:
        if number_array[y_pos+1][x_pos-1] == searching_for:
            found_pos.append([y_pos+1,x_pos-1])
    if y_pos>0:
        if number_array[y_pos-1][x_pos] == searching_for:
            found_pos.append([y_pos-1,x_pos]) 
    if y_pos<number_fields-1:
        if number_array[y_pos+1][x_pos] == searching_for:
            found_pos.append([y_pos+1,x_pos])
    if y_pos>0 and x_pos<number_fields-1:
        if number_array[y_pos-1][x_pos+1] == searching_for:
            found_pos.append([y_pos-1,x_pos+1])
    if x_pos<number_fields-1:
        if number_array[y_pos][x_pos+1] == searching_for:
            found_pos.append([y_pos,x_pos+1])
    if x_pos<number_fields-1 and y_pos<number_fields-1:
        if number_array[y_pos+1][x_pos+1] == searching_for:
            found_pos.append([y_pos+1,x_pos+1])  

    return found_pos   

# Load templates of numbers
template_1 = cv2.imread('Templates/1.png',0)
template_2 = cv2.imread('Templates/2.png',0)
template_3 = cv2.imread('Templates/3.png',0)
template_4 = cv2.imread('Templates/4.png',0)
template_5 = cv2.imread('Templates/5.png',0)

x_start=random.randrange(9)
y_start=random.randrange(9)
print(y_start)
print(x_start)
click_field(x_start,y_start)

while(True):
    counter_x = 0
    counter_y = 0

    last_time = time.time()
    while(True):
        
        # each field
        screen = get_screen(227+counter_x*x_size,155+y_size*counter_y,285+counter_x*x_size,214+y_size*counter_y)

        # all fields
        #screen = get_screen((227,157,733,665)
        # links [0]  rechts [2]
        # oben [1]  unten [3]

        # process image and determine if field is still covered (9) or 0 bombs
        processed_screen, field_cat = process_img(screen)

        result[counter_y][counter_x] = field_cat

        #print('Loop took {} seconds'.format(time.time()-last_time))
        #print('y: ' + str(counter_y) + ', x: ' + str(counter_x))
        last_time = time.time()
        

        if SHOW_PROCESSED_IMAGE:
            cv2.imshow('window', processed_screen)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

        # save field as png
        if SAVE_IMAGES:
            file = 'Extract_fields/field_' + str(counter_y) + '_' + str(counter_x) + '.png'
            cv2.imwrite(file,processed_screen)

        # correlation with 1
        res_1 = cv2.matchTemplate(processed_screen,template_1,cv2.TM_CCOEFF)
        min_val, max_val_1, min_loc, max_loc = cv2.minMaxLoc(res_1)

        # correlation with 2
        res_2 = cv2.matchTemplate(processed_screen,template_2,cv2.TM_CCOEFF)
        min_val, max_val_2, min_loc, max_loc = cv2.minMaxLoc(res_2)

        # correlation with 3
        res_3 = cv2.matchTemplate(processed_screen,template_3,cv2.TM_CCOEFF)
        min_val, max_val_3, min_loc, max_loc = cv2.minMaxLoc(res_3) 

        # correlation with 4
        res_4 = cv2.matchTemplate(processed_screen,template_4,cv2.TM_CCOEFF)
        min_val, max_val_4, min_loc, max_loc = cv2.minMaxLoc(res_4)       

        # correlation with 5
        res_5 = cv2.matchTemplate(processed_screen,template_5,cv2.TM_CCOEFF)
        min_val, max_val_5, min_loc, max_loc = cv2.minMaxLoc(res_5) 

        correlation_res_1[counter_y][counter_x] = max_val_1
        correlation_res_2[counter_y][counter_x] = max_val_2
        correlation_res_3[counter_y][counter_x] = max_val_3
        correlation_res_4[counter_y][counter_x] = max_val_4
        correlation_res_5[counter_y][counter_x] = max_val_5
        

        # counter 0 ... 8 (x and y)
        counter_y = counter_y + 1
        if counter_y > 8:
            counter_y = 0
            counter_x = counter_x+1
            print('y: ' + str(counter_y) + ', x: ' + str(counter_x))
            if counter_x > 8:
                break

    for x in range(number_fields):
        for y in range(number_fields):
            if correlation_res_5[y][x] > 3000000:
                result[y][x] = 5

            if correlation_res_4[y][x] > 3000000:
                result[y][x] = 4

            if correlation_res_3[y][x] > 3000000:
                result[y][x] = 3

            if correlation_res_2[y][x] > 3000000:
                result[y][x] = 2

            if correlation_res_1[y][x] > 2000000:
                result[y][x] = 1

    # if a 9 is touching a 0 (which is not possible), lower the threshold of the recognition
    for x in range(number_fields):
        for y in range(number_fields):
            if result[y][x] == 0 and (count_surrounding(result, 0, x, y) > 0 or count_surrounding(result, 10, x, y) > 0):
                print('####### Error in detecting the map! ########')
                break
        else:
            continue
        break
            


    # when a shown number touches the same number of hidden fields, these fields are bombs
    # write the bombs into the result list as 10
    for y in range(number_fields):
        for x in range(number_fields):
            touching_covered_fields = get_touching_fields(result, 9, x, y)

            if len(touching_covered_fields) == result[y][x]:
                for element in touching_covered_fields:
                    mines[element[0]][element[1]] = 1

    for y in range(number_fields):
        for x in range(number_fields):
            if mines[y][x] == 1:
                result[y][x]=10


    # when shown number touches the same number of bombs, you can open all the other covered fields
    for y in range(number_fields):
        for x in range(number_fields):
            touching_bombs = count_surrounding(result, 10, x, y)

            if touching_bombs == result[y][x]:
                touch_this = get_touching_fields(result, 9, x, y)
                for element in touch_this:
                    click_field(element[1], element[0])


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
    for y in range(number_fields):
        for x in range(number_fields):
            if result[y][x]<9 and result[y][x]>0:
                not_found_bombs[y][x] = result[y][x] - count_surrounding(result, 10, x, y)
            else:
                not_found_bombs[y][x] = result[y][x]

    # find candidates for this solving algo (same number - bombs)
    for y in range(number_fields):
        for x in range(number_fields):
            if not_found_bombs[y][x]<9 and not_found_bombs[y][x]>0:
                found_candidates.append([y, x])
                found_candidates.append(get_touching_fields(not_found_bombs, not_found_bombs[y][x], x, y))

    # check if touching 9's of one field is a subset of the other touching 9's
    for i in range(0,len(found_candidates),2):  
        for element_cand in found_candidates[i+1]:
            part_1 = found_candidates[i]
            part_2 = element_cand

            touching_1 = get_touching_fields(result, 9, part_1[1], part_1[0])
            touching_2 = get_touching_fields(result, 9, part_2[1], part_2[0])

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
                        click_field(element_open[1], element_open[0])

    print_map(result)