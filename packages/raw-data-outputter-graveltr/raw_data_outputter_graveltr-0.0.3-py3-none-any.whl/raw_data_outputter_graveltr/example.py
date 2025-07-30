from importlib.resources import files

def test_function():
    data_text = files('raw_data_outputter_graveltr.data').joinpath('my_data.txt').read_text()
    return data_text
