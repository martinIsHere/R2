"""
matte 
"""
def sigma_sum(bottom, top, func):
    """
    Sigma notasjonssum
    """
    if bottom < top:
        _sum=0
        for i in range(bottom, top+1):
            if func:
                _sum+=func(i)
        return _sum
    return "NAN"
def vt_x(i, a, dx):
    """
    gir x_i for venstretilnaerming, vt.
    """
    return a+i*dx
    
def venstretilnaerming(a,b,f,n):
    """
    En venstretilnærming som oppgitt i boken
    """
    dx=(b-a)/n
    def function(i):
        return f(vt_x(i-1,a,dx))*dx
    return sigma_sum(1,n, function)

def f_1(x):
    """
    Eksempel funksjon f(x)
    """
    return x

print(venstretilnaerming(0,4,f_1,9999))
