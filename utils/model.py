from typing import Tuple
from shapely.geometry import Point


class Emission:
    """
    This class defines the different pollutant emissions
    """

    def __init__(self, co2=0, co=0, nox=0, hc=0, pmx=0):
        """
        Emission constructor
        :param co2: Quantity of CO2(in mg)
        :param co: Quantity of C0(in mg)
        :param nox: Quantity of Nox(in mg)
        :param hc: Quantity of HC(in mg)
        :param pmx: Quantity of PMx(in mg)
        """
        self.co2 = co2
        self.co = co
        self.nox = nox
        self.hc = hc
        self.pmx = pmx

    def __add__(self, other):
        """
        Add two emission objects
        :param other: The other Emission object to add
        :return: A new object whose emission values are the sum of both Emission object
        """
        return Emission(self.co2 + other.co2, self.co + other.co, self.nox + other.nox, self.hc + other.hc,
                        self.pmx + other.pmx)

    def value(self):
        """
        :return: The sum of all emissions
        """
        return self.co2 + self.co + self.nox + self.hc + self.pmx

    def __repr__(self) -> str:
        """
        :return: The Emission string representation
        """
        repr = f'Emission(co2={self.co2},co={self.co},nox={self.nox},hc={self.hc},pmx={self.pmx})'
        return str(repr)



class Vehicle:
    """
    The Vehicle class defines a vehicle object
    """

    def __init__(self, veh_id: int, pos: Tuple[float, float], tipo, vel, classe, edge):
        """
        Vehicle constructor
        :param veh_id: The vehicle ID
        :param pos: The position of the vehicle one the map
        """
        self.emissions: Emission = Emission()
        self.veh_id = veh_id
        self.pos = Point(pos)
        self.type = tipo
        self.speed = vel
        self.classe = classe
        self.edge = edge

    def __repr__(self) -> str:
        """
        :return: The Vehicle string representation
        """
        return str(self.__dict__)