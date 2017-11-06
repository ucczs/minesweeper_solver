import numpy as np
from PIL import ImageGrab
import cv2
from shape_detector import ShapeDetector

SAVE_IMAGES = 1

def get_screen(x1=0,y1=0,x2=0,y2=0):
    if x2>0 and y2>0:
        screen = np.array(ImageGrab.grab(bbox=(x1,y1,x2,y2)))
    else:
        screen = np.array(ImageGrab.grab())

    return screen

def calc_contours(orig_image):
    processed_img = cv2.cvtColor(orig_image, cv2.COLOR_BGR2GRAY)

    processed_img = cv2.Canny(processed_img, threshold1=50, threshold2=500)

    im2, contours, hierarchy = cv2.findContours(processed_img.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    return contours

def calc_center_points(num_x, num_y, distance, start_x, start_y, end_x, end_y):
    calc_center = []

    big_half_x = int(round(num_x/2+0.49))
    small_half_x = int(num_x/2)

    for y_count in range(num_y):
        for x_count in range(small_half_x):
            x = int(start_x - distance * x_count)
            y = int(start_y - distance * y_count)
            calc_center.append([x,y])

    for y_count in range(num_y):
        for x_count in range(big_half_x):
            x = int(end_x + distance * x_count)
            y = int(end_y + distance * y_count)
            calc_center.append([x,y])
        
    return calc_center

def draw_center_points(center_points, img, distance):
    for center in center_points:
        #cv2.circle(img,(center[0],center[1]), 4, (255,255,0), -1)
        top_corner_x = int(center[0]+0.25*distance)
        top_corner_y = int(center[1]+0.325*distance)
        bottom_corner_x = int(center[0]-0.25*distance)
        bottom_corner_y = int(center[1]-0.325*distance)

        cv2.rectangle(img,(top_corner_x,top_corner_y),(bottom_corner_x,bottom_corner_y),(255,255,0), -1)

    filename = 'D:/GitHub/minesweeper_solver/center_points.jpg'
    cv2.imwrite(filename,img)

def get_center_point_list_image(contours):
    sd = ShapeDetector()

    preCX = 0
    preCY = 0

    area_list = []
    center_list = []

    for c in contours:
        shape = sd.detect(c)
        if shape == 'square':
            M = cv2.moments(c)

            area = cv2.contourArea(c)

            if M["m00"] > 0:
                cX = int(M["m10"]/M["m00"])
                cY = int(M["m01"]/M["m00"])

                diffX = preCX - cX
                diffY = preCY - cY

                if diffX > 0 or diffY > 0:
                    if area>10:
                        area_list.append(area)
                        center_list.append([cX, cY])

                        #print('cX=' + str(cX) + ', cY=' + str(cY))
                        #print('diffcX=' + str(diffX) + ', diffcY=' + str(diffY))

                preCX = cX
                preCY = cY
                
    histo = np.histogram(area_list,bins=7)

    max_value_histogram = max(histo[0])
    idx = [i for i, j in enumerate(histo[0]) if j == max_value_histogram]

    min_border = histo[1][idx[0]]

    try:
        max_border = histo[1][idx[0]+2]
    except:
        max_border = 100000000

    cpoint_list = []
    for idx, area in enumerate(area_list):
        if area < max_border and area > min_border:
            cpoint_list.append(center_list[idx])

    return cpoint_list

def calc_grid_characteristics(cpoint_list):
    max_yval=0
    max_xval=0

    min_yval=9999999
    min_xval=9999999

    for cpoint in cpoint_list:
        if cpoint[0] > max_xval:
            max_xval = cpoint[0]
        if cpoint[1] > max_yval:
            max_yval = cpoint[1]    
        if cpoint[0] < min_xval:
            min_xval = cpoint[0]
        if cpoint[1] < min_yval:
            min_yval = cpoint[1]      

    pre_valx = 0
    pre_valy = 0
    diffY_list = []

    for cpoint in cpoint_list:
        diffY_list.append(pre_valy-cpoint[0])
        pre_valy=cpoint[0]

    histo = np.histogram(diffY_list,bins=1000000)

    max_value_histogram = max(histo[0])
    idx = [i for i, j in enumerate(histo[0]) if j == max_value_histogram]

    diff = histo[1][idx[0]+1]

    y_fields=int(round((max_yval-min_yval)/diff))+1
    x_fields=int(round((max_xval-min_xval)/diff))+1

    return (x_fields, y_fields, diff, max_xval, max_yval, min_xval, min_yval)

def get_centers():
    original_img = get_screen()

    contours = calc_contours(original_img)

    cpoint_list = get_center_point_list_image(contours)

    [x_fields, y_fields, diff, max_xval, max_yval, min_xval, min_yval] = calc_grid_characteristics(cpoint_list)

    calc_center = calc_center_points(x_fields, y_fields, diff, max_xval, max_yval, min_xval, min_yval)

    if SAVE_IMAGES:
        draw_center_points(calc_center,original_img,diff)

    return (calc_center, diff)

if __name__ == "__main__":
    get_centers()