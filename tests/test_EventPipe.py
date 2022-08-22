from flightgear_python.fg_if import EventPipe


def test_send_recv():
    ep = EventPipe()
    msg = (1, 2, 3)
    ep.parent_send(msg)
    assert ep.child_recv() == msg
