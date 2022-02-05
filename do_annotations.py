import csv
import glob
import json
import os
import shutil
import numpy as np
from PIL import Image


class ProcessingAnnotations:
    def __init__(self, global_path, input_data_path, prefix_path, csv_location='csv', view_csv_location='view_csv'):
        self.global_path = global_path
        self.input_data_path = input_data_path
        self.prefix = prefix_path
        self.csv_location = csv_location
        self.via_csv_location = 'annotations'
        self.view_csv_location = view_csv_location
        self.data_for_save = []
        self.top_left_inform_point = [40, 40]
        self.box_inform_width = 700
        self.box_inform_height = 10

    def prepare_input_data(self, remove_old_data=True):
        if os.path.exists(os.path.join(self.global_path, self.prefix, self.csv_location)) and remove_old_data:
            shutil.rmtree(os.path.join(self.global_path, self.prefix, self.csv_location))
        os.makedirs(os.path.join(self.global_path, self.prefix, self.csv_location), exist_ok=True)
        if os.path.exists(os.path.join(self.global_path, self.prefix, self.view_csv_location)) and remove_old_data:
            shutil.rmtree(os.path.join(self.global_path, self.prefix, self.view_csv_location))
        os.makedirs(os.path.join(self.global_path, self.prefix, self.view_csv_location), exist_ok=True)
        files = glob.glob(os.path.join(self.global_path, self.prefix, self.csv_location, '*_view*.csv'))
        for file in files:
            file_name = os.path.basename(file).split(self.prefix + '_')[1]
            dst_file = os.path.join(self.global_path, self.prefix, self.view_csv_location, file_name)
            shutil.move(file, dst_file)
        files = glob.glob(os.path.join(self.input_data_path, '*.csv'))
        for file in files:
            file_name = os.path.basename(file).split(self.prefix + '_')[1]
            dst_file = os.path.join(self.global_path, self.prefix, self.csv_location, file_name)
            shutil.move(file, dst_file)

    def prepare_output_data(self):
        if os.path.exists(os.path.join(self.global_path, self.prefix, self.via_csv_location)):
            shutil.rmtree(os.path.join(self.global_path, self.prefix, self.via_csv_location))
        os.makedirs(os.path.join(self.global_path, self.prefix, self.via_csv_location), exist_ok=True)

    @staticmethod
    def get_via_header():
        return ['#filename', 'file_size', 'file_attributes', 'region_count', 'region_id',
                'region_shape_attributes', 'region_attributes']

    @staticmethod
    def get_csv_header():
        return ['file_name', 'camera_type', 'angle_y', 'angle_x', 'image_upload_priority', 'location', 'damage_type',
                'part_focus',
                'part_name', 'part_id', 'left', 'top', 'right', 'bottom', 'score']

    def add_one_box_to_save_data(self, box, score, box_count, class_name, image_name, image_size, element_count):
        shape_dict = json.dumps({'name': 'rect', 'x': box[0], 'y': box[1],
                                 'width': box[2],
                                 'height': box[3]})
        text = {'text': '{}_{}'.format(class_name, str(np.round(score, 2)))}
        attr_dict = json.dumps(text)
        my_dict = {"#filename": image_name, "file_size": image_size,
                   "file_attributes": "{}",
                   "region_count": element_count, "region_id": box_count,
                   "region_shape_attributes": shape_dict, "region_attributes": attr_dict}
        box_count += 1
        self.data_for_save.append(my_dict)
        return box_count

    def add_one_element_to_save_data(self, box, text, box_count, image_name, image_size, element_count):
        shape_dict = json.dumps({'name': 'rect', 'x': str(box[0]), 'y': str(box[1]),
                                 'width': str(box[2]),
                                 'height': str(box[3])})
        text = {'text': '{}'.format(text)}
        attr_dict = json.dumps(text)
        my_dict = {"#filename": image_name, "file_size": image_size,
                   "file_attributes": "{}",
                   "region_count": element_count, "region_id": box_count,
                   "region_shape_attributes": shape_dict, "region_attributes": attr_dict}
        box_count += 1
        self.data_for_save.append(my_dict)
        return box_count

    def correct_element_count(self, box_count):
        for row in self.data_for_save:
            row['region_count'] = box_count

    def view_csv_to_via_csv(self, file, box_count, image_name, image_size):
        view_file_name = os.path.basename(file).replace('.csv', '_view.csv')
        view_file = os.path.join(self.global_path, self.prefix, self.view_csv_location, view_file_name)
        index_box = 1
        with open(view_file, 'r', encoding='UTF8') as f:
            reader = csv.DictReader(f, delimiter=',', lineterminator='\n')
            for row in reader:
                provider = row.get('provider', 0)
                part_score = np.round(row.get('part_score', 0), 2)
                angle_score = np.round(row.get('angle_score', 0), 5)
                real_score = np.round(row.get('real_score', 0), 5)
                text = '{}_part={}_angle={}_total{}'.format(provider, part_score, angle_score, real_score)
                box = [self.top_left_inform_point[0],
                       self.top_left_inform_point[1] + index_box*self.box_inform_height*2,
                       self.box_inform_width,
                       self.box_inform_height]
                box_count = self.add_one_element_to_save_data(box, text, box_count, image_name, image_size, 1)
                index_box = index_box + 1
        return box_count

    def csv_to_via_csv(self, prefix_file_name, score_inf=0.1):
        files = glob.glob(os.path.join(self.global_path, self.prefix, self.csv_location, prefix_file_name + '.csv'))
        for file in files:
            self.data_for_save = []
            main_result_put = False
            image_name = os.path.basename(file).replace('.csv', '')
            width, height = Image.open(os.path.join(self.global_path, self.prefix, image_name)).size
            file_size = os.path.getsize(os.path.join(self.global_path, self.prefix, image_name))
            box_count = 0
            with open(file, 'r', encoding='UTF8') as f:
                reader = csv.DictReader(f, delimiter=',', lineterminator='\n')
                for row in reader:
                    if main_result_put is False:
                        element_text = '{}_{}_{}'.format(row.get('location', ''), row.get('damage_type', ''),
                                                         row.get('part_focus', ''))
                        box = [self.top_left_inform_point[0],
                               self.top_left_inform_point[1],
                               self.box_inform_width,
                               self.box_inform_height]
                        box_count = self.add_one_element_to_save_data(box, element_text, box_count,
                                                                      image_name, file_size, 1)
                        main_result_put = True
                    left = int(float(row['left']) * width)
                    top = int(float(row['top']) * height)
                    right = int(float(row['right']) * width)
                    bottom = int(float(row['bottom']) * height)
                    score = float(row['score'])
                    part_name = row.get('part_name', '')
                    box = [left, top, right - left, bottom - top]
                    if score > score_inf:
                        box_count = self.add_one_box_to_save_data(box, score, box_count, part_name,
                                                                  image_name, file_size, 1)
            box_count = self.view_csv_to_via_csv(file, box_count, image_name, file_size)
            self.correct_element_count(box_count + 1)
            full_file_name = os.path.join(self.global_path, self.prefix, self.via_csv_location, os.path.basename(file))
            with open(full_file_name, 'w', encoding='UTF8') as f:
                w = csv.DictWriter(f, self.get_via_header(), delimiter=',', lineterminator='\n')
                w.writeheader()
                w.writerows(self.data_for_save)
                print('{} was processing'.format(os.path.basename(file)))

    def transformation_data(self, remove_old_data=True):
        self.prepare_input_data(remove_old_data)
        self.prepare_output_data()
        self.csv_to_via_csv('*', score_inf=0.2)


def get_list_txt(global_path, file_name='list_files.txt'):
    list_files = glob.glob(os.path.join(global_path, '*.jpg'))
    lines_to_write = []
    for index in range(1, len(list_files)):
        base_name = '*_{}.{}.jpg'.format(index, index)
        file = glob.glob(os.path.join(global_path, base_name))
        if len(file) > 0 and os.path.isfile(file[0]):
            name_file = file[0].split('src')[1]
            lines_to_write.append(name_file + ',\n')
    with open(os.path.join(global_path, file_name), 'w') as fr:
        fr.writelines(lines_to_write)


if __name__ == '__main__':
    # get_list_txt('/Users/innadaymand/Projects/service-ravin-monorepo/apps/algo/src/assets/algo-test/prod150181')
    process_annotation = ProcessingAnnotations(
        '/Users/innadaymand/Projects/service-ravin-monorepo/apps/algo/src/assets/algo-test/',
        '/Users/innadaymand/Downloads',
        'prod150181')
    process_annotation.transformation_data(False)
