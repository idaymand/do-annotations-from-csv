# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import glob
import json
import os
import shutil
import csv

import cv2
import numpy
from pandocfilters import Math


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


def set_dump_boxes_view(file, global_path, split_str, folder_input_add_csv, index, main_part, line_num, rows_via):
    base_name_view = (os.path.basename(file).split('.jpg'))[0] + '_view.jpg.csv'
    file_view = os.path.join(global_path, split_str, folder_input_add_csv, base_name_view)
    index_view = 2
    data_view = None
    if os.path.exists(file_view):
        with open(file_view, encoding="utf-8") as f_view:
            data_view = csv.DictReader(f_view)
            for row_view in data_view:
                parts = row_view.get('parts_score')
                provider = row_view.get('provider')
                view_sc = row_view.get('view_score', 0)
                if view_sc is None or view_sc == '':
                    view_sc = 0
                angle_sc = row_view.get('angle_score', 0)
                if angle_sc is None or angle_sc == '':
                    angle_sc = 0
                comb_score = row_view.get('comb_score', 0)
                if comb_score is None or comb_score == '':
                    comb_score = 0
                real_score = row_view.get('real_score', 0)
                if real_score is None or real_score == '':
                    real_score = 0
                region_camera_type = {'shape_attributes': {
                    'name': 'rect',
                    'x': '{}'.format(str(30)),
                    'y': '{}'.format(str(40 * index_view + 10)),
                    'width': '{}'.format(str(700)),
                    'height': '{}'.format(str(10))
                },
                    'region_attributes': {
                        'text': f'prov{str(provider)}_parts{str(numpy.round(float(parts), 5))}_'
                                f'view{str(numpy.round(float(view_sc), 5))}_'
                                f'angle{str(numpy.round(float(angle_sc), 5))}_'
                                f'comb{str(numpy.round(float(comb_score), 5))}_'
                                f'real{str(numpy.round(float(real_score), 5))}',
                    }
                }
                record = {'#filename': main_part.get('file_name'),
                          'file_size': main_part.get('file_size'),
                          'file_attributes': '{}',
                          'region_count': line_num + data_view.line_num,
                          'region_id': index,
                          'region_shape_attributes': json.dumps(region_camera_type['shape_attributes']),
                          'region_attributes': json.dumps(region_camera_type['region_attributes'])
                          }
                rows_via.append(record)
                index = index + 1
                index_view = index_view + 1
    if data_view:
        line_num = line_num + data_view.line_num
     return index, line_num


def set_dump_boxes_scene(file, global_path, split_str, folder_input_add_csv, index, main_part, line_num, rows_via):
    base_name_view = (os.path.basename(file).split('.jpg'))[0] + '_scene.jpg.csv'
    file_view = os.path.join(global_path, split_str, folder_input_add_csv, base_name_view)
    index_view = 1
    if os.path.exists(file_view):
        with open(file_view, encoding="utf-8") as f_view:
            data_view = csv.DictReader(f_view)
            for row_view in data_view:
                provider = row_view.get('provider')
                scene_score = row_view.get('scene_score', 0)
                aspect_ratio_car = row_view.get('aspect_ratio_car', 0)
                region_camera_type = {'shape_attributes': {
                    'name': 'rect',
                    'x': '{}'.format(str(900)),
                    'y': '{}'.format(str(40 * index_view + 10)),
                    'width': '{}'.format(str(700)),
                    'height': '{}'.format(str(10))
                },
                    'region_attributes': {
                        'text': f'prov{str(provider)}_scene_score{str(numpy.round(float(scene_score), 5))}'
                                f'_aspect_ratio_car{str(numpy.round(float(aspect_ratio_car), 5))}',
                    }
                }
                record = {'#filename': main_part.get('file_name'),
                          'file_size': main_part.get('file_size'),
                          'file_attributes': '{}',
                          'region_count': line_num + data_view.line_num,
                          'region_id': index,
                          'region_shape_attributes': json.dumps(region_camera_type['shape_attributes']),
                          'region_attributes': json.dumps(region_camera_type['region_attributes'])
                          }
                rows_via.append(record)
                index = index + 1
                index_view = index_view + 1
    return index;


def make_folder_input_data(download_path, global_path, split_str, name_folder, file_name_fragment):
    if os.path.exists(os.path.join(global_path, split_str, name_folder)):
        shutil.rmtree(os.path.join(global_path, split_str, name_folder))
    os.makedirs(os.path.join(global_path, split_str, name_folder), exist_ok=True)
    files = glob.glob(os.path.join(download_path, file_name_fragment))
    for file in files:
        file_name = (file.split(split_str + '_')[1])
        full_path_dst = os.path.join(global_path, split_str, name_folder, file_name)
        shutil.move(file, full_path_dst)


def make_folder_output_data(download_path, global_path, split_str, name_folder):
    if os.path.exists(os.path.join(global_path, split_str, name_folder)):
        shutil.rmtree(os.path.join(global_path, split_str, name_folder))
    os.makedirs(os.path.join(global_path, split_str, name_folder), exist_ok=True)


def do_annotations_from_csv(global_path, split_str, download_path='/Users/innadaymand/Downloads'):
    folder_result_via = 'annotations'
    make_folder_output_data(download_path, global_path, split_str, folder_result_via)
    # make_folder_input_data(download_path, global_path, split_str, 'view_csv', '*_view.jpg.csv')
    # make_folder_input_data(download_path, global_path, split_str, 'scene_csv', '*_scene.jpg.csv')
    # make_folder_input_data(download_path, global_path, split_str, 'csv', '*.jpg.csv')
    files = glob.glob(os.path.join(global_path, split_str, 'csv', '*.csv'))
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
                        'angle_y': row.get('angle_y'),
                        'location': row.get('location'),
                        'damage_type': row.get('damage_type'),
                        'part_focus': row.get('part_focus'),
                        'image_upload_priority': row.get('image_upload_priority'),
                    }
                origin_start_x = int(float(row.get('left')) * main_part.get('width'))
                origin_start_y = int(float(row.get('top')) * main_part.get('height'))
                origin_end_x = int(float(row.get('right')) * main_part.get('width'))
                origin_end_y = int(float(row.get('bottom')) * main_part.get('height'))
                score = row.get('score')
                if score == '':
                    score = '0'
                binary_rel_score = row.get('binary_rel_score')
                if binary_rel_score == '':
                    binary_rel_score = '-100'
                region = {'shape_attributes': {
                    'name': 'rect',
                    'x': str(origin_start_x),
                    'y': str(origin_start_y),
                    'width': str(origin_end_x - origin_start_x),
                    'height': str(origin_end_y - origin_start_y)
                },
                    'region_attributes': {
                        'text': '{}_{}_{}'.format(row.get('part_name'),
                                                  str(numpy.round(float(score), 2)),
                                                  str(numpy.round(float(binary_rel_score), 2)))
                    }
                }
                record = {'#filename': main_part.get('file_name'),
                          'file_size': main_part.get('file_size'),
                          'file_attributes': '{}',
                          'region_count': data.line_num + 1,
                          'region_id': index,
                          'region_shape_attributes': json.dumps(region['shape_attributes']),
                          'region_attributes': json.dumps(region['region_attributes'])
                          }
                rows_via.append(record)
                index = index + 1
            if len(main_part) > 0:
                region_camera_type = {'shape_attributes': {
                    'name': 'rect',
                    'x': '{}'.format(str(30)),
                    'y': '{}'.format(str(40)),
                    'width': '{}'.format(str(700)),
                    'height': '{}'.format(str(10))
                },
                    'region_attributes': {
                        'text': f'camtype{str(main_part.get("camera_type"))}_{str(main_part.get("angle_y"))}_'
                                f'{main_part.get("location")}_'
                                f'{main_part.get("damage_type")}_{main_part.get("part_focus")}_'
                                f'upload{str(numpy.round(float(main_part.get("image_upload_priority", 0)), 2))}',
                    }
                }
                record = {'#filename': main_part.get('file_name'),
                          'file_size': main_part.get('file_size'),
                          'file_attributes': '{}',
                          'region_count': data.line_num + 1,
                          'region_id': index,
                          'region_shape_attributes': json.dumps(region_camera_type['shape_attributes']),
                          'region_attributes': json.dumps(region_camera_type['region_attributes'])
                          }
                rows_via.append(record)
                index = index + 1
                line_num = data.line_num + 1
                index, line_num = set_dump_boxes_view(file, global_path, split_str, 'view_csv', index, main_part,
                                                      line_num,
                                                      rows_via)
                set_dump_boxes_scene(file, global_path, split_str, 'scene_csv', index, main_part,
                                     (line_num + 1),
                                     rows_via)

                header = ['#filename', 'file_size', 'file_attributes', 'region_count', 'region_id',
                          'region_shape_attributes', 'region_attributes']
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
    for index in range(1, len(files) - 1):
        str_index = '_{}.{}.jpg'.format(index, index)
        file = [x for x in files if str_index in x]
        if len(file) > 0:
            file_data = file[0].split('assets')[1]
            lines.append('/assets{},\r\n'.format(file_data))
    with open(os.path.join(global_path, 'list_files.txt'), "w") as f:
        f.writelines(lines)


if __name__ == '__main__':
    do_annotations_from_csv('/Users/innadaymand/PycharmProjects/service-ravin-monorepo/apps/algo/src/assets/algo-test',
                            split_str='dev1876500')
    # do_list_of_files('/Users/innadaymand/PycharmProjects/service-ravin-monorepo/apps/algo/src/assets/algo-test/dev1882105')
