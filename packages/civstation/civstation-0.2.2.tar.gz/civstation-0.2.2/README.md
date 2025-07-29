# civstation

## Overview

Provides a Station object, which represents a Station of the kind found in civil plans of roads and other linear features, where 5+10 for example represents a point 510 feet (or meters or any units) from an arbitrary starting point.

## Station objects

Import the Station class:

```python
from civstation import Station
```

Create a station object:

```python
sta = Station("4+56.78")
```

Stations can also be made from a number, which will convert it to a Station.

```python
>>>sta = Station(456.78)
>>>print (sta)
4+56.78
```

Stations can also be made from a Station, for ease of implementation.

Stations default to displaying two decimal places with trailing zeros. This can be changed by setting decimal_places to the desired number.

```python
>>>sta = Station(456.78, decimal_places = 4)
>>>print(sta)
4+56.7800
```

## Offset Objects

Offset objects work similarly to Stations, but represent a deviation to the left or right from the line that the Station refers to.

Right (RT) is positive and Left (LT) is negative.

```python
>>> offset1=Offset("86.47LT")
>>> offset2=Offset("-86.47")
>>> offset1
86.47LT
>>> offset2
86.47LT

```

## Point Objects

Point objects represent a point on a 2D plane, where the x and y coordinates are a Station and an Offset.

## Operations

Stations and Offsets can be added, subtracted, and compared.

Two Points can be subtracted, returning a straight-line distance between them.

Adding a station and a number (float, int, etc.) returns a Station.

Subtracting a number from a station returns a Station.

Subtracting a a Station from a Station returns a **float**. This is because stations represent a position along a line. Subtracting two stations produces a *distance* not a *position*, best represented as a float, not a Station. However, this behavior can be overridden by setting `return_float_on_sub = False`, to work completely in Stations.

There doesn't appear to be a good reason to multiply or divide Stations, so it is not supported. If this is necessary, convert them to floats or another suitable type.  

## Definition of Station object

The following code shows the args taken by a Station object.

```python
class Station:
    def __init__(self, sta, decimal_places = 2, return_float_on_sub = True) -> None:
```
