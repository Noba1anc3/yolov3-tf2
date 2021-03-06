import os
import json
import tqdm
import tensorflow as tf
from absl import app, flags, logging
from absl.flags import FLAGS

flags.DEFINE_string('image_dir', '../data/train/images', 'images directory')
flags.DEFINE_string('anno_file', '../data/train/train.json', 'annotation file path')
flags.DEFINE_string('output_prefix', '../data/train', 'prefix of output tfrecord name')


def build_single(annotation):
    """
    构建单张图片的tfrecord
    """

    img_path = os.path.join(FLAGS.image_dir, annotation['filename'])
    img_raw = open(img_path, 'rb').read()

    height, width = annotation['height'], annotation['width']

    xmin = []
    ymin = []
    xmax = []
    ymax = []
    classes_text = []

    for idx in range(len(annotation['bboxes'])):
        bbox = annotation['bboxes'][idx]
        xmin.append(float(bbox[0]) / width)
        ymin.append(float(bbox[1]) / height)
        xmax.append(float(bbox[0] + bbox[2]) / width)
        ymax.append(float(bbox[1] + bbox[3]) / height)
        classes_text.append(annotation['labels'][idx].encode('utf8'))

    single_tfrecord = tf.train.Example(features=tf.train.Features(
        feature={
            'image/encoded': tf.train.Feature(bytes_list=tf.train.BytesList(value=[img_raw])),
            'image/object/bbox/xmin': tf.train.Feature(float_list=tf.train.FloatList(value=xmin)),
            'image/object/bbox/xmax': tf.train.Feature(float_list=tf.train.FloatList(value=xmax)),
            'image/object/bbox/ymin': tf.train.Feature(float_list=tf.train.FloatList(value=ymin)),
            'image/object/bbox/ymax': tf.train.Feature(float_list=tf.train.FloatList(value=ymax)),
            'image/object/class/text': tf.train.Feature(bytes_list=tf.train.BytesList(value=classes_text)),
        }
    ))

    return single_tfrecord


def main(_argv):

    with open(FLAGS.anno_file, 'r', encoding='utf8') as f:
        json_dict = json.load(f)
    logging.info('Json file loaded.')

    id2label = {}
    for cat in json_dict['categories']:
        id2label[cat['id']] = cat['name']
    logging.info("Id2label parse finished. %s", id2label)

    images = json_dict['images']

    logging.info("Start to build tfrecord...")
    writer = tf.io.TFRecordWriter(FLAGS.output_prefix + '.tfrecord')

    for item in tqdm.tqdm(images):

        image_id, filename, height, width = item['id'], item['file_name'], item['height'], item['width']

        bboxes = []
        labels = []

        for anno in json_dict['annotations']:
            if anno['image_id'] == image_id:
                bboxes.append(anno['bbox'])
                labels.append(id2label[anno['category_id']])

        if len(bboxes) == 0:     # 过滤无标签的图片
            continue

        annotation = {'filename': filename,
                      'height': height,
                      'width': width,
                      'bboxes': bboxes,
                      'labels': labels}

        single_tfrecord = build_single(annotation)
        writer.write(single_tfrecord.SerializeToString())

    writer.close()

    logging.info('Tfrecord built.')


if __name__ == '__main__':
    app.run(main)
