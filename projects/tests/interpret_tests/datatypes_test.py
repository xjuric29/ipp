from interpret_lib import components
from interpret_lib import instructions


def test_var1():
    frames = components.Frames()
    var = instructions.Var('GF@ahoj', frames)
    assert var.get_frame() == 'GF'
    assert var.get_name() == 'ahoj'


def test_const_int1():
    const = instructions.Const('int', '+954785')
    assert const.get_value() == 954785


def test_const_int2():
    const = instructions.Const('int', '123')
    assert const.get_value() == 123


def test_const_int3():
    const = instructions.Const('int', '-6')
    assert const.get_value() == -6


def test_const_bool1():
    const = instructions.Const('bool', 'true')
    assert const.get_value() is True


def test_const_bool2():
    const = instructions.Const('bool', 'false')
    assert const.get_value() is False


def test_const_str1():
    const = instructions.Const('string', 'ahoj')
    assert const.get_value() == 'ahoj'


def test_const_str2():
    const = instructions.Const('string', 'ᛚᛀᛉᛯᚤᛓᛠᛖᚺᛕᛘ')
    assert const.get_value() == 'ᛚᛀᛉᛯᚤᛓᛠᛖᚺᛕᛘ'


def test_const_str3():
    const = instructions.Const('string', '\\065\\032\\065')
    assert const.get_value() == 'A A'


def test_const_str4():
    const = instructions.Const('string', '\\065ahoj\\032boo\\065')
    assert const.get_value() == 'Aahoj booA'


def test_label1():
    label = instructions.Label('call')
    assert label.get_value() == 'call'


def test_label2():
    label = instructions.Label('_123')
    assert label.get_value() == '_123'


def test_type1():
    ipp_type = instructions.Type('int')
    assert ipp_type.get_value() == int


def test_type2():
    ipp_type = instructions.Type('bool')
    assert ipp_type.get_value() == bool


def test_type3():
    ipp_type = instructions.Type('string')
    assert ipp_type.get_value() == str
