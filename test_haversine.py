'''
Unit test for the haversine module.
Comparisons made to
https://www.vcalc.com/wiki/vCalc/Haversine+-+Distance
'''

from floodsystem.haversine import haversine, haversine_vector, Unit


def test_haversine():

    # Test 1: valid inputs
    first_point = (1, 5)
    second_point = (10, 8)
    assert round(haversine(first_point, second_point, unit=Unit.KILOMETERS)) == 1054

    # Test 2: invalid input, should raise a TypeError
    first_point = None
    second_point = (0, 0)
    try:
        haversine(first_point, second_point)
        assert False
    except TypeError:
        assert True


def test_haversine_vector():

    # Test 1: valid inputs
    first_points = [(1, 2), (3, 4), (6, -1)]
    second_points = [(10, -9), (8, -7), (4, 12)]
    assert [round(d) for d in list(haversine_vector(first_points, second_points,
        unit=Unit.KILOMETERS))] == [1575, 1338, 1457]

    # Test 2: invalid inputs
    first_points = [(1, -1), None, (186, 'a')]
    second_points = [(1, 1), (0, 0, 0), (first_points[0])]
    try:
        haversine_vector(first_points, second_points)
        assert False
    except (TypeError, IndexError):
        assert True
