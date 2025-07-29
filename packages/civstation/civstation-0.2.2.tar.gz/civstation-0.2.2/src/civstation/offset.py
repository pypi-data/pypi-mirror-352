from .stations import Station

class Offset(Station):
    """Represents an Offset of the kind used with Stations in civil plans. 
    where 86.47RT for example represents a point 86.47 feet (or meters or any units) to the right of the centerline.
    
    Attributes:
        offset: Can be in Offset notation ("45.00LT") or from a float (-45.0). Right is positive and Left is negative.
        decimal_places: number of decimal places shown. Defaults to 2.
    """
    #TODO: Refactor this, it's too complex. But it does work.
    #get rid of repeated calls to .lower().
    def __init__ (self, offset, decimal_places = 2, return_float_on_sub = True) ->None:
            self.decimal_places = decimal_places
            self.return_float_on_sub = return_float_on_sub
            if isinstance(offset, Offset):
                self.val=float(offset)
            elif "rt" in str(offset).lower() or "lt" in str(offset).lower():
                negative=False
                if "rt" in str(offset).lower()[-2:]:
                    if "'" in str(offset):
                        endnum=str(offset).index("'")
                    else: endnum=str(offset).lower().index("r")
                if "lt" in str(offset).lower()[-2:]:
                    negative=True
                    if "'" in str(offset):
                        endnum=str(offset).index("'")
                    else: endnum=str(offset).lower().index("l")                
                try:
                    self.val=float(str(offset)[:endnum])
                except: raise ValueError("Not a valid Offset")
                if negative: self.val=-self.val
            else:
                try: self.val = float(offset)
                except: raise ValueError("Not a valid offset.")
    
    def __str__(self):
        offset = f"{round(abs(self.val), self.decimal_places):.{self.decimal_places}f}"
        if self.val <0: return offset+"LT"
        elif self.val >0: return offset+"RT"
        else: return "" 

    def __neg__(self):
        return Offset(-self.val)