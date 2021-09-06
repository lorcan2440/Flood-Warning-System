'''
Unit tests for the utils module
'''

# pylint: disable=import-error

import import_helper  # noqa

import pytest

from floodsystem.utils import sorted_by_key, wgs84_to_web_mercator, wgs84_to_web_mercator_vector, flatten


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


def test_wgs84_to_web_mercator_vector():

    import numpy as np

    # test array conversion
    TEST_COORDS = [(25, 50), (-45, 120), (50, 0), (0, 40)]
    output_coords = wgs84_to_web_mercator_vector(TEST_COORDS)
    assert np.allclose(output_coords,
        [(5565975, 2875745), (13358339, -5621521), (0, 6446275.84), (4452780, 0)], atol=0.51)

    # test exception, raised by out of bounds input
    TEST_COORDS = np.array([(45, 20), (-10, 60), (520, -700)])
    with pytest.raises(ValueError) as e_info:
        output_coords = wgs84_to_web_mercator_vector(TEST_COORDS)
        print(e_info)


def test_speed_vector_vs_scalar():

    import timeit
    import numpy as np

    # create a large list of coords
    NUM_COORDS = 10000
    REPEAT = 10
    TEST_COORDS = np.transpose((np.random.uniform(-85, 85, size=NUM_COORDS),
                                np.random.uniform(-180, 180, size=NUM_COORDS)))

    time_scalar = timeit.timeit('''output = [wgs84_to_web_mercator(coord) for coord in TEST_COORDS]''',
        globals={"TEST_COORDS": TEST_COORDS, "wgs84_to_web_mercator": wgs84_to_web_mercator},
        number=REPEAT)

    time_vector = timeit.timeit('''output = wgs84_to_web_mercator_vector(TEST_COORDS)''',
        globals={"TEST_COORDS": TEST_COORDS, "wgs84_to_web_mercator_vector": wgs84_to_web_mercator_vector},
        number=REPEAT)

    if time_scalar < time_vector:
        raise RuntimeWarning('Vector function was slower than scalar function. \n'
        f'Total time for scalar function: {time_scalar} \n'
        f'Total time for vector function: {time_vector} \n'
        f'Used {NUM_COORDS} coordinate pairs and repeated {REPEAT} times.')

    assert time_vector < time_scalar


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
