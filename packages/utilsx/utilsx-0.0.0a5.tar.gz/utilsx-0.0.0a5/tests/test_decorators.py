from utilsx.decorators import narrow_return


class TestNarrowReturn:
    def test_no_args_two_returns(self) -> None:
        _example_return_value = (1, "la")

        def _example_function() -> tuple[int, str]:
            return _example_return_value

        getter_of_first = narrow_return(0)(_example_function)
        getter_of_second = narrow_return(1)(_example_function)
        assert getter_of_first() == _example_return_value[0]
        assert getter_of_second() == _example_return_value[1]

    def test_one_arg_two_returns(self) -> None:
        def _get_square_and_cube(x: float) -> tuple[float, float]:
            return x**2, x**3

        get_square = narrow_return(0)(_get_square_and_cube)
        get_cube = narrow_return(1)(_get_square_and_cube)
        assert get_square(2) == 4
        assert get_cube(2) == 8
