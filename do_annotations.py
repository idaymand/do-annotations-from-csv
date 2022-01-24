import glob
import os
import shutil


def prepare_input_data(global_path, location_path, prefix):
    input_folder = 'csv'
    if os.path.exists(os.path.join(global_path, prefix, input_folder)):
        shutil.rmtree(os.path.join(global_path, prefix, input_folder))
    os.makedirs(os.path.join(global_path, prefix, input_folder), exist_ok=True)
    files = glob.glob(os.path.join(location_path, '*.csv'))
    for file in files:
        file_name = os.path.basename(file).split(prefix+'_')[1]
        dst_file = os.path.join(global_path, prefix, input_folder, file_name)
        shutil.move(file, dst_file)


def get_list_txt(global_path, file_name='list_files.txt'):
    list_files = glob.glob(os.path.join(global_path, '*.jpg'))
    lines_to_write = []
    for index in range(1, len(list_files)):
        base_name = '*_{}.{}.jpg'.format(index, index)
        file = glob.glob(os.path.join(global_path, base_name))
        if len(file) > 0 and os.path.isfile(file[0]):
            name_file = file[0].split('src')[1]
            lines_to_write.append(name_file + ',')
    with open(os.path.join(global_path, file_name), 'w') as fr:
        fr.writelines(lines_to_write)


if __name__ == '__main__':
    #    get_list_txt('/Users/innadaymand/Projects/service-ravin-monorepo/apps/algo/src/assets/algo-test/prod150181')
    prepare_input_data('/Users/innadaymand/Projects/service-ravin-monorepo/apps/algo/src/assets/algo-test/',
                       '/Users/innadaymand/Downloads', 'prod150181')
