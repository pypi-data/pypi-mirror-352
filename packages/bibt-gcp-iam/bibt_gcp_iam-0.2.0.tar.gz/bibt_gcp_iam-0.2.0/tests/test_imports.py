def test_level1_import():
    try:
        import bibt  # noqa: F401
    except ImportError:
        assert False
    assert True


def test_level2_import():
    try:
        from bibt import gcp  # noqa: F401
    except ImportError:
        assert False
    assert True


def test_level3_import():
    try:
        from bibt.gcp import iam  # noqa: F401
    except ImportError:
        assert False
    assert True


def test_level4_import():
    try:
        from bibt.gcp.iam import Client  # noqa: F401
    except ImportError:
        assert False
    assert True
