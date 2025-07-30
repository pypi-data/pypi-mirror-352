from importlib.resources import files

def read_data_file(filename):
    data_text = files('raw_data_outputter_graveltr.data').joinpath('my_data.txt').read_text()
    return data_text
