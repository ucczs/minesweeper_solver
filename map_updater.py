import cv2
import map_generator
import numpy as np
import time

SAVE_FIELD = 0

def print_map(result):
    for i in range(len(result)):
        print(result[:][i]) 

def initialize_map(calc_center):
    x_fields=0
    y_fields=0

    for center in calc_center:
        if center[2] > x_fields:
            x_fields = center[2]
        if center[3] > y_fields:
            y_fields = center[3]

    initial_map = [[17 for x in range(x_fields)] for y in range(y_fields)] 

    return initial_map

# identify hidden field with the average color.
# when the average color ist noch bright, the field is hidden
# all_avg < 200 --> hidden field
# all_avg > 240 --> 0 bombs
def identify_type(field_img, counter=0):


    avg_color_per_row = np.average(field_img, axis=0)
    avg_color = np.average(avg_color_per_row, axis=0)
    all_avg = np.average(avg_color, axis=0)

    #field closed
    if abs(avg_color[0] - 114)<20 and abs(avg_color[1] - 197)<10 and abs(avg_color[2] - 250)<10:
        field_type = 9
    # avg is very white: zero bombs
    elif abs(avg_color[0] - 250)<10 and abs(avg_color[1] - 250)<10 and abs(avg_color[2] - 250)<10:
        field_type = 0      
    # avg is white gray or black
    elif abs(avg_color[0]-avg_color[1])<10 and abs(avg_color[1]-avg_color[2])<10 and abs(avg_color[0]-avg_color[2])<10:
        field_type = 0
    else:
        #filename = 'D:/GitHub/minesweeper_solver/Contours/felder_zu_' + str(int(all_avg)) + '_' + str(counter) + '.jpg'
        #cv2.imwrite(filename,field_img)           
        field_type = 12  

    return field_type


def identify_number_color(field_img,distance,counter):
    found_number = 0

    avg_color_pixel = []
    for row in field_img:
        for pixel in row:
            avg = sum(pixel) / len(pixel)
            # color white, gray or black
            if abs(avg - pixel[0]) < 6 and abs(avg - pixel[1]) < 6 and abs(avg - pixel[2]) <6:
                pass
            else:
                avg_color_pixel.append(pixel)

    avg_color_all = [0, 0, 0]
    for pixel in avg_color_pixel:
        avg_color_all[0] = avg_color_all[0] + pixel[0]
        avg_color_all[1] = avg_color_all[1] + pixel[1]
        avg_color_all[2] = avg_color_all[2] + pixel[2]                

    if len(avg_color_pixel) > 0:
        avg_color_all[:] = [x / len(avg_color_pixel) for x in avg_color_all]
    
        #print(avg_color_all)

        # 1: [<100 >200 >200]
        if avg_color_all[0] < 100 and avg_color_all[1] > 180 and avg_color_all[2] > 200:
            found_number = 1
        # 2: [<100 >200 <100]
        elif avg_color_all[0] < 150 and avg_color_all[1] > 150 and avg_color_all[2] < 100:
            found_number = 2
        # 3: [>200 <100 100<x<200]
        elif avg_color_all[0] > 200 and avg_color_all[1] < 100 and avg_color_all[2] < 200 and avg_color_all[2] > 100:
            found_number = 3    
        # 4: [<100 <100 >200]
        elif avg_color_all[0] < 100 and avg_color_all[1] < 130 and avg_color_all[2] > 195:
            found_number = 4
        # 5: [>200 <100 <100] (ähnlich zu 3)
        elif avg_color_all[0] > 180 and avg_color_all[1] < 100 and avg_color_all[2] < 100:
            found_number = 5
        else:
            found_number = 15
            #filename = 'D:/GitHub/minesweeper_solver/Contours/part_pic_' + str(found_number) + '_' + str(counter) + '.jpg'
            #cv2.imwrite(filename,field_img)
            #print(avg_color_all)
            #print(counter)
            #print(avg_color_all)
        
    #filename = 'D:/GitHub/minesweeper_solver/Contours/indetifyno_' + str(found_number) + '_' + str(counter) + '.jpg'
    #cv2.imwrite(filename,field_img)    

    return found_number
 



def update_map(calc_center, distance, identified_fields, result):
    counter = 0
    
    # pause because of animation of field opening
    time.sleep(0.5)
    screen = map_generator.get_screen()

    #updated_map = initialize_map(calc_center)
    updated_map = result

    for center in calc_center:
        top_corner_x = int(center[0]+0.25*distance)
        top_corner_y = int(center[1]+0.325*distance)
        bottom_corner_x = int(center[0]-0.25*distance)
        bottom_corner_y = int(center[1]-0.325*distance)

        part_screen = screen[bottom_corner_y:top_corner_y, bottom_corner_x:top_corner_x]

        x=center[2]-1
        y=center[3]-1 
        if not([y,x] in identified_fields):     
            updated_map[y][x] = identify_type(part_screen,counter)

        if updated_map[y][x] != 9 and updated_map[y][x] != 0:
            if [y,x] in identified_fields:
                continue
            else:
                counter = counter + 1
                updated_map[y][x] = identify_number_color(part_screen,distance,counter)
                #print('x=' + str(x) + ' ,y=' + str(y))
                if updated_map[y][x] != 15:
                    identified_fields.append([y,x])

        if SAVE_FIELD:
            counter = counter + 1
            filename = 'D:/GitHub/minesweeper_solver/DEBUG/part_pic_' + str(counter) + '.jpg'
            cv2.imwrite(filename,part_screen)

    #print_map(updated_map)

    return (updated_map, identified_fields)


if __name__ == "__main__":
    update_map()