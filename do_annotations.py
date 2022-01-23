import glob
import os


def get_list_txt(global_path, file_name='list_files.txt'):
    list_files = glob.glob(os.path.join(global_path, '*.jpg'))
    lines_to_write = []
    for index in range(1, len(list_files)):
        base_name = '*_{}.{}.jpg'.format(index, index)
        file = glob.glob(os.path.join(global_path, base_name))
        if len(file) > 0 and os.path.isfile(file[0]):
            lines_to_write.append(file[0] + ', \n')
    with open(os.path.join(global_path, file_name), 'w') as fr:
        fr.writelines(lines_to_write)


if __name__ == '__main__':
    get_list_txt('/Users/innadaymand/Projects/service-ravin-monorepo/apps/algo/src/assets/algo-test/prod150181')
