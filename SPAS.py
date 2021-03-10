import cv2
import numpy as np
from Queue import *
from math import *
import time
 
###### CONST ######
width = 480
height = 320
 
cam = cv2.VideoCapture(0)
cam.set(3,width)
cam.set(4,height)
vertices = np.array([[(0, 310), (480, 310), (460, 80),
                      (50, 80)]])
 
global bound_Value
bound_Value = 40#############Changable 40~80
q_Num = 0
q_Represent = []
q_Maxsize = 10
q_list = []
'''for i in range(0,q_Maxsize):
    q_Represent.append((0,0))'''
new_Queue = 0


'''_tick2_frame = 0
_tick2_fps = 20000000
_tick2_t0 = time.time()'''

start = time.time()

 
###### FUNCT ######
def make_ROI(img, region, color3 = (255, 255, 255), color1 = 255):
    mask = np.zeros_like(img)
 
    if len(img.shape) > 2:
        color = color3
    else:
        color = color1
    cv2.fillPoly(mask, region, color)
 
    return cv2.bitwise_and(img, mask)

def distance(point1, point2):
    global bound_Value
    x_2 = pow(((int)(point1[0]) - (int)(point2[0])),2)
    y_2 = pow(((int)(point1[1]) - (int)(point2[1])),2)
    result = sqrt(x_2 + y_2)
    if bound_Value > result: ## determine as same point
        return True
    else:
        return False

'''def tick(fps = 60):
    global _tick2_frame, _tick2_fps, _tick2_t0
    n = _tick2_fps/fps
    _tick2_frame += n
    while n > 0:
        n -= 1
    if time.time() - _tick2_t0 > 1:
        _tick2_t0 = time.time()
        _tick2_fps = _tick2_frame
        _tick2_frame = 0'''
 
###### RUN ######
 
 
while True:
    
    ret, frame = cam.read()
    frame2 = np.copy(frame)
    roi = make_ROI(frame2, vertices)
    
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray = np.float32(gray)
 
    '''max1_x = 1000
    max1_y = 1000
    max2_x = 1000
    max2_y = 1000
    corners = cv2.goodFeaturesToTrack(gray, 5, 0.1, 20)
    try:
        corners = np.int0(corners)
        for corner in corners:
            x, y = corner.ravel()
            cv2.circle(gray, (x,y), 3, 255, -1)
            if max1_x > x and max2_x < x:
                if max1_x < max2_x:
                    max2_y = y
                    max2_x = x
                else:
                    max1_y = y
                    max1_x = x
            elif max1_x > x:
                max1_y = y
                max1_x = x
            elif max2_x < x:
                max2_y = y
                max2_x = x
    except TypeError: pass'''
 
    dst = cv2.cornerHarris(gray, 2, 3, 0.1)#############Changable_second value 2~5
    
    dst = cv2.dilate(dst, None)
    frame[dst > 0.01 * dst.max()] = [0, 0, 225]
    roi[dst > 0.01 * dst.max()] = [0, 0, 225]
    #accumulate data
    matrix = np.where(dst > 0.01 * dst.max())
    matrix_Index = 0
    next_Queue = True
    now_Queue = 0
    repre_Check = 0
    new_Queue = 0
    q_list = []
    q_Represent = []
    '''for i in range(0,q_Maxsize):
        q_Represent.append((0,0))'''
    ###### ALGORITHM ######
    if np.size(matrix[0]) > 100:
        while(matrix_Index < np.size(matrix[0])):##new_Queue + 1 != q_Maxsize and 
            repre_Check = 0
            for i in range(0,new_Queue):
                if distance(q_Represent[i],[matrix[1][matrix_Index],matrix[0][matrix_Index]]):
                    if q_list[i].full():
                        q_list[i].get()
                        q_list[i].put([matrix[1][matrix_Index],matrix[0][matrix_Index]])
                        q_Represent[i] = [matrix[1][matrix_Index],matrix[0][matrix_Index]]
                        break
                    else:
                        q_list[i].put([matrix[1][matrix_Index],matrix[0][matrix_Index]])
                        q_Represent[i] = [matrix[1][matrix_Index],matrix[0][matrix_Index]]
                        break
                else:##not same point
                    if new_Queue > 11:
                        break
                    elif i+1 == new_Queue:
                        next_Queue = True
                        break
            if new_Queue > 11:
                break
            if next_Queue:
                q_list.append(Queue(q_Maxsize))
                #print "!",new_Queue,len(q_list)
                q_list[new_Queue].put([matrix[1][matrix_Index],matrix[0][matrix_Index]])
                q_Represent.append([matrix[1][matrix_Index],matrix[0][matrix_Index]])
                new_Queue += 1
                next_Queue = False
            matrix_Index += 1
        result_Arr = sorted(q_Represent, key = lambda x:x[0],reverse = True)
        for i in range(0,len(result_Arr)):
            if len(result_Arr) <= i:
                break
            if result_Arr[i][1] > 300:
                #print "pop",i,len(result_Arr)
                result_Arr.pop(i)
        '''max_Repre = 0
        max_Index = 0
        for i in range(0,new_Queue):
            if max_Repre < q_Represent[i][1]:
                max_Repre = q_Represent[i][1]
                max_Index = i'''
        length = len(result_Arr)
        critic = 0#int(length/3)
        Corner_Result = ((result_Arr[critic][0] + result_Arr[critic+1][0])/2, (result_Arr[critic][1] + result_Arr[critic+1][1])/2)

        ####remove for fps
        cv2.circle(roi,(result_Arr[critic][0],result_Arr[critic][1]), 5, (0,0,256),5)
        cv2.circle(roi,(result_Arr[critic+1][0],result_Arr[critic+1][1]), 5, (0,0,256),5)
    #print "ACT", Corner_Result
    ###### SHOW ######
    
    cv2.circle(roi,(Corner_Result[0],Corner_Result[1]), 5, (256,0,0),5)
    for i in range(0,length):
        cv2.circle(roi,(result_Arr[i][0],result_Arr[i][1]), 3, (0,256,0),5)
    
    cv2.imshow('dst', frame)
    cv2.imshow('eeee',roi)


    #####fps####
    end = time.time()
    print 1/(end - start)
    start = time.time()
    if cv2.waitKey(1) & 0xff == 27:
        print "END"
        break
    
cam.release()
cv2.destroyAllWindows()
