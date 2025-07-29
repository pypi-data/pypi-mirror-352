def itk_windowcalculate(neww:int,newh:int,startw:int,starth:int):
    xmult = (100*neww)/startw
    ymult = (100*newh)/starth
    if xmult > ymult:
        return ymult
    else:
        return xmult

def itk_windowresizefont(fo:int,mu:float):
    return round((fo*mu)/100)

def multdivide(number,multiplier,diviser):
    return number*multiplier/diviser

def roundedmultdivide(number,multiplier,diviser):
    return round(number*multiplier)/diviser