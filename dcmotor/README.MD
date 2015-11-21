Quad H-Bridge MotorDriver Class
===
*relies on micropython pre-timers PWM module, needs updating*

Configured for pyskin with TI 754410 in the following configuration;

```
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

21/11/15 partial implementation of timer/channel driven PWM
