import cv2
import numpy as np
import os
import datetime as dt


# Instructions:
# 1. Set paths to folders where backgrounds, videos and recordings will be stored.
# 2. Move your images and videos to previously mentioned folders, they cannot be empty.
# 3. Set window resolution to the same size as resolution of videos (background images are automatically resized).
# 4. Stop recording before you quit.
# 5. You can change change the threshold value, video speed and invert masks by using bars at top of the window. (Changing speed does not affect on video you are recording).
# 6. Set capture mode (cap_mode) to value 0 (video capture) or 1 (camera capture).
#
#  ___________________________________________________
# |                      Keys:                        |
# |                                                   |
# | q - Quit                                          |
# | w - Next video                                    |
# | s - Previous video                                |
# | d - Next background                               |
# | a - Previous background                           |
# | o - Change mask processing (Contours/Greenscreen) |
# | r - Start recording                               |
# | e - Stop recording                                |
# | t - Change capture mode (Video/Camera)            |
# |___________________________________________________|
#
#######################################
width = 1280 
height = 720 

path_to_backgrounds="test/backgrounds/"
path_to_videos="test/videos/"
path_to_recordings="test/recordings/"

cap_mode = 0
#######################################









def nothing(x):
    pass

def get_image_resolution(image):
    image_height,image_width,channels = image.shape
    resolution = [int(image_height),int(image_width)] 
    return resolution

def get_video_resolution(video):
    resolution = [video.get(cv2.CAP_PROP_FRAME_HEIGHT),video.get(cv2.CAP_PROP_FRAME_WIDTH)]
    return resolution

cap = cv2.VideoCapture(0)

no_camera = False
on_record = False

if not cap.isOpened():
    print("No access to the camera.")
    no_camera = True
else:
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

path_to_record = path_to_recordings + str(dt.datetime.now().strftime("%d_%m_%Y-%H_%M_%S")+".mp4")

files=os.listdir(path_to_backgrounds)
videos=os.listdir(path_to_videos)

backgrounds=[]
video_paths=[]
resolutions=[]

for file in files:
    if file.endswith(".jpg") or file.endswith(".png"):
        file_path=os.path.join(path_to_backgrounds,file)
        image = cv2.imread(file_path)
        image = cv2.resize(image,(width,height))
        backgrounds.append(image)
        resolutions.append(get_image_resolution(image))

for video in videos:
    if video.endswith(".mp4"):
        video_path=os.path.join(path_to_videos,video)
        video_paths.append(video_path)

if len(video_paths) != 0:
    no_videos = False
else:
    no_videos = True

backgrounds_cursor = 0
videos_cursor = 0

process_mode = 0

fourcc = cv2.VideoWriter_fourcc(*'mp4v')

backgrounds_max_index = len(backgrounds) - 1
videos_max_index = len(video_paths) - 1

lower_green = np.array([35, 100, 100])
upper_green = np.array([90, 255, 255])

if not no_videos:
    video = cv2.VideoCapture(video_paths[videos_cursor])
    frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = video.get(cv2.CAP_PROP_FPS)/2

masks = [0,0]

cv2.namedWindow('Capture')

cv2.createTrackbar('Min','Capture',60,300,nothing)
cv2.createTrackbar('Max','Capture',120,300,nothing)

cv2.createTrackbar('Speed','Capture',60,500,nothing)
cv2.setTrackbarMin('Speed','Capture', 1)

cv2.createTrackbar('Mask inv','Capture',0,1,nothing)

while True:
    if cap_mode == 1:
        if no_camera:
            exit()
        ret, frame = cap.read()
        if not ret:
            print('Camera capture failed.')
            exit()
    else:
        if not no_videos:
            ret, frame = video.read()
            if not ret:
                video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            if get_video_resolution(video) == resolutions[0]:
                nothing
            else:
                print("Invalid video resolution")
                video.release()
                exit()
        else:
            print("No videos detected")
            exit()

    path_to_record="test/recordings/"+str(dt.datetime.now().strftime("%d_%m_%Y-%H_%M_%S")+".mp4")

    speed = cv2.getTrackbarPos('Speed','Capture')
    
    if process_mode == 0:
        if len(backgrounds) != 0:
            nothing
        else:
            print("No backgrounds detected")
            exit()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        min = cv2.getTrackbarPos('Min','Capture')
        max = cv2.getTrackbarPos('Max','Capture')

        if cv2.getTrackbarPos('Mask inv','Capture') == 0:
            mask_index=[1,0]
        else:
            mask_index=[0,1]
        ret, thresh = cv2.threshold(gray, min, max, 0)

        contours, a = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        
        masks[0] = cv2.fillPoly(np.zeros_like(gray), contours, (255, 255, 255))
        masks[1] = cv2.bitwise_not(masks[0])

        mask_1 = cv2.bitwise_and(backgrounds[backgrounds_cursor], backgrounds[backgrounds_cursor], mask=masks[mask_index[0]])
        mask_2 = cv2.bitwise_and(frame, frame, mask=masks[mask_index[1]])

        
    else:
        if len(backgrounds) != 0:
            nothing
        else:
            print("No backgrounds detected")
            exit()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_green, upper_green)
        mask_inv = cv2.bitwise_not(mask)
        
        mask_1 = cv2.bitwise_and(backgrounds[backgrounds_cursor], backgrounds[backgrounds_cursor], mask=mask)
        mask_2 = cv2.bitwise_and(frame, frame, mask=mask_inv)

    result = cv2.add(mask_1, mask_2)

    if on_record:
        out.write(result)
        cv2.rectangle(result,(0,0),(result.shape[1] - 1, result.shape[0] - 1), (0,0,255),10)

    cv2.imshow('Capture', result)

    k = cv2.waitKey(int(1000/speed))
    if k == ord('q'):
        if on_record:
            print('Finish recording first!')
        else:
            if cap_mode == 0:
                video.release()
                break
            else:
                cap.release()
                break

    if k == ord('a'):
        if backgrounds_cursor == 0:
            backgrounds_cursor = backgrounds_max_index
        else:
            backgrounds_cursor-=1
    if k == ord('d'):
        if backgrounds_cursor == backgrounds_max_index:
            backgrounds_cursor = 0
        else:
            backgrounds_cursor+=1
    
    if k == ord('o'):
        if process_mode == 0:
            process_mode = 1
        else:
            process_mode = 0

    if k == ord('w'):
        if videos_cursor == videos_max_index:
            videos_cursor = 0
            video = cv2.VideoCapture(video_paths[videos_cursor])
        else:
            videos_cursor+=1
            video = cv2.VideoCapture(video_paths[videos_cursor])
    if k == ord('s'):
        if videos_cursor == 0:
            videos_cursor = videos_max_index
            video = cv2.VideoCapture(video_paths[videos_cursor])
        else:
            videos_cursor-=1
            video = cv2.VideoCapture(video_paths[videos_cursor])

    if k == ord('r') and on_record is False:
        out = cv2.VideoWriter(path_to_record,fourcc,fps,(frame_width,frame_height))
        on_record = True
        print('Recording...')

    if k == ord('e') and on_record==True:
        print('Recording finished')
        on_record = False
        out.release()

    if k == ord('t'):
        if cap_mode == 1:
            if not no_videos:
                cap_mode = 0
                print('Capture mode switched to video')
            else:
                print("No video detected")
        else:
            if no_camera:
                print("No access to the camera")
            else:    
                cap_mode = 1
                print('Capture mode switched to camera')
        
cv2.destroyAllWindows()