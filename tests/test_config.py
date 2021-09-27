from optimizer.config import Config, Param, Type, Scale
import pytest


def test_scale_construct():

    assert(Scale.LOG == Scale.construct("log"))
    assert(Scale.LINEAR == Scale.construct("linear"))

    # linear, log 以外は非サポート
    with pytest.raises(ValueError):
        _ = Scale.construct("any")
