from floodsystem.stationdata import build_station_list


def run():

    # Build list of stations
    stations = build_station_list()

    # Print number of stations
    print(f"Number of stations: {len(stations)}")

    # Display data from 3 stations:
    for station in stations:
        if station.name in [
                'Bourton Dickler', 'Surfleet Sluice', 'Gaw Bridge'
        ]:
            print(station)


if __name__ == "__main__":
    print("\n *** Task 1A: CUED Part IA Flood Warning System *** \n")
    print('Hello world')
    run()
