import pytest

import purekit as pk


class TestGetCallerModule:
    def test_immediate_caller_returns_module_name(self):
        def caller():
            return pk.meta.get_caller_module()

        assert caller() == __name__

    def test_depth_two_returns_outer_module_name(self):
        def outer():
            def inner():
                return pk.meta.get_caller_module(depth=2)

            return inner()

        assert outer() == __name__

    @pytest.mark.parametrize("depth", [0, -1])
    def test_invalid_depth_raises_value_error(self, depth: int):
        expected = f"invalid {depth=!r}; expected >= 1"
        with pytest.raises(ValueError) as excinfo:
            pk.meta.get_caller_module(depth)
        assert str(excinfo.value) == expected

    def test_too_large_depth_raises_runtime_error(self):
        def caller():
            with pytest.raises(RuntimeError) as excinfo:
                pk.meta.get_caller_module(depth=9999)
            assert str(excinfo.value) == "expected to be executed within a function"

        caller()


class TestGetCallerName:
    def test_immediate_caller_returns_function_name(self):
        def foobar():
            return pk.meta.get_caller_name()

        assert foobar() == "foobar"

    def test_depth_two_returns_outer_name(self):
        def outer():
            def inner():
                return pk.meta.get_caller_name(depth=2)

            return inner()

        assert outer() == "outer"

    @pytest.mark.parametrize("depth", [0, -1])
    def test_invalid_depth_raises_value_error(self, depth: int):
        expected = f"invalid {depth=!r}; expected >= 1"
        with pytest.raises(ValueError) as excinfo:
            pk.meta.get_caller_name(depth)
        assert str(excinfo.value) == expected

    def test_too_large_depth_raises_runtime_error(self):
        def caller():
            # choose a large depth to walk past available frames
            with pytest.raises(RuntimeError) as excinfo:
                pk.meta.get_caller_name(depth=9999)
            assert str(excinfo.value) == "expected to be executed within a function"

        caller()


class TestGetCallerVarname:
    def test_returns_immediate_caller_name(self):
        foo = object()

        def caller():
            return pk.meta.get_caller_varname(foo, depth=1)

        assert caller() == "foo"

    def test_returns_outer_frame_name_with_depth(self):
        outer = object()

        def outer_fn():
            inner = object()  # noqa

            def inner_fn():
                # depth=2 -> inspect outer_fn's locals
                return pk.meta.get_caller_varname(outer, depth=2)

            return inner_fn()

        assert outer_fn() == "outer"

    @pytest.mark.parametrize("depth", [0, -1])
    def test_invalid_depth_raises_value_error(self, depth: int):
        expected = f"invalid {depth=!r}; expected >= 1"
        with pytest.raises(ValueError) as excinfo:
            pk.meta.get_caller_varname(object(), depth)
        assert str(excinfo.value) == expected

    def test_depth_out_of_range_raises_runtime_error(self):
        def caller():
            # very large depth -> requested frame won't exist
            return pk.meta.get_caller_varname(object(), depth=9999)

        with pytest.raises(RuntimeError):
            caller()

    def test_name_not_found_raises_value_error(self):
        def caller():
            # pass an ephemeral object that is not bound to a local name in `caller`
            return pk.meta.get_caller_varname(object(), depth=1)

        with pytest.raises(ValueError):
            caller()
