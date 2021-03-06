# import the necessary packages
import argparse
import warnings
import datetime
import imutils
import json
import time
import cv2

from tasks import exec_notify


class MotionDetector:
    STATUS_OCCUPIED = 'occupied'
    STATUS_UNOCCUPIED = 'unoccupied'
    STATUS_CHOICES = {
        STATUS_OCCUPIED: 'Occupied',
        STATUS_UNOCCUPIED: 'Unoccupied',
    }

    # filter warnings, load the configuration
    def __init__(self, args):
        warnings.filterwarnings('ignore')
        self.conf = json.load(open(args['conf']))

    def detect(self):
        # initialize the camera and grab a reference to the raw camera capture
        video_capture = cv2.VideoCapture(0)

        # allow the camera to warmup, then initialize the average frame, last
        # uploaded timestamp, and frame motion counter
        print '[INFO] warming up...'
        time.sleep(self.conf['main']['camera_warmup_time'])
        avg = None
        last_uploaded = datetime.datetime.now()
        motion_counter = 0

        # capture frames from the camera
        while True:
            # grab the raw NumPy array representing the image and initialize
            # the timestamp and occupied/unoccupied text
            ret, frame = video_capture.read()
            timestamp = datetime.datetime.now()
            status = self.STATUS_UNOCCUPIED

            # resize the frame, convert it to grayscale, and blur it
            frame = imutils.resize(frame, width=500)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            # if the average frame is None, initialize it
            if avg is None:
                print '[INFO] starting background model...'
                avg = gray.copy().astype('float')
                continue

            # accumulate the weighted average between the current frame and
            # previous frames, then compute the difference between the current
            # frame and running average
            cv2.accumulateWeighted(gray, avg, 0.5)
            frame_delta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

            # threshold the delta image, dilate the thresholded image to fill
            # in holes, then find contours on thresholded image
            thresh = cv2.threshold(
                frame_delta, self.conf['main']['delta_thresh'], 255, cv2.THRESH_BINARY
            )[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            (_, cnts, _) = cv2.findContours(
                thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            # loop over the contours
            for c in cnts:
                # if the contour is too small, ignore it
                if cv2.contourArea(c) < self.conf['main']['min_area']:
                    continue

                # compute the bounding box for the contour, draw it on the
                # frame, and update the text
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                status = self.STATUS_OCCUPIED

            # draw the text and timestamp on the frame
            ts = timestamp.strftime('%A %d %B %Y %I:%M:%S%p')
            cv2.putText(
                frame,
                'Room Status: {}'.format(self.STATUS_CHOICES[status]),
                (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                2
            )
            cv2.putText(
                frame, ts,
                (10, frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.35,
                (0, 0, 255),
                1
            )

            # check to see if the room is occupied
            if status == self.STATUS_OCCUPIED:
                # check to see if enough time has passed between uploads
                if (timestamp - last_uploaded).seconds >= self.conf['main']['min_upload_seconds']:
                    # increment the motion counter
                    motion_counter += 1

                    # check to see if the number of frames with consistent
                    # motion is high enough
                    if motion_counter >= self.conf['main']['min_motion_frames']:
                        path = self.conf['extra']['output_directory']
                        _file = timestamp.strftime('%Y_%m_%dT%H_%M_%S' + '.jpg')

                        if self.conf['main']['dry_run']:
                            print 'file: %s' % (path + _file)

                        else:
                            cv2.imwrite(path + _file, frame)

                        last_uploaded = timestamp
                        motion_counter = 0

                        attachment = None

                        if self.conf['main']['add_attachments']:
                            attachment = (path + _file)

                        if self.conf['main']['use_celery']:
                            exec_notify.delay(attachment)

            # otherwise, the room is not occupied
            else:
                motion_counter = 0

            # check to see if the frames should be displayed to screen
            if self.conf['main']['show_video']:
                # display the security feed
                cv2.imshow('Security Feed', frame)
                key = cv2.waitKey(1) & 0xFF

                # if the `q` key is pressed, break from the loop
                if key == ord('q'):
                    break


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument(
    '-c', '--conf', required=True,
    help='path to the JSON configuration file'
)
args = vars(ap.parse_args())

# initialize the class
motion_detector = MotionDetector(args)
motion_detector.detect()
