'''
Unit tests for the utils module
'''

# pylint: disable=import-error

import import_helper  # noqa

from floodsystem.utils import sorted_by_key, wgs84_to_web_mercator, flatten


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

    CAMBRIDGE_CITY_CENTRE = (52.2053, 0.1218)  # (lat, lon)
    output_coord = wgs84_to_web_mercator(CAMBRIDGE_CITY_CENTRE)
    assert tuple([round(i) for i in output_coord]) == (13559, 6837332)


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
