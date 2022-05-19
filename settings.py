import glob


def data_paths(data_path):
    list_of_files = glob.glob(data_path + "/*.csv")
    print(list_of_files)
    options_list = []
    for data_file in list_of_files:
        file_name = data_file.split("/")[-1]
        options_list.append({'label': file_name, 'value': data_file})
    return options_list


def init():
    global file_options_list
    file_options_list = data_paths("data")
