class Station:
    """Represents a Station of the kind found in civil plans of roads and other linear features, 
    where 5+10 for example represents a point 510 feet (or meters or any units) from an arbitrary starting point.
    
    Attributes:
        sta: Can be in Station notation ("4+56.00") or from a float (456.00)
        decimal_places: number of decimal places shown. Defaults to 2.
    """
    def __init__(self, sta, decimal_places = 2, return_float_on_sub = True) -> None:
        self.decimal_places = decimal_places
        self.return_float_on_sub = return_float_on_sub  
        
        if isinstance(sta, Station):
            self.val = float(sta)
        #sta should be a number, or a station in 12+34 or 12+34.56 format.
        elif "+" in str(sta):
            if sta.count("+") > 1: raise ValueError("Station should only have one + character.")   
            elif "." in sta and sta.index(".")-sta.index("+") != 3:
                raise ValueError("There should be two digits between + character and decimal point.")
            elif "." not in sta and sta [-3] != "+":
                raise ValueError("There should be two digits after the + character.")
            else:
                try:   
                    self.val = float(sta.replace("+", ""))
                except ValueError:
                    raise ValueError("Station should be a valid number when + character is removed.")
        else:
            try:
                self.val = float(sta)
            except ValueError:
                raise ValueError("Not a valid number or Station.")
            
    def __str__(self):
        #Show in station format and add leading and trailing zeros as needed.
        if self.decimal_places <= 0:
            sta = str(int(round(self.val, self.decimal_places)))
            while len(sta) < 3:
                sta = "0" + sta
            plus_sign_index = -2

        else:
            sta = str(round(self.val, self.decimal_places))
            while sta.index(".") < 3:
                sta = "0" + sta
            while sta.index(".") > len(sta) - (self.decimal_places + 1):
                sta = sta + "0"
            plus_sign_index = sta.index(".") - 2

        sta = sta[:plus_sign_index] + "+" + sta[plus_sign_index:]    
        return sta
    
    def __repr__(self):
        return self.__str__()    
    def __float__(self):
        return float(self.val)
    def __int__(self):
        return int(self.val)

    def __add__(self, added_val):
        return Station(float(self.val) + float(added_val))
    def __radd__(self, added_val):
        return self.__add__(added_val)
    def __sub__(self, subtracted_val):
        if isinstance(subtracted_val, Station) and self.return_float_on_sub == True:
            return float(self.val) - float(subtracted_val)
        else: return Station(float(self.val) - float(subtracted_val))
    def __rsub__(self, subtracted_from):
        if isinstance(subtracted_from, Station) and self.return_float_on_sub == True:
            return float(subtracted_from) - float(self.val)
        else: return Station(float(subtracted_from) - float(self.val))

    def __eq__(self, compare_val) -> bool:
        if self.val == compare_val: return True
        else: return False
    def __ne__(self, compare_val) -> bool:
        if self.val != compare_val: return True
        else: return False
    def __lt__(self, compare_val) -> bool:
        if self.val < compare_val: return True
        else: return False
    def __gt__(self, compare_val) -> bool:
        if self.val > compare_val: return True
        else: return False
    def __le__(self, compare_val) -> bool:
        if self.val <= compare_val: return True
        else: return False
    def __ge__(self, compare_val) -> bool:
        if self.val >= compare_val: return True
        else: return False    
  