#! python3

from collections import deque
from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2
import numpy as np
import threading
import queue
import matplotlib
import itertools
from matplotlib import pyplot as plt
from matplotlib import animation as animation
import multiprocessing


'''
Step #1: Detect the presence of a colored ball using computer vision techniques.
Step #2: Track the ball as it moves around in the video frames, drawing its previous positions as it moves.
'''

def main():

    matplotlib.use('TkAgg')

    def nothing(x):
        pass

    cv2.namedWindow("Tracking")
    cv2.createTrackbar("LH", "Tracking", 0, 255, nothing) # Lower Hue
    cv2.createTrackbar("LS", "Tracking", 49, 255, nothing) # Lower Saturation
    cv2.createTrackbar("LV", "Tracking", 42, 255, nothing) # Lower Value
    cv2.createTrackbar("UH", "Tracking", 63, 255, nothing) # Upper Hue
    cv2.createTrackbar("US", "Tracking", 107, 255, nothing) # Upper Saturation    
    cv2.createTrackbar("UV", "Tracking", 150, 255, nothing) # Upper Value


    '''

    Array Color Data:

    #1 - 0,16,26(L) 49,114,127(U)
    #2 - 2,46,60(L) 72,91,99(U)
    #3 - 0,46,86(L) 72,186,125(U) # not good
    #4 - 0,46,21(L) 21,106,111(U) # pretty good
    #5 - 0,70,19(L) 21,106,111(U) # seems perfect
    #6 - 0,70,19(L) 21,107,215(U) # good
    #7 - 0,55,72(L) 56,111,212(u) # perfect for implementation {found}

    '''
    # l_b = np.array([0, 16, 26])
    # u_b = np.array([40, 114, 110])

    vs = cv2.VideoCapture('video\\spring-system.mp4')

    x = 122
    y = 445

    # Dimensions 77 x 72
    width = 60
    height = 180

    term_criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)

    # Output
    # fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    # out = cv2.VideoWriter('detection-spring-final.avi', fourcc, 29.970662, (406, 720), True)

    xs_equilibrium_queue = queue.Queue()
    ys_equilibrium_queue = queue.Queue()

    amplitude_y_queue = queue.Queue()


    res = []

    amplitude = 0

    event = threading.Event()

    class ThreadingEquilibrium(threading.Thread):

        def __init__(self, xs_equilibrium_queue, ys_equilibrium_queue, res):
            super().__init__()
            self.res = []
            self.xs_equilibrium_queue = xs_equilibrium_queue
            self.ys_equilibrium_queue = ys_equilibrium_queue

        def run(self):
            xs = []
            ys = []
            while True:
                xpos = self.xs_equilibrium_queue.get()
                xs.append(xpos)
                ypos = self.ys_equilibrium_queue.get()
                ys.append(ypos)
                # print("XS LIST>", xs, "YS LIST>", ys)
                min_x = min(xs)
                max_x = max(xs)
                min_y = min(ys)
                max_y = max(ys)
                final_pos_x = (min_x + max_x) / 2
                final_pos_y = (min_y + max_y) / 2
                res.clear()
                res.append(final_pos_x)
                res.append(final_pos_y)


    second_ys_queue = queue.Queue()
    second_xs_queue = queue.Queue()

    class ComputeCoordinates(threading.Thread):

        def __init__(self, second_ys_queue, second_xs_queue):
            super().__init__()
            self.second_ys_queue = second_ys_queue
            self.second_xs_queue = second_xs_queue # X position [Optional]
            self.ys = []
            self.xs = [] # X position [Optional]

        def run(self):
            job_1_x = multiprocessing.SimpleQueue()
            job_1_y = multiprocessing.SimpleQueue()
            job_1 = multiprocessing.Process(None, doplot,args=(job_1_y, job_1_x))
            job_1.start()
            frame = 0
            
            while True:
                frame += 1
                ypos = self.second_ys_queue.get()
                xpos = self.second_xs_queue.get()
                self.ys.append(ypos)
                job_1_x.put(frame)
                job_1_y.put(ypos)
                self.xs.append(xpos)
    


    eqThread = ThreadingEquilibrium(xs_equilibrium_queue, ys_equilibrium_queue, res)
    eqThread.setDaemon(True)
    eqThread.start()

    computeCoordinates = ComputeCoordinates(second_ys_queue, second_xs_queue)
    computeCoordinates.setDaemon(True)
    computeCoordinates.start()



    

    
    



    # amp = queue.Queue()

    # def get_amplitude(ys_list):
    #     if len(ys_list) == 0:
    #         pass
    #     else:
    #         min_y = min(ys_list) # 313
    #         equilibrium = amplitude_y_queue.get() # 415
    #         distancePixels = equilibrium - min_y
    #         amplitude = distancePixels * 2.54/72
    #         return amplitude
        
    # lock = threading.Lock()

    # time_elapsed = 0
    # op = 0
    # sw1 = True

    ''' [TODO]'''
    # def get_timePeriod(objPos, ys_list):
    #     global time_elapsed
    #     global op
    #     global lock
    #     global sw1
    #     global frameOP
    #     # end_timing = time.perf_counter()
    #     # print(end_timing)
    #     print("POSOTIO", objPos)
    #     if objPos == max(ys_list):
    #         op += 1
    #     elif objPos == min(ys_list):
    #         op += 1
        
    #     # print("~~~~~~~~~~~~~~~~~~~", op)

    #     if op >= 3:
    #         time_elapsed = frameOP - 216
    #         sw1 = False

    frameOP = 0 # Starting point
    # plt.show()


        # job_1.join()

    # [TODO] Start looping
    while True:
        
        _, frame = vs.read()

        if frame is None:
            break

        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        l_h = cv2.getTrackbarPos("LH", "Tracking")
        l_s = cv2.getTrackbarPos("LS", "Tracking")
        l_v = cv2.getTrackbarPos("LV", "Tracking")

        u_h = cv2.getTrackbarPos("UH", "Tracking")
        u_s = cv2.getTrackbarPos("US", "Tracking")
        u_v = cv2.getTrackbarPos("UV", "Tracking")

        
        l_b = np.array([l_h, l_s, l_v])
        u_b = np.array([u_h, u_s, u_v])

        mask = cv2.inRange(hsv, l_b, u_b)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        _, track_window = cv2.meanShift(mask, (x, y, width, height), term_criteria)
        x, y, w, h = track_window

        padding = 30
        padding_bottom = 35

        top_left_coordinates = (x, (y - padding))

        cv2.rectangle(frame, (top_left_coordinates), (x + w, y + h - padding_bottom), (0, 255, 0), 2)


        x_pos, y_pos = top_left_coordinates



        # print("Coordinates:", "X:", x_pos, "Y:", y_pos)

        xs_equilibrium_queue.put(x_pos)
        ys_equilibrium_queue.put(y_pos)

        second_ys_queue.put(y_pos)
        second_xs_queue.put(x_pos)
        
        '''print(coord)'''

        f = tuple(res)

        if len(f) == 0:
            pass
        else:
            e_x, e_y = f
            amplitude_y_queue.put(e_y)
            # print("Equilibrium>>", e_y)
            cv2.circle(frame, (int(e_x), int(e_y)), 6,  (255, 255, 0), -1)

        # get_amp_Thread = threading.Thread(target=lambda q, arg1: q.put(get_amplitude(arg1)), args=(amp, ys))
        # get_amp_Thread.setDaemon(True)
        # get_amp_Thread.start()

        # if amp.qsize() == 0:
        #     pass
        # else:
        #     amplitude = amp.get() # centimeters [cm]
        #     # print("AMP [*]>", amplitude, "cm")
            

        # print("AMP [2]", amplitude, "[cm]")
        # Another value 8.59 for time!
        # start_time = time.perf_counter()
        # print(start_time)
        # if frameOP >= 214:
        #     if sw1:
        #         # d = str(start_time)
        #         # first_timing = d[::]
        #         # first_timing = float(first_timing)
        #         # # print(first_timing)
        #         periodThread = threading.Thread(target=get_timePeriod, args=(y_pos, ys))
        #         periodThread.setDaemon(True)
        #         periodThread.start()
                
        # print(start_time) # [TODO] ~3.4 Starting point

        # print("[+] PERIOD", time_elapsed)
        
        '''
        30 FRAMES PER SEC => 1 sec
        '''

        cv2.imshow("Frame", frame)
        # frameOP += 1
        # print("OP", frameOP)
        # cv2.imshow("Mask", mask)
        # out.write(frame)
        
        key = cv2.waitKey(60) & 0xFF

        if key == ord('q'):
            break

    vs.release()
    # out.release()
    cv2.destroyAllWindows()




def doplot(job_1_y, job_1_x):
    # time = job_1_x.get()
    

    # x = np.linspace(0, 30, 100)
    # y = np.linspace(0, 30, 100)
    # t = 0     
    xs = []
    ys = []
    qx = multiprocessing.Queue()
    qy = multiprocessing.Queue()
    job_2 = multiprocessing.Process(None, gr,args=(qx, qy))
    job_2.start()
    while True:
        
        coordY = job_1_y.get()
        coordX = job_1_x.get()
        # print(coordY)
        # ys.append(coordY)
        # # ys = np.array(ys)

        xs.append(coordX)
        ys.append(coordY)

        qx.put(coordX)
        qy.put(coordY)

        # print(ys)

        


def gr(graphQ_X, graphQ_Y):
    xs = []
    ys = []
    fig = plt.figure(1)
    # ax = fig.add_subplot(1, 1, 1)
    ax = plt.axes(xlim=(0, 30), ylim=(10, 19))
    displacement, = ax.plot([], [], 'r-', label="[Weg Graph] | Displacement")
    ''' a = -w^2*x
    for acceleration we need position and time
    '''
    figAcc = plt.figure(2)
    ax2 = plt.axes(xlim=(0, 30), ylim=(-260, 260))
    acceleration, = ax2.plot([], [], 'b-', label="[Beschleunigung] | Acceleration")

    figVelo = plt.figure(3)
    ax3 = plt.axes(xlim=(0, 30), ylim=(-35, 35))
    velocity, = ax3.plot([], [], 'y-', label="[Geschwindigkeit] | Velocity")


    # ax.spines['left'].set_position(('data', 0.0))
    # ax.spines['bottom'].set_position(('data', 0.0))
    # ax.spines['right'].set_color('none')
    # ax.spines['top'].set_color('none')
    ays = []
    t = 0.722
    f = 1/t
    w = 2*np.pi*f
    # w_def = 8.6664
    amplitude = 3.32 # [TODO] Determine this value by passing file.txt with later amplitude (px)
    # time = np.linspace(0, 100, 300)
    forA = queue.Queue()
    def animate(i):

        x = graphQ_X.get()
        y = graphQ_Y.get()

        y = y * 2.54 / 72   # Centimeters
        x = x/30            # Time [sec]

        forA.put(x)

        xs.append(x)
        ys.append(y)

        # dis = amplitude * np.sin(w*x)
        # displacementProof.append(dis)
        
        # -amplitude * w**2 * np.sin(x*w)
        # a = -w**2 * y
        # print(a)
        # ays.append(a)


        # print(np.array(ays))
        # print(np.array(xs))
        displacement.set_data(np.array(xs), np.array(ys))
        # acceleration.set_data(np.array(xs), np.array(ays))
        return displacement,
        # ax.clear()
    
    x_lAcc = []
    y_lAcc = []
    veloQe = queue.Queue()
    def accG(i):

        xAcc = forA.get()

        veloQe.put(xAcc)

        x_lAcc.append(xAcc)

        a = -amplitude * w**2 * np.sin(xAcc*w)

        y_lAcc.append(a)

        acceleration.set_data(np.array(x_lAcc), np.array(y_lAcc))

        return acceleration,

    x_lVelo = []
    y_lVelo = []
    def veloAni(i):

        v_X = veloQe.get()

        x_lVelo.append(v_X)

        v = w*amplitude*np.cos(w*v_X)

        y_lVelo.append(v)

        velocity.set_data(np.array(x_lVelo), np.array(y_lVelo))

        return velocity,



    line_ani = animation.FuncAnimation(fig, animate, 5000, interval=50, blit=True, repeat=False)
    accAnim = animation.FuncAnimation(figAcc, accG, 5000, interval=50, blit=True, repeat=False)
    veloAni = animation.FuncAnimation(figVelo, veloAni, 5000, interval=50, blit=True, repeat=False)

    plt.figure(1)
    plt.gca().invert_yaxis()
    plt.title("[Weg Graph] | Displacement")
    plt.xlabel("t/s")
    plt.ylabel("x/m")
    plt.grid()

    plt.figure(2)
    plt.title("[Beschleunigung] | Acceleration")
    plt.xlabel("t/s")
    plt.ylabel("a/m^-2")
    plt.grid()

    plt.figure(3)
    plt.title("[Geschwindigkeit] | Velocity")
    plt.xlabel("t/s")
    plt.ylabel("v/m-1")
    plt.grid()
    


    
    plt.show()

# def accGraph(frame):
#     xs = []
#     ys = []
#     fig = plt.figure()
#     # ax = fig.add_subplot(1, 1, 1)
#     ax = plt.axes(xlim=(0, 30), ylim=(10, 20))
#     displacement, = ax.plot([], [], 'r-', label="Displacement")
#     ''' a = -w^2*x
#     for acceleration we need position and time
#     '''
#     acceleration, = ax.plot([], [], 'b-', label="Acceleration")
#     ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), shadow=True, ncol=3)

#     ays = []
#     t = 0.722
#     f = 1/t
#     w = 2*np.pi*f
#     amplitude = 3.32 # [TODO] Determine this value by passing file.txt with later amplitude (px)
#     # w_def = 8.6664



if __name__ == '__main__':
    main()