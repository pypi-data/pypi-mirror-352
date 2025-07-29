from spelltinkle.cli_complete import complete_module


def test_jedi():
    res = complete_module('as')
    print(res)
    assert 'asyncio' in res
    assert 'ast' in res
