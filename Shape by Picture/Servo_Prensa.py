lata=0

if (Servo1=HIGH)
  lata=lata+1
Colocar no código do servo 1 um delay de 3 segundos
if (lata>0 and iniciodecurso=LOW)
  servo2 = HIGH
else (lata>0 and iniciodecurso=HIGH)
  servo2=LOW
