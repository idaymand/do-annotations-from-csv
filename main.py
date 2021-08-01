# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import glob
import json
import os
import shutil
import csv

import cv2


def save_VIA_boxes(texts, boxes, width, height, regions):
    index = 0
    for (start_X, start_Y, end_X, end_Y) in boxes:
        origin_start_x = start_X * width
        origin_start_y = start_Y * height
        origin_end_x = end_X * width
        origin_end_y = end_Y * height
        region = {'shape_attributes': {
            'name': 'rect',
            'x': origin_start_x,
            'y': origin_start_y,
            'width': origin_end_x - origin_start_x,
            'height': origin_end_y - origin_start_y
        },
            'region_attributes': {
                'Text': texts[index]
            }
        }
        regions.append(region)
        index = index + 1


def do_annotations_from_csv(global_path, split_str, download_path='/Users/innadaymand/Downloads'):
    folder_result_via = 'annotations'
    folder_input_csv = 'csv'
    file_name_via = 'via_annotations.csv'
    if os.path.exists(os.path.join(global_path, split_str, folder_result_via)):
        shutil.rmtree(os.path.join(global_path, split_str, folder_result_via))
    os.makedirs(os.path.join(global_path, split_str, folder_result_via), exist_ok=True)
    # if os.path.exists(os.path.join(global_path, split_str, folder_input_csv)):
    #     shutil.rmtree(os.path.join(global_path, split_str, folder_input_csv))
    os.makedirs(os.path.join(global_path, split_str, folder_input_csv), exist_ok=True)
    files = glob.glob(os.path.join(download_path, '*.jpg.csv'))
    for file in files:
        file_name = (file.split(split_str + '_')[1])
        full_path_dst = os.path.join(global_path, split_str, folder_input_csv, file_name)
        shutil.move(file, full_path_dst)
    files = glob.glob(os.path.join(global_path, split_str, folder_input_csv, '*.csv'))
    for file in files:
        rows_via = []
        with open(file, encoding="utf-8") as f:
            data = csv.DictReader(f)
            main_part = {}
            index = 0
            for row in data:
                if len(main_part) == 0:
                    original_file_name = os.path.basename(row.get('file_name'))
                    file_size = os.path.getsize(os.path.join(global_path, split_str, original_file_name))
                    img = cv2.imread(os.path.join(global_path, split_str, original_file_name))
                    [height, width, _] = img.shape
                    main_part = {
                        'file_name': original_file_name,
                        'file_size': file_size,
                        'width': width,
                        'height': height,
                        'camera_type': row.get('camera_type'),
                    }
                origin_start_x = int(float(row.get('left')) * main_part.get('width'))
                origin_start_y = int(float(row.get('top')) * main_part.get('height'))
                origin_end_x = int(float(row.get('right')) * main_part.get('width'))
                origin_end_y = int(float(row.get('bottom')) * main_part.get('height'))
                region = {'shape_attributes': {
                    'name': 'rect',
                    'x': str(origin_start_x),
                    'y': str(origin_start_y),
                    'width': str(origin_end_x - origin_start_x),
                    'height': str(origin_end_y - origin_start_y)
                },
                    'region_attributes': {
                        'text': row.get('part_name'),
                        #                        'Score': row.get('score')
                    }
                }
                record = {'#filename': main_part.get('file_name'),
                          'file_size': main_part.get('file_size'),
                          'file_attributes': '{}',
                          'region_count': data.line_num,
                          'region_id': index,
                          'region_shape_attributes': json.dumps(region['shape_attributes']),
                          'region_attributes': json.dumps(region['region_attributes'])
                          }
                rows_via.append(record)
                index = index + 1
            region_camera_type = {'shape_attributes': {
                'name': 'rect',
                'x': '{}'.format(str(30)),
                'y': '{}'.format(str(30)),
                'width': '{}'.format(str(100)),
                'height': '{}'.format(str(20))
            },
                'region_attributes': {
                    'text': 'camera_type{}'.format(str(main_part.get('camera_type'))),
                }
            }
            record = {'#filename': main_part.get('file_name'),
                      'file_size': main_part.get('file_size'),
                      'file_attributes': '{}',
                      'region_count': data.line_num,
                      'region_id': index,
                      'region_shape_attributes': json.dumps(region_camera_type['shape_attributes']),
                      'region_attributes': json.dumps(region_camera_type['region_attributes'])
                      }
            rows_via.append(record)
            header = ['#filename', 'file_size', 'file_attributes', 'region_count', 'region_id',
                      'region_shape_attributes', 'region_attributes']
            if len(main_part) > 0:
                with open(os.path.join(global_path, split_str, folder_result_via,
                                       main_part.get('file_name') + '.csv'), 'w') as f:
                    w = csv.DictWriter(f, header, delimiter=',', lineterminator='\n')
                    w.writeheader()
                    for row in rows_via:
                        w.writerow(row)
                    print(' file {} was processed '.format(main_part.get('file_name')))
            else:
                print(' file {} does not have detections '.format(file))

    print('folder {} was processed'.format(split_str))


def do_list_of_files(global_path):
    files = glob.glob(os.path.join(global_path, '*.jpg'))
    lines = []
    for index in range(1, len(files)):
        str_index = '_{}.{}.jpg'.format(index, index)
        file = [x for x in files if str_index in x]
        if len(file) > 0:
            file_data = file[0].split('assets')[1]
            lines.append('"/assets{}",\r\n'.format(file_data))
    with open(os.path.join(global_path, 'list_files.txt'), "w") as f:
        f.writelines(lines)


if __name__ == '__main__':
    do_annotations_from_csv('/Users/innadaymand/PycharmProjects/service-ravin-monorepo/apps/algo/src/assets',
                            split_str='Eliron')
 #   do_list_of_files('/Users/innadaymand/PycharmProjects/service-ravin-monorepo/apps/algo/src/assets/Eliron')
