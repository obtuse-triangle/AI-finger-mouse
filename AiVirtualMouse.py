import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy
import win32api
from win32con import *


########################################################################
wCam, hCam = 640, 480
frameR = 100  # Frame Reduction
smoothening = 5
########################################################################

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

scrollToggle = False

cup = [0, 0]

pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0
clicktoggle = False
RMclick = 0

detector = htm.handDetector(maxHands=2)
wSrc, hSrc = autopy.screen.size()
# print(wSrc, hSrc)

while True:
    # 1. find hand Landmarks
    success, img = cap.read()

    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)
    cv2.rectangle(
        img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2
    )

    # 2. get the tip of the index and middle fingers
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        x20, y20 = lmList[20][1:]

        # print(x1, y1, x2, y2)
        # 3. Check which fingers are up
        fingers = detector.fingersUp()

        # 4. Only Index Finger : moving mode
        if fingers[1] == 1:
            # 5. Convert Coordinates

            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wSrc))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hSrc))
            # 6. Smoothen Values
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening
            # 7. Move Mouse
            try:
                autopy.mouse.move(wSrc - clocX, clocY)
            except:
                pass
            cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)

            # 8. Both Index and middle fingers up : clicking mode
            # 9. Find distance between fingers
            length, img, lineInfo = detector.findDistance(3, 5, img)
            length1, img, lineInfo1 = detector.findDistance(8, 12, img)
            # print(length)
            # 10. Click mouse if distance short
            if length < 30:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 10, (0, 255, 0), cv2.FILLED)
                if clicktoggle is False:
                    autopy.mouse.toggle(down=True)
                    clicktoggle = True
            else:
                if clicktoggle is True:
                    autopy.mouse.toggle(down=False)
                    clicktoggle = False
            if length1 < 22:
                if scrollToggle is False:
                    scrollToggle = True
                    cup = [plocX, plocY]
                cv2.circle(
                    img, (lineInfo1[4], lineInfo1[5]), 10, (255, 255, 0), cv2.FILLED
                )

                scroll = int((clocY - cup[1] ) * 1.3)

                win32api.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, scroll, 0)
                cup = [plocX, plocY]
            else:
                plocX, plocY = clocX, clocY
                scrollToggle = False
                cup = [plocX, plocY]
            plocX, plocY = clocX, clocY
            if fingers[4] == 0 and fingers[3] == 0:
                if time.time() - RMclick > 1:
                    cv2.circle(img, (x20, y20), 10, (0, 255, 255), cv2.FILLED)
                    autopy.mouse.click(autopy.mouse.Button.RIGHT)
                    RMclick = time.time()

    # 11. Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    # 12. Display
    cv2.imshow("Image", img)
    cv2.setWindowProperty("Image", cv2.WND_PROP_TOPMOST, 1)
    cv2.waitKey(1)
