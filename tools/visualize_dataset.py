
import cv2
import numpy as np

from absl import app, flags, logging
from absl.flags import FLAGS

from yolov3_tf2.dataset import load_tfrecord_dataset, transform_images
from yolov3_tf2.utils import draw_outputs

flags.DEFINE_string('classes', '../data/voc2012.names', 'path to classes file')
flags.DEFINE_integer('size', 416, 'resize images to')
flags.DEFINE_string(
    'dataset', '../data/voc2012_train.tfrecord', 'path to dataset')
flags.DEFINE_string('output', '../data/output.jpg', 'path to output image')
flags.DEFINE_integer('yolo_max_boxes', 100, '')


def main(_argv):
    class_names = [c.strip() for c in open(FLAGS.classes).readlines()]
    logging.info('classes loaded')

    dataset = load_tfrecord_dataset(FLAGS.dataset, FLAGS.classes, FLAGS.size)
    dataset = dataset.shuffle(512)

    for image, labels in dataset.take(1):
        boxes = []
        scores = []
        classes = []

        for x1, y1, x2, y2, label in labels:
            if x1 == 0 and x2 == 0:
                continue

            boxes.append((x1, y1, x2, y2))
            scores.append(1)
            classes.append(label)

        nums = [len(boxes)]
        boxes = [boxes]
        scores = [scores]
        classes = [classes]

        logging.info('labels:')
        for i in range(nums[0]):
            logging.info('\t{}, {}, {}'.format(class_names[int(classes[0][i])],
                                               np.array(scores[0][i]),
                                               np.array(boxes[0][i])))

        img = cv2.cvtColor(image.numpy(), cv2.COLOR_RGB2BGR)
        img = draw_outputs(img, (boxes, scores, classes, nums), class_names)
        cv2.imwrite(FLAGS.output, img)
        logging.info('output saved to: {}'.format(FLAGS.output))


if __name__ == '__main__':
    app.run(main)
