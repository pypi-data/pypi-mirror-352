import pytest
from defdict import DefDict  # Replace 'your_module' with the actual module name where DefDict is defined

def test_instance_creation(benchmark):
    def wrapper():
        return DefDict()
    result = benchmark(wrapper)
    assert isinstance(result, DefDict)

def test_data_assignment(benchmark):
    def wrapper():
        d = DefDict({'key1': 1, 'key2': 2})
    benchmark(wrapper)

def test_data_retrieval(benchmark):
    def wrapper():
        d = DefDict({'key1': 1, 'key2': 2})
        return d.get('key1')
    result = benchmark(wrapper)

def test_filter_function(benchmark):
    def wrapper():
        d = DefDict({'key1': 1, 'key2': 2,'key3': 3})
        return d.filter(['key1', 'key2'])
    result = benchmark(wrapper)
    assert 'key3' not in result.keys()


def test_format_function(benchmark):
    def wrapper():
        d = DefDict({'key1': 1, 'key2': 2})
        return d.format({'key1': 10, 'key2': 20})
    result = benchmark(wrapper)
    assert result.get('key1') == 10


def test_nested_defdict(benchmark):
    def run_tests():
        inner_def = {'inner_key': float}
        outer_def = {'outer_key': inner_def}
        nested_def_dict = DefDict(outer_def, nested_def=True)
        # Check if the nested DefDict definitions are created correctly
        assert 'outer_key' in nested_def_dict.DEF
        assert isinstance(nested_def_dict.DEF['outer_key'], DefDict)
        assert 'inner_key' in nested_def_dict.DEF['outer_key'].DEF

        # Test setting and getting values
        nested_def_dict.set({'outer_key': {'inner_key': 5.0}})
        assert nested_def_dict.get('outer_key').get('inner_key') == 5.0

        # Test the list() method
        assert nested_def_dict.list() == [nested_def_dict.get('outer_key')]

        # Test the list_keys() method
        assert nested_def_dict.list_keys() == ['outer_key']

        # Test the as_ruled() method
        assert nested_def_dict.as_ruled() == {'outer_key': nested_def_dict.get('outer_key').as_ruled()}

    # Benchmarking the setup and the test running
    benchmark(run_tests)
