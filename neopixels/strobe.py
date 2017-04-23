import machine, time, neopixel, urandom

np = neopixel.NeoPixel(machine.Pin(4), 8)
numpixels = 8
black = (0,0,0)
bright = (255,255,255)
pink = (255,20,147)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
gold = (255,215,0)
grey = (25,25,25)
orange = (255,140,0)
purple = (148,0,211)
brown = (102,51,0)
peach = (255,204,204)

j = 0
while True:
    for i in range(12):
        if i%2 == 0:
            if j%10 == 0:
                
                np.fill(gold)
            elif j%10 == 1:
                np.fill(blue)
            elif j%10 == 2:
                np.fill(pink)
            elif j%10 == 3:
                np.fill(red)
            elif j%10 == 4:
                np.fill(purple)
            elif j%10 == 5:
                np.fill(green)
            elif j%10 == 6:
                np.fill(grey)
            elif j%10 == 7:
                np.fill(peach)
            elif j%10 == 8:
                np.fill(grey)
            else:
                np.fill(green)
        else:
            np.fill(black)
        np.write()
        time.sleep(.05)
    time.sleep(.25)
    j += 1