# Quad H-Bridge MotorDriver Class
Driver for a pyboard v1.1 pyskin dc motor driver utilising a TI 754410 quad h-bridge.

Has proved useful for driving multiple dc motor's, steppers and as a simple audio amplifier.

Long superceded, retained in-case I want to reawaken it at some point.

```
Skin in Y position:
                     -----------------------
          Pin Vin -> |16 +ve        1,2EN 1| -> Pin Y8
           Pin Y1 -> |15 4A            1A 2| -> Pin Y7
          Motor 2 -> |14 4Y            1Y 3| -> Motor 1
    Gnd & -ve Bat -> |13 Gnd          Gnd 4| -> Gnd & -ve Bat
    Gnd & -ve Bat -> |12 Gnd          Gnd 5| -> Gnd & -ve Bat
          Motor 2 -> |11 3Y            2Y 6| -> Motor 1
           Pin Y2 -> |10 3A            2A 7| -> Y6
           Pin Y3 -> |9  3,4EN    +ve Bat 8| -> +ve Bat
                     -----------------------
```
## example
```python
>>> import dcmotor
>>> y1 = dcmotor.DCMOTOR(dcmotor.Y1)
>>> y1.state(50) #50% duty, forward
50.0
>>> y1.state(-50) #50% duty, backwards
-50.0
>>> y1.state() #report state
-50.0
>>> y1.state(0) #stop
0.0
```
## specify pwm frequency or reverse motor pols
```python
>>> import dcmotor
>>> y1 = dcmotor.DCMOTOR(dcmotor.Y1, freq=2000, reverse=True)
>>> y2.freq()
2000
>>> y2.freq(1000)
1000
```
## h-bridge motor configs defined
```
Y1 = enable pin Y8 tim12_ch2, control = pins Y6 & Y7
Y2 = enable pin Y3 tim10_ch1, control = pins Y1 & Y2
X1 = enable pin X8 tim14_ch1, control = pins X6 & X7
X2 = enable pin X3 tim9_ch1, control = pins X1 & X2
```
