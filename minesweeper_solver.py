# ideas:
# - track which fields are already pressed --> dont press them again
# - check pattern improve idea

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


# returns the complete screen
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
    for i in range(len(result)):
        print(result[:][i]) 


# clicks on a location on the screen (x/y)
def click(x,y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)    


# clicks on a specific field (x/y coordinates)
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
# y-pos/x-pos field of result
def count_surrounding(result, searching_for, x_pos, y_pos, x_fields, y_fields):
    touching_counter = len(get_touching_fields(result, searching_for, x_pos, y_pos, x_fields, y_fields))
    return touching_counter                    


# creates a list with x-pos/y-pos coordinates of touching fields with specific number
def get_touching_fields(result, searching_for, x_pos, y_pos, x_fields, y_fields):
    found_pos = []
    if y_pos>0 and x_pos>0:
        if result[y_pos-1][x_pos-1] == searching_for:
            found_pos.append([y_pos-1,x_pos-1])
    if x_pos>0:
        if result[y_pos][x_pos-1] == searching_for:
            found_pos.append([y_pos,x_pos-1])
    if y_pos<y_fields-1 and x_pos>0:
        if result[y_pos+1][x_pos-1] == searching_for:
            found_pos.append([y_pos+1,x_pos-1])
    if y_pos>0:
        if result[y_pos-1][x_pos] == searching_for:
            found_pos.append([y_pos-1,x_pos]) 
    if y_pos<y_fields-1:
        if result[y_pos+1][x_pos] == searching_for:
            found_pos.append([y_pos+1,x_pos])
    if y_pos>0 and x_pos<x_fields-1:
        if result[y_pos-1][x_pos+1] == searching_for:
            found_pos.append([y_pos-1,x_pos+1])
    if x_pos<x_fields-1:
        if result[y_pos][x_pos+1] == searching_for:
            found_pos.append([y_pos,x_pos+1])
    if x_pos<x_fields-1 and y_pos<y_fields-1:
        if result[y_pos+1][x_pos+1] == searching_for:
            found_pos.append([y_pos+1,x_pos+1])  

    return found_pos   


# returns coordinates of the fields which touches field x/y
def get_surrounding_coordinates(x,y,x_fields,y_fields):
    surrounding_coordinates = []
    for x_pos in range(x-1,x+2):
        for y_pos in range(y-1,y+2):
            if x_pos >= 0 and x_pos < x_fields and y_pos >= 0 and y_pos < y_fields and (x_pos != x or y_pos != y):
                surrounding_coordinates.append([y_pos,x_pos])                            
    return surrounding_coordinates


# return all fields which are in set1 and set2
def create_subset(set_1,set_2):
    subset = []
    for coordinates_1 in set_1:
        for coordinates_2 in set_2:
            if coordinates_1[0] == coordinates_2[0] and coordinates_1[1] == coordinates_2[1]:
                subset.append([coordinates_1[0],coordinates_1[1]])
    return subset


## Detect bombs 1 ##
# when a shown number touches the same number of hidden fields (9), these fields are bombs
# write the bombs into the result list as 10
def detect_bombs_easy(result,x_fields,y_fields):
    
    mines = [[0 for x in range(x_fields)] for y in range(y_fields)]

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

    return result


## Detect bombs 2 ##
# more complex algorithm to detect bombs
def detect_bombs_complex(result, x_fields, y_fields):
    
    # go through all fields
    for y in range(y_fields):
        for x in range(x_fields):
            surrounding_coordinates = get_surrounding_coordinates(x,y,x_fields,y_fields)
            # go through all neightbors and check if a field is save
            for neightbor_coord in surrounding_coordinates:  
                # make sure that no 15's are around, because this will mess up this algorithm
                surrounding_15 = count_surrounding(result,15,neightbor_coord[1],neightbor_coord[0],x_fields,y_fields)
                neightbor_surrounding_15 = count_surrounding(result,9,neightbor_coord[1],neightbor_coord[0],x_fields,y_fields)
                if not(surrounding_15 > 0 or neightbor_surrounding_15 > 0):
                    neighbour_fields_hidden = get_touching_fields(result,9,neightbor_coord[1],neightbor_coord[0],x_fields,y_fields)
                    fields_hidden = get_touching_fields(result,9,x,y,x_fields,y_fields)

                    subset = create_subset(fields_hidden,neighbour_fields_hidden)

                    neightbor_not_found_bombs = result[neightbor_coord[0]][neightbor_coord[1]] - count_surrounding(result, 10, neightbor_coord[1], neightbor_coord[0], x_fields, y_fields)
                    not_touched = create_not_in_subset(neighbour_fields_hidden,subset)
                    if fields_hidden == subset and (neightbor_not_found_bombs - result[y][x] == len(not_touched) and result[y][x]<9):
                        for bomb_found in not_touched:
                            result[bomb_found[0]][bomb_found[1]] = 10
                            
    return result

def check_pattern_criteria(result,x,y, x_fields, y_fields,direction):
    valid = 0
    
    if direction == 0:
        if result[y][x] == 1 and result[y-1][x] == 9 and result[y+1][x] == 9:
            valid = 0
        else:
            valid = 1
    elif direction == 1:
        if result[y][x] == 1 and result[y][x-1] == 9 and result[y][x+1] == 9:
            valid = 0
        else:
            valid = 1

    return valid        

## Detect bombs 3 ##
# detect bombs with some common patterns
def detect_bombs_with_patterns(result, x_fields, y_fields, not_found_bombs):
    
    # if result is 1 and both are 9 dont decide

    # pattern 1:
    # 1 2 1
    # B - B
    # print('not found bombs:')
    # print_map(not_found_bombs)

    pattern_1 = [1,2,1]
    found_pattern = check_pattern(not_found_bombs,pattern_1,x_fields,y_fields)
    for pat in found_pattern:
        try:
            # pattern in x direction
            if pat[2] == 0:
                if check_pattern_criteria(result,pat[1],pat[0], x_fields, y_fields,0) and check_pattern_criteria(result,pat[1]-2,pat[0], x_fields, y_fields,0):
                    if result[pat[0]-1][pat[1]] == 9 :
                        result[pat[0]-1][pat[1]] = 10
                        result[pat[0]-1][pat[1]-2] = 10
                        print('Bomb found: y=' + str(pat[0]-1) + ' x=' + str(pat[1]))   
                        print('Bomb found: y=' + str(pat[0]-1) + ' x=' + str(pat[1]-2))                       
                    elif result[pat[0]+1][pat[1]] == 9:
                        result[pat[0]+1][pat[1]] = 10
                        result[pat[0]+1][pat[1]-2] = 10   
                        print('Bomb found: y=' + str(pat[0]+1) + ' x=' + str(pat[1]))   
                        print('Bomb found: y=' + str(pat[0]+1) + ' x=' + str(pat[1]-2))                           
        except:
            pass         

        try:
            # pattern in y direction
            if pat[2] == 1:   
                if check_pattern_criteria(result,pat[1],pat[0], x_fields, y_fields,1) and check_pattern_criteria(result,pat[1],pat[0]-2, x_fields, y_fields,1):
                    if result[pat[0]][pat[1]-1] == 9:
                        result[pat[0]][pat[1]-1] = 10
                        result[pat[0]-2][pat[1]-1] = 10    
                        print('Bomb found: y=' + str(pat[0]-2) + ' x=' + str(pat[1]-1))   
                        print('Bomb found: y=' + str(pat[0]) + ' x=' + str(pat[1]-1))   
                    elif result[pat[0]][pat[1]+1] == 9:
                        result[pat[0]][pat[1]+1] = 10
                        result[pat[0]-2][pat[1]+1] = 10 
                        print('Bomb found: y=' + str(pat[0]) + ' x=' + str(pat[1]-1)+1)   
                        print('Bomb found: y=' + str(pat[0]-2) + ' x=' + str(pat[1]+1))                            
        except:
            pass                                   


    # 1 2 2 1
    # - B B -
    pattern_2 = [1,2,2,1]
    found_pattern = check_pattern(not_found_bombs,pattern_2,x_fields,y_fields)
    for pat in found_pattern:
        try:
        # pattern in x direction        
            if pat[2] == 0:
                if check_pattern_criteria(result,pat[1]-1,pat[0], x_fields, y_fields,0) and check_pattern_criteria(result,pat[1]-2,pat[0], x_fields, y_fields,0):                
                    if result[pat[0]-1][pat[1]-1] == 9:
                        result[pat[0]-1][pat[1]-1] = 10
                        result[pat[0]-1][pat[1]-2] = 10
                        print('Bomb found: y=' + str(pat[0]-1) + ' x=' + str(pat[1]-1))   
                        print('Bomb found: y=' + str(pat[0]-1) + ' x=' + str(pat[1]-2))                     
                    elif result[pat[0]+1][pat[1]-1] == 9:
                        result[pat[0]+1][pat[1]-1] = 10
                        result[pat[0]+1][pat[1]-2] = 10  
                        print('Bomb found: y=' + str(pat[0]+1) + ' x=' + str(pat[1]-1))   
                        print('Bomb found: y=' + str(pat[0]+1) + ' x=' + str(pat[1]-2))                             
        except:
            pass                                 

        try:
            # pattern in y direction
            if pat[2] == 1:      
                if check_pattern_criteria(result,pat[1],pat[0]-1, x_fields, y_fields,1) and check_pattern_criteria(result,pat[1],pat[0]-2, x_fields, y_fields,1):                  
                    if result[pat[0]-1][pat[1]-1] == 9:
                        result[pat[0]-1][pat[1]-1] = 10
                        result[pat[0]-2][pat[1]-1] = 10   
                        print('Bomb found: y=' + str(pat[0]-1) + ' x=' + str(pat[1]-1))   
                        print('Bomb found: y=' + str(pat[0]-2) + ' x=' + str(pat[1]-1))                            
                    elif result[pat[0]-1][pat[1]+1] == 9:
                        result[pat[0]-1][pat[1]+1] = 10
                        result[pat[0]-2][pat[1]+1] = 10     
                        print('Bomb found: y=' + str(pat[0]-1) + ' x=' + str(pat[1]+1))   
                        print('Bomb found: y=' + str(pat[0]-2) + ' x=' + str(pat[1]+1))                         
        except:
            pass                          

    # print('map after pattern analysis:')
    # print_map(result)

    return result

def check_pattern(result,pattern,x_fields,y_fields):
    found_pattern = []
    current_pos = 0

    length_pattern = len(pattern)

    for y in range(y_fields):
        current_pos = 0
        for x in range(x_fields):
            if result[y][x] == pattern[current_pos]:
                current_pos = current_pos + 1
                if current_pos == length_pattern:
                    found_pattern.append([y,x,0])
                    current_pos = 0
            else:
                current_pos = 0

    for x in range(x_fields):
        current_pos = 0
        for y in range(y_fields):
            if result[y][x] == pattern[current_pos]:
                current_pos = current_pos + 1
                if current_pos == length_pattern:
                    found_pattern.append([y,x,1])
                    current_pos = 0
            else:
                current_pos = 0                    

    return found_pattern


## Algorithm 1 ##
# when shown number touches the same number of bombs, you can open all the other covered fields
def open_obvious_fields(result,calc_center,x_fields,y_fields):
    click_counter = 0

    for y in range(y_fields):
        for x in range(x_fields):
            touching_bombs = count_surrounding(result, 10, x, y, x_fields, y_fields)

            if touching_bombs == result[y][x]:
                touch_this = get_touching_fields(result, 9, x, y, x_fields, y_fields)
                for element in touch_this:
                    click_field(element[1], element[0], calc_center)
                    click_counter = click_counter + 1

    return click_counter



## Algorithm 2 ##
# Explanation:
# - find neighbours which have the same number minus bombs
# - get coordinates of touching 9's
# - if coordinates of touching 9's from one field are a subset of the coordinates
#   of the touching 9's from the other field
# - all other touching fields can be opened
# example:
# 9 9 9 ..
# 1 1 2 ..
# 0 0 0 ..
# the upper right 9 is a field without a bomb
def open_fields_complex_1(result, calc_center, x_fields, y_fields,not_found_bombs):
    click_counter = 0
    # create list with number of not discovered bombs
    found_candidates = []

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
                        click_counter = click_counter + 1

    return click_counter


## Algorithm 3 ##
# NoX = shown number of field X
# BX = touching bombs of field X
# TX = touching 9's of field X
# SXY = intersection of touching 9's of field X and Y
#
# if No2 - B2 - (T2 - S12) > No1 - B1
# then open all fields which are (T1 - S12)
# Example:
# 0 0 0 0 ..
# 0 1 2 0 ..
# 9 9 9 9 ..
# lower left 9 is a field without a bomb
def open_fields_complex_2(result, calc_center, x_fields, y_fields,not_found_bombs):
    click_counter = 0

    # go through all fields
    for y in range(y_fields):
        for x in range(x_fields):
            surrounding_coordinates = get_surrounding_coordinates(x,y,x_fields,y_fields)
            # go through all neightbors and check if a field is save
            for neightbor_coord in surrounding_coordinates:
                # both fields must touch unknown bombs
                if not_found_bombs[y][x] > 0 and not_found_bombs[y][x] < 9 and not_found_bombs[neightbor_coord[0]][neightbor_coord[1]] > 0 and not_found_bombs[neightbor_coord[0]][neightbor_coord[1]] < 9:
                    
                    neighbour_fields_hidden = get_touching_fields(result,9,neightbor_coord[1],neightbor_coord[0],x_fields,y_fields)
                    fields_hidden = get_touching_fields(result,9,x,y,x_fields,y_fields)

                    subset_surrounding = create_subset(fields_hidden,neighbour_fields_hidden)

                    bombs_in_inter = not_found_bombs[y][x] - (len(fields_hidden) - len(subset_surrounding))

                    if bombs_in_inter >= not_found_bombs[neightbor_coord[0]][neightbor_coord[1]]:
                        save_fields = create_not_in_subset(neighbour_fields_hidden,subset_surrounding)
                        if not(save_fields is None):
                            for open_field in save_fields:
                                click_field(open_field[1],open_field[0],calc_center)
                                click_counter = click_counter + 1

    return click_counter


# returns a list which contains info about how many bombs are not found on each field
def create_not_found_bombs_list(result,x_fields,y_fields):
    not_found_bombs = [[0 for x in range(x_fields)] for y in range(y_fields)]
    
    for y in range(y_fields):
        for x in range(x_fields):
            if result[y][x]<9 and result[y][x]>0:
                not_found_bombs[y][x] = result[y][x] - count_surrounding(result, 10, x, y, x_fields, y_fields)
            else:
                not_found_bombs[y][x] = result[y][x]

    return not_found_bombs


# return all fields which are only in one of the sets
def create_not_in_subset(set_1,set_2):
    not_subset = []
    for coordinates_1 in set_1:
        if not(coordinates_1 in set_2):
            not_subset.append([coordinates_1[0],coordinates_1[1]])
    for coordinates_2 in set_2:
        if not(coordinates_2 in set_1):
            not_subset.append([coordinates_2[0],coordinates_2[1]])    
    return not_subset


# performs first move by clicking randomly once
def first_move(calc_center,x_fields,y_fields):
    x_start=random.randrange(x_fields)
    y_start=random.randrange(y_fields)
    click_field(x_start,y_start,calc_center) 

# for each hidden field the probability that a bomb is there is calculated
# the field with the lowest probability will be pressed
def perform_guess_click(result,calc_center,x_fields,y_fields,not_found_bombs):
    
    probability_map = [[-1 for x in range(x_fields)] for y in range(y_fields)]
    for y in range(y_fields):
        for x in range(x_fields):  
            if result[y][x] == 9:
                surrounding_coordinates = get_surrounding_coordinates(x,y,x_fields,y_fields)
                for coordinates in surrounding_coordinates:
                    probability = -1
                    touching_fields = count_surrounding(result, 9, coordinates[1], coordinates[0], x_fields, y_fields)
                    if result[coordinates[0]][coordinates[1]] > 0 and result[coordinates[0]][coordinates[1]] < 9 and touching_fields>0:
                        probability = not_found_bombs[coordinates[0]][coordinates[1]] / touching_fields

                    if probability > probability_map[y][x] and probability>0:
                        probability_map[y][x] = probability

    for y in range(y_fields):
        for x in range(x_fields):   
            if probability_map[y][x] == -1:
                probability_map[y][x] = 1                      

    (min_y, min_x) = find_coordinates_of_minimum(probability_map, x_fields, y_fields)

    if probability_map[min_y][min_x] < 1 and probability_map[min_y][min_x]>0:
        click_field(min_x,min_y,calc_center)
        print('Guess click: x=' + str(min_x) + ',y=' + str(min_y) + ' risk of bomb=' + '%.2f' % probability_map[min_y][min_x])

      
                
def find_coordinates_of_minimum(list, x_fields, y_fields):
    minimum = 10000000
    for y in range(y_fields):
        for x in range(x_fields):  
            if list[y][x] < minimum:
                minimum = list[y][x]
                min_x = x
                min_y = y

    return(min_y, min_x)
                

def main():
    [calc_center, distance, y_fields, x_fields] = map_generator.get_centers()

    result = [[9 for x in range(x_fields)] for y in range(y_fields)]
    identified_fields = []
    counter_9 = 0
    no_click = 0   

    first_move(calc_center,x_fields,y_fields)

    last_time = time.time()

    solving_in_progress = True
    
    last_curpos = win32api.GetCursorPos()        
    
    # Time for open large field
    time.sleep(0.1)

    
    while(True):               

        (result, identified_fields) = map_updater.update_map(calc_center, distance,identified_fields, result)

        ####### Detecting/Solving algorithms start here ######

        ## Detect bombs ##

        result = detect_bombs_easy(result, x_fields, y_fields)
        result = detect_bombs_complex(result, x_fields, y_fields)

        # just use this method if one run was without click
        if no_click > 0:
            not_found_bombs = create_not_found_bombs_list(result, x_fields, y_fields)
            result = detect_bombs_with_patterns(result, x_fields, y_fields,not_found_bombs)

        ## Open fields without bombs
        not_found_bombs = create_not_found_bombs_list(result, x_fields, y_fields)

        curpos = win32api.GetCursorPos() 
        if last_curpos != curpos:
            print('Mouse moved')
            break

        clicks_1 = open_obvious_fields(result, calc_center, x_fields, y_fields)
        clicks_2 = open_fields_complex_1(result, calc_center, x_fields, y_fields,not_found_bombs)
        clicks_3 = open_fields_complex_2(result, calc_center, x_fields, y_fields,not_found_bombs)

        # if no clicks two times in a row are performed guess a field
        if clicks_1+clicks_2+clicks_3 == 0:
            if no_click > 1:
                perform_guess_click(result,calc_center,x_fields,y_fields,not_found_bombs)
                no_click = 0
            else:
                no_click = no_click + 1
        else:
            no_click = 0

        last_curpos = win32api.GetCursorPos() 

        #print_map(result)

        counter_9 = 0
        for y in range(y_fields):
            for x in range(x_fields):        
                if result[y][x] == 9:
                    counter_9 = counter_9 + 1
        
        if counter_9 == 0:
            print('No open fields! Win!!')
            break

        print('Loop took {} seconds'.format(time.time()-last_time))
        last_time = time.time()


if __name__ == "__main__":
    main()        