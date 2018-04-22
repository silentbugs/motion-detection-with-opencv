# motion-detection-with-opencv
Forked from [motion-detection-with-opencv](https://github.com/YaoQ/motion-detection-with-opencv) on github.

Uses celery for asynchronous notifications.


## info
- Python2.7
- Webcam used is /dev/video0

### Usage
```bash
$ pip install -r requirements.txt
```
```bash
$ python motion-detector.py -c conf.json
$ celery -A tasks worker -l info
```
