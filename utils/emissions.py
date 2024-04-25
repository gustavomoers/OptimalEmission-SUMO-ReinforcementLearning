import traci
from typing import List

from utils.model import  Vehicle, Emission


def compute_vehicle_emissions(veh_id):
    """
    Recover the emissions of different pollutants from a vehicle and create an Emission instance
    :param veh_id: The vehicle ID
    :return: A new Emission instance
    """
    co2 = traci.vehicle.getCO2Emission(veh_id)
    co = traci.vehicle.getCOEmission(veh_id)
    nox = traci.vehicle.getNOxEmission(veh_id)
    hc = traci.vehicle.getHCEmission(veh_id)
    pmx = traci.vehicle.getPMxEmission(veh_id)

    return Emission(co2, co, nox, hc, pmx)


def get_all_vehicles() -> List[Vehicle]:
    """
    Recover all useful information about vehicles and creates a vehicles list
    :return: A list of vehicles instances
    """
    vehicles = list()
    for veh_id in traci.vehicle.getIDList():
        veh_pos = traci.vehicle.getPosition(veh_id)
        veh_type = traci.vehicle.getTypeID(veh_id)
        veh_speed = traci.vehicle.getSpeed(veh_id)
        emission_class = traci.vehicle.getEmissionClass(veh_id)
        vehicle = Vehicle(veh_id, veh_pos, veh_type, veh_speed, emission_class)
        vehicle.emissions = compute_vehicle_emissions(veh_id)
        vehicles.append(vehicle)
    return vehicles




