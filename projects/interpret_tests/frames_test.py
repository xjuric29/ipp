from interpret_lib import components


frames = components.Frames()


def test_tmp_frame():
    global frames

    frames.create_frame()

    assert frames.get_frame() == {}


def test_tmp_fill_frame():
    global frames
    global result1

    tmp = frames.get_frame()
    tmp['a'] = 123
    tmp['_123'] = True

    result1 = {'a': 123, '_123': True}
    assert frames.get_frame() == result1


def test_local_frame():
    global frames
    global result1

    frames.push_frame()

    assert frames.get_local_frame() == result1


def test_tmp_frame_advanced():
    global frames
    global result2

    frames.create_frame()
    frames.create_frame()
    frames.create_frame()
    frames.create_frame()
    frames.create_frame()
    tmp = frames.get_frame()
    tmp[1] = 8
    frames.push_frame()

    result2 = {1: 8}
    assert frames.get_local_frame() == tmp


def test_pop1():
    global frames
    global result2

    frames.pop_frame()

    assert frames.get_frame() == result2


def test_pop2():
    global frames
    global result1

    frames.pop_frame()

    assert frames.get_frame() == result1


def test_global_frame():
    global frames

    frames.globalFrame[4] = 1

    assert frames.globalFrame == {4: 1}
