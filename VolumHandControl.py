import cv2
import time
import numpy as np
import HandTrackingModule as htm
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

########################################
wCam,hCam = 640, 480 
########################################

pTime = 0


cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(detectionCon=0.75)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
# 

minvol = volRange[0]
maxvol = volRange[1]
vol = 0
volBar = 0
volPer = 0

while True:
    success, img = cap.read()
    img = detector.findHands(img)

    lmList, bbox = detector.findPosition(img)


    if len(lmList) != 0:
        length, img, lineInfo = detector.findDistance(4, 8, img)
        
        if length < 20:
            cv2.circle(img, (lineInfo[2],lineInfo[3]), 10, (0,255,0), cv2.FILLED)
        elif length > 130:
            cv2.circle(img, (lineInfo[2],lineInfo[3]), 10, (0,255,0), cv2.FILLED)
        # hand 20 - 130
        # vol -65 - 0

        vol = np.interp(length, [20,130], (minvol, maxvol))
        volBar = np.interp(length, [20,130], (400, 150))
        volume.SetMasterVolumeLevel(vol, None)
        volPer = np.interp(length, [20,130], (0, 100))
        volume.SetMasterVolumeLevel(vol, None)

    cv2.rectangle(img, (50,150), (85, 400), (0, 255, 0), 3)
    cv2.rectangle(img, (50,int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f"{int(volPer)}%", (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)
    
            

    cTime = time.time()

    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(img, f"FPS: {int(fps)}", (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)


    cv2.imshow("Img", img)
    cv2.waitKey(1)