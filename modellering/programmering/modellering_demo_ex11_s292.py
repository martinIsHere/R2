from pylab import *

m = 3             # massen i kg
q = 1.5           # friksjonskonstanten i kg/s
k = 1.25          # fjærkonstanten i N/m
steglengde = 0.01
x_min = 0
x_maks = 20
x_verdier = arange(x_min, x_maks + steglengde, steglengde)
y_verdier = []
antall_iterasjoner = len(x_verdier) - 1

# Initialbetingelser
s = -0.50
sd = 0

# Differensiallikning - et uttrykk for den andredervierte
sdd = -(q*sd + k*s)/m
y_verdier.append(s)

# Eulermetoden
for i in range(antall_iterasjoner):
  s = s + sd * steglengde
  sd = sd + sdd * steglengde
  sdd = -(q*sd + k*s)/m
  y_verdier.append(s)

plot(x_verdier, y_verdier)
axhline(0, color = "gray")
axvline(0, color = "gray")
xlabel("Tid i sekunder")
ylabel("Utslag i meter")
show()
