from pylab import *

a = 0
b = 50
n = 10000             # antall steg
delta_t = (b - a)/n   # steglengde
N0 = 6500             # initialbetingelse

def Nder(N):
  return -0.007*N - 25

t = zeros(n)
N = zeros(n)

N[0] = N0

for i in range(n - 1):
  N[i+1] = N[i] + Nder(N[i]) * delta_t
  t[i+1] = t[i] + delta_t

plot(t, N)
xlabel("Tid (år)")
ylabel("Innbyggertall")
show()
