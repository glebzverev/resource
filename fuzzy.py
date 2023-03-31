import numpy as np

class Fuzzy:
    
    def __init__(self, val=0):
        val = np.array(val) if isinstance(val,(list, np.ndarray)) else np.array([val])
        self.val = val.astype('float32')
         
    def __invert__(self):          # ~x      NOT
        return Fuzzy(1-self.val)
     
    def __and__(self, other):      # x & y   AND
        return Fuzzy( np.minimum(self.val, other.val) )
 
    def __or__(self, other):       # x | y    OR
        return Fuzzy( np.maximum(self.val, other.val) )
 
    def __eq__(self, other):
        return Fuzzy(self.val == other.val)
     
    def __str__(self):
        return f"{self.val[0]}" if len(self.val)==1 else  f"{self.val}"
     
    def minmax(self):
        return (self.val.min(), self.val.max())
     
    def __gt__(self, other):
        return Fuzzy( np.minimum( np.ones_like(self.val), 1-self.val+other.val) )

x = Fuzzy(       [0,  0,  0,  0.5,0.5,0.5,1,  1,  1] )
y = Fuzzy(       [0,  0.5,1,  0,  0.5,1,  0,  0.5,1] )
 
print(x & y )  # [0.  0.  0.  0.  0.5 0.5 0.  0.5 1. ]    
print(x | y )  # [0.  0.5 1.  0.5 0.5 1.  1.  1.  1. ]

vals = np.linspace(0,1,101, dtype='float32')
 
x  = Fuzzy(vals)
print ( (x &  x).minmax() )   # (0.0, 1.0)
print ( (x & ~x).minmax() )   # (0.0, 0.5)
print ( (x | ~x).minmax() )   # (0.5, 1.0)
 
x, y, z  = np.meshgrid(vals, vals, vals) 
x, y, z  = Fuzzy(x), Fuzzy(y),  Fuzzy(z)
 
print ( ((x & (y | z))  == ((x & y) | (x & z))).minmax() ) # (1.0, 1.0)

d, x1, y1, z1  = Fuzzy([1]), Fuzzy([1]), Fuzzy([0.2]),  Fuzzy([0.6])
print(d & x1 & y1 | z1)

