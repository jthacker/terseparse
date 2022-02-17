from . import assert_conv_fails
from terseparse import types

def test_Int():
    t = types.Int(-0xF, 0x10)
    t('-15') == -15
    t('-0xF') == -0xF
    t('0xF') == 15
    t('15') == 15

    assert_conv_fails(t, '-16')
    assert_conv_fails(t, '-0x10')
    assert_conv_fails(t, '0x10')
    assert_conv_fails(t, '16')

def test_Int_leading_zero():
    t = types.Int()
    t('00') == 0
    t('-00') == 0
    t('043') == 43

    assert_conv_fails(t, 'a')

def test_Int_u32():
    t = types.Int.u32

    t('0') == 0
    t('0xFFFFFFFF') == 2**32 - 1

    assert_conv_fails(t, '-1')
    assert_conv_fails(t, '0xFFFFFFFF + 1')

def test_Or():
    t = types.Or(types.Int.negative, types.Int(1, 10))

    assert_conv_fails(t, '0')

    assert t('-10') == -10
    assert t('9') == 9

def test_Dict():
    t = types.Dict({'a': types.Int(0, 2), 'b': str})

    assert_conv_fails(t, 'asdf')
    assert_conv_fails(t, 'a:-1')
    assert_conv_fails(t, 'a:2')
    assert_conv_fails(t, 'a:2 b:asdf')

    assert t('a:0') == {'a': 0}
    assert t('b:asdf') == {'b': 'asdf'}
    assert t('a:0 b:asdf') == {'a': 0, 'b': 'asdf'}
    assert t('a=0,b=asdf') == {'a': 0, 'b': 'asdf'}
    assert t('a:1, b=asdf') == {'a': 1, 'b': 'asdf'}

def test_Dict_default_value():
    t = types.Dict({'a': types.Int() | types.Keyword('', 5)})

    assert_conv_fails(t, 'a:a')

    assert t('a') == {'a': 5}
    assert t('a:5') == {'a': 5}

def test_Dict_punctuation():
    t = types.Dict({'a': str, 'b': str})
    assert t('a:/a/b/c/d,b:/e/f/g') == {'a': '/a/b/c/d', 'b': '/e/f/g'}

def test_Dict_to_Set():
    dt = types.Dict({'a': types.Int(0, 2), 'b': str})
    t = dt.keys_to_set_type()
    assert t('a a') == {'a'}
    assert t('a b') == {'a', 'b'}
    assert t('b, a') == {'a', 'b'}

def test_List():
    t = types.List(types.Or(types.Keyword('a'), types.Keyword('b')))
    assert_conv_fails(t, 'asdf')
    assert_conv_fails(t, 'bsdf')

    assert t('a') == ['a']
    assert t('b') == ['b']
    assert t('a b') == ['a', 'b']

def test_Keyword():
    t = types.Keyword('a', 1)
    assert_conv_fails(t, 'b')
    assert_conv_fails(t, 1)

    assert t('a') == 1

def test_Or_string():
    t = types.Or('a', 'b', 'c')
    assert_conv_fails(t, 'd')
    assert_conv_fails(t, '0')

    assert t('a') == 'a'
    assert t('b') == 'b'
    assert t('c') == 'c'

def test_Or_string_syntax_sugar():
    t = types.Int() | 'a'
    assert_conv_fails(t, 'aa')

    assert t('a') == 'a'
    assert t('1234') == 1234

def test_Set():
    t = types.Set(types.Or('a', 'b', 'c'))
    assert_conv_fails(t, 'd')
    assert_conv_fails(t, 'a,b,c,d')

    assert t('a') == set(('a',))
    assert t('a,b') == set(('a', 'b'))

def test_Set_duplicates():
    t = types.Set(types.Or('a', 'b', 'c'))

    assert t('a,a,a,b') == set(('a','b'))
