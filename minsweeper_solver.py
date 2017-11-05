# optimierung (german):
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

# process image:
# convert colour space and define if the field is hidden or already opened
# process image with Canny operator
def process_img(original_img):
    processed_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)

    # calculate histogram and decide if field is still covered (9) or zero bombs
    hist = cv2.calcHist([processed_img], [2], None, [8],[0, 256])
    if hist[-1] < 10:
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
template_1 = cv2.imread('D:/Dropbox/Programmieren/Python/Minesweeper_Solver/Templates/1.png',0)
template_2 = cv2.imread('D:/Dropbox/Programmieren/Python/Minesweeper_Solver/Templates/2.png',0)
template_3 = cv2.imread('D:/Dropbox/Programmieren/Python/Minesweeper_Solver/Templates/3.png',0)
template_4 = cv2.imread('D:/Dropbox/Programmieren/Python/Minesweeper_Solver/Templates/4.png',0)
template_5 = cv2.imread('D:/Dropbox/Programmieren/Python/Minesweeper_Solver/Templates/5.png',0)

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
        screen = np.array(ImageGrab.grab(bbox=(227+counter_x*x_size,155+y_size*counter_y,285+counter_x*x_size,214+y_size*counter_y)))

        # all fields
        #screen = np.array(ImageGrab.grab(bbox=(227,157,733,665)))
        # links [0]  rechts [2]
        # oben [1]  unten [3]

        # process image and determine if field is still covered (9) or 0 bombs
        new_screen, field_cat = process_img(screen)

        result[counter_y][counter_x] = field_cat

        #print('Loop took {} seconds'.format(time.time()-last_time))
        print('y: ' + str(counter_y) + ', x: ' + str(counter_x))
        last_time = time.time()
        

        if SHOW_PROCESSED_IMAGE:
            cv2.imshow('window', new_screen)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

        # save field as png
        if SAVE_IMAGES:
            file = 'D:/Dropbox/Programmieren/Python/Minesweeper_Solver/Extract_fields/field_' + str(counter_y) + '_' + str(counter_x) + '.png'
            cv2.imwrite(file,new_screen)

        # correlation with 1
        res_1 = cv2.matchTemplate(new_screen,template_1,cv2.TM_CCOEFF)
        min_val, max_val_1, min_loc, max_loc = cv2.minMaxLoc(res_1)

        # correlation with 2
        res_2 = cv2.matchTemplate(new_screen,template_2,cv2.TM_CCOEFF)
        min_val, max_val_2, min_loc, max_loc = cv2.minMaxLoc(res_2)

        # correlation with 3
        res_3 = cv2.matchTemplate(new_screen,template_3,cv2.TM_CCOEFF)
        min_val, max_val_3, min_loc, max_loc = cv2.minMaxLoc(res_3) 

        # correlation with 4
        res_4 = cv2.matchTemplate(new_screen,template_4,cv2.TM_CCOEFF)
        min_val, max_val_4, min_loc, max_loc = cv2.minMaxLoc(res_4)       

        # correlation with 5
        res_5 = cv2.matchTemplate(new_screen,template_5,cv2.TM_CCOEFF)
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

            if correlation_res_1[y][x] > 2300000:
                result[y][x] = 1


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

    # Lösungsalgo 3
    # wenn zwei benachbarten und zahlen minus bomben gleich
    # wenn angrenzende felder der einen zahl teilmenge der angrenzenden felder der anderen
    # zahl
    # dann öffne felder die außerhalb der teilmenge liegen            

    # algo 3:
    # finde nachbarn, die gleiche (zahl-bomben) haben
    #   create list with number of not discovered bombs
    #   take this list to find candidates for this algo
    # for i in range(number_fields):
    #     for j in range(number_fields):

    # get coordinates of touching 9's
    # wenn kleinere anzahl von koordinaten von 9's komplett im anderen liste enthalten ist
    # öffne alle felder von größerer anzahl, die nicht enthalten ist

    for i in range(number_fields):
        print(result[:][i]) 
