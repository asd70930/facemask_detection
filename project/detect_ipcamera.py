import cv2
import os.path
import config
import threading
import time
import Queue

def get_cam(path, q):
    cap = cv2.VideoCapture(path)
    while 1:
        ret, image = cap.read()
        s = image.shape
        h = s[0]
        w = s[1]
        # print(image.shape)
        # if not w + h == 720 + 576:
        #     o = int((w - 720) / 2)
        #     z = int((h - 576) / 2)
        #
        #     image = image[z:z + 576, o:o + 720]
        # print(image.shape)

        q.put(image) if ret else None
        try:
            q.get(timeout=1) if q.qsize() > 1 else None
        except:
            pass
        # time.sleep(0.05)
    # print("queue_img_put shut down")

cascPath = config.cascPath
mouthPath = config.casc_mouthPath
ipcamera_path = config.ipcamera_path
if not os.path.isfile(cascPath):
        raise RuntimeError("%s: not found" % cascPath)
if not os.path.isfile(mouthPath):
        raise RuntimeError("%s: not found" % mouthPath)

# out = -1  # out :-1   can't find eyes
          # out : 0   not masking
          # out : 1   masking

faceCascade = cv2.CascadeClassifier(cascPath)
mouthCascade = cv2.CascadeClassifier(mouthPath)
combo = 0
flag = -2

que_put = Queue.Queue(maxsize=2)
t = threading.Thread(target=get_cam, args=(ipcamera_path, que_put))
t.daemon = True
t.start()
time.sleep(1)

while 1:
    image = que_put.get()
    time_start = time.time()
    # ret, image = cap.read()

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray,
                                         # detector options
                                         scaleFactor=1.1,
                                         minNeighbors=4,
                                         minSize=(20, 20))
    if len(faces) != 0:
        for (x, y, w, h) in faces:
            face_range = image[y:y + w, x:x + h]
            gray_face = cv2.cvtColor(face_range, cv2.COLOR_BGR2GRAY)

            cv2.imshow('face_range', face_range)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
            mouths = mouthCascade.detectMultiScale(gray_face,
                                                 # detector options
                                                 scaleFactor=1.1,
                                                 minNeighbors=4,
                                                 minSize=(5, 5))
            print('mouth:', len(mouths))
            #
            if len(mouths) != 0:
                masked = False
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
            else:
                masked = True
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)


    time_done = time.time()
    time_process = time_done - time_start
    fps = 1/time_process
    print 'infrence time :', time_process
    cv2.putText(image, 'fps:'+str(fps), (60, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.imshow('Video', image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    time.sleep(1)
cv2.destroyAllWindows()
