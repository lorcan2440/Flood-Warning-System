'''
Unit tests for the utils module
'''

# pylint: disable=import-error

import import_helper  # noqa

import pytest
import os

from floodsystem.utils import sorted_by_key, wgs84_to_web_mercator, flatten, coord_letters, \
    haversine, haversine_vector, Unit


def test_sort():

    '''
    Test sort container by specific index
    '''

    a = (10, 3, 3)
    b = (5, 1, -1)
    c = (1, -3, 4)
    list0 = (a, b, c)

    # Test sort on 1st entry
    list1 = sorted_by_key(list0, 0)
    assert list1[0] == c
    assert list1[1] == b
    assert list1[2] == a

    # Test sort on 2nd entry
    list1 = sorted_by_key(list0, 1)
    assert list1[0] == c
    assert list1[1] == b
    assert list1[2] == a

    # Test sort on 3rd entry
    list1 = sorted_by_key(list0, 2)
    assert list1[0] == b
    assert list1[1] == a
    assert list1[2] == c


def test_reverse_sort():

    '''
    Test sort container by specific index (reverse)
    '''

    a = (10, 3, 3)
    b = (5, 1, -1)
    c = (1, -3, 4)
    list0 = (a, b, c)

    # Test sort on 1st entry
    list1 = sorted_by_key(list0, 0, reverse=True)
    assert list1[0] == a
    assert list1[1] == b
    assert list1[2] == c

    # Test sort on 2nd entry
    list1 = sorted_by_key(list0, 1, reverse=True)
    assert list1[0] == a
    assert list1[1] == b
    assert list1[2] == c

    # Test sort on 3rd entry
    list1 = sorted_by_key(list0, 2, reverse=True)
    assert list1[0] == c
    assert list1[1] == a
    assert list1[2] == b


def test_wgs84_to_web_mercator():

    '''
    Verified with
    https://epsg.io/transform#s_srs=4326&t_srs=3857&x=0.1020031&y=52.1946039
    '''

    # test normal input
    TEST_COORD = (52.2053, 0.1218)  # (lat, lon)
    output_coord = wgs84_to_web_mercator(TEST_COORD)
    assert tuple([round(i) for i in output_coord]) == (13559, 6837332)

    # test lat = zero
    TEST_COORD = (0, 50)
    output_coord = wgs84_to_web_mercator(TEST_COORD)
    print(output_coord)
    assert tuple([round(i) for i in output_coord]) == (5565975, 0)

    # test long = zero
    TEST_COORD = (50, 0)
    output_coord = wgs84_to_web_mercator(TEST_COORD)
    assert tuple([round(i) for i in output_coord]) == (0, 6446276)

    # test lat = long = zero
    TEST_COORD = (0, 0)
    output_coord = wgs84_to_web_mercator(TEST_COORD)
    assert tuple([round(i) for i in output_coord]) == (0, 0)

    # test out of range exception
    TEST_COORD = (90, 0)
    with pytest.raises(ValueError) as e_info:
        output_coord = wgs84_to_web_mercator(TEST_COORD)
        print(e_info)


def test_flatten():

    '''
    List of lists -> list
    List of tuples -> list
    List of list of lists -> list of lists -> list
    '''

    assert flatten([[1, 2, 3], [4, 5, 6]]) == [1, 2, 3, 4, 5, 6]
    assert flatten([(1, 2, 3), (4, 5)]) == [1, 2, 3, 4, 5]
    assert flatten(flatten([[[1, 2], [3, 4]], [[5, 6], [7, 8]], [[9, 10], [11, 12]]])) == [
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
    ]


def test_coord_letters():

    '''
    Simple tests
    '''

    TEST_COORD = (25, 50)
    assert coord_letters(*TEST_COORD) == ('N', 'E')

    TEST_COORD = (-60, -150)
    assert coord_letters(*TEST_COORD) == ('S', 'W')

    TEST_COORD = (0, 0)
    assert coord_letters(*TEST_COORD) == ('N', 'E')


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
