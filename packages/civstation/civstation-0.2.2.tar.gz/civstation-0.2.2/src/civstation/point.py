from .stations import Station
from .offset import Offset
from math import sqrt

class Point:
    """Represents a point on a 2D plane, where the x and y coordinates are a Station and an Offset.

    Attributes:
        Station: A Station object, or a number or string that can be made into a Station.
        Offset: An Offset object, or a number or string that can be made into an Offset.
    """
    def __init__(self, station: Station, offset = None)->None:
        if offset is None:
            offset = Offset(0)
        try:
            self.station=Station(station)
            self.offset = Offset(offset)
        except (TypeError, ValueError) as e:
            raise ValueError ("Invalid Station or Offset") from e 
        
    def __str__(self):
        return f"{str(self.station)} {str(self.offset)}"
    
    def __repr__(self):
        return self.__str__()    

    def __sub__(self, subtracted_val):
        return self.distance(subtracted_val)
    
    def __rsub__(self, subtracted_val):
        return self.distance(subtracted_val)
    
    def distance(self, other)->float:
        if isinstance(other, Station):
            other=Point(other)
        if not isinstance(other, Point):
            raise ValueError("Must use two Point objects to get distance.")
        
        xdist=float(self.station-other.station)
        ydist=float(self.offset-other.offset)
        return sqrt((xdist**2) + (ydist**2))
    
    def dist2d(self, other):
        """Returns a list with both the x (Station) and y (Offset) distances between two Points. 
        """
        x_delta = self.station-other.station
        y_delta = self.offset-other.offset
        return [x_delta,y_delta]
    

    