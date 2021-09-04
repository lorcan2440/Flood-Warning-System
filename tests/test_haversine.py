'''
Unit tests for the haversine module.
Comparisons made to
https://www.vcalc.com/wiki/vCalc/Haversine+-+Distance
'''

# pylint: disable=import-error

import import_helper  # noqa
import pytest
import os

from floodsystem.haversine import haversine, haversine_vector, Unit


def test_haversine():

    # Test 1: valid inputs
    first_point = (1, 5)
    second_point = (10, 8)
    assert round(haversine(first_point, second_point, unit=Unit.KILOMETERS)) == 1054

    # Test 2: invalid input, should raise a TypeError
    first_point = None
    second_point = (0, 0)
    with pytest.raises(TypeError) as e_info:
        haversine(first_point, second_point)
        print(e_info)


def test_haversine_vector():

    # Test 1: valid inputs
    first_points = [(1, 2), (3, 4), (6, -1)]
    second_points = [(10, -9), (8, -7), (4, 12)]
    assert [round(d) for d in list(haversine_vector(first_points, second_points,
        unit=Unit.KILOMETERS))] == [1575, 1338, 1457]

    # Test 2: different length inputs, using combination mode
    first_points = [(1, 2), (3, 4), (6, -1)]
    second_points = [(10, -9), (8, -7)]

    with pytest.raises(ValueError) as e_info:
        assert haversine_vector(first_points, second_points, unit=Unit.KILOMETERS) is not None
        print(e_info)

    # Test 3: invalid inputs
    first_points = [(1, -1), None, (186, 'a')]
    second_points = [(1, 1), (0, 0, 0), (first_points[0])]
    with pytest.raises((TypeError, IndexError)) as e_info:
        haversine_vector(first_points, second_points)
        print(e_info)


def test_vector_without_numpy():

    # Temporarily remove numpy and try to use haversine vector functions
    os.system('pip uninstall -y numpy')
    first_points = [(1, 2), (3, 4), (6, -1)]
    second_points = [(10, -9), (8, -7), (4, 12)]
    dists = list(haversine_vector(first_points, second_points))
    assert [round(d) for d in dists] == [1575, 1338, 1457]
    os.system('pip install numpy')
