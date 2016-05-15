from argparse import ArgumentParser
from math import pi, cos, sqrt


schematic = r"""
                .___| |____._________.
                |   | |    |         |
                |   C1     |  |      |
                |          !__|-\    |
                |             |   \__!___ Vo(s)
          R1    |    R2       |   /
Vi(s) __/\/\/\__!__/\/\/\__.__|+ /
                           |  |/
                           |
                         __|__
                     C2  ----- 
                           |
                         __|__
                          ---
                           -

"""

def design(order, fc=None, cap=None, res=None):
    return [ Stage(order, k+1, fc, cap, res) for k in range(order / 2) ]

def fmt(val, units):
    conv = (
        (0.0, 1.0e-9, 1.0e-12, 'p'),
        (1.0e-9, 1.0e-3, 1.0e-6, 'u'),
        (1.0e-3, 1.0e+6, 1.0e+3, 'k'),
        (1.0e+6, 1.0e+9, 1.0e+6, 'M'),
        (1.0e+9, 1.0e+99, 1.0e+9, 'G')
    )
    for c in conv:
        if abs(val) >= c[0] and abs(val) < c[1]:
            return '{0} {1}{2}'.format(val / c[2], c[3], units)
    


class Stage(object):

    def __init__(self, n, k, fc=None, cap=None, res=None):
        assert not n % 2, 'This library only computes even order filters'
        assert not (cap is None and res is None), \
            'You must provide either a capacitor or resistor value'
        assert cap is None or res is None, \
        'You may only provide one of capacitor or resistor value'
        self.n = int(n)
        self.k = int(k)
        self.fc = fc
        self.cap = cap
        self.res = res
        if self.res:
            self.r1 = self.r2 = 1.0
            self._set_capacitances()
        else:
            self.c1 = self.c2 = 1.0
            self._set_resistances()
        self._scale()

    def _scale(self):
        for attr in ('r1', 'r2', 'c1', 'c2'):
            print self.fc
            if self.fc:
                setattr(self, attr, 2.0 * pi * self.fc * getattr(self, attr))
            if self.res:
                if attr.startswith('r'):
                    setattr(self, attr, self.res * getattr(self, attr))
                else:
                    setattr(self, attr, getattr(self, attr) / self.res)
            elif self.cap:
                if attr.startswith('c'):
                    setattr(self, attr, self.cap * getattr(self, attr))
                else:
                    setattr(self, attr, getattr(self, attr) / self.cap)

    def _set_capacitances(self):
        self.c2 = self._coefficient()/2.0
        self.c1 = 1.0/self.c2

    def x_set_resistances(self):
        B = self._coefficient()
        i = 1
        while True:
            discr = B*B - 4 * self.c2
            print discr
            if discr < 0:
                i += 1
                self.c2 = 1.0/float(i)
            else:
                break
        self.r2 = (-B + sqrt(discr)) / (2*self.c2)
        self.r1 = 1.0/(self.c2 * self.r2)

    def _set_resistances(self):
        B = self._coefficient()
        i = 1 
        while True:
            discr = (self.c1*B)**2 - 4*self.c1
            if discr < 0:
                i += 1
                self.c1 = float(i)
            else:
                break
        self.r2 = (-B + sqrt(discr))/(4*self.c1)
        self.r1 = 1.0/(self.c1 * self.r2)

    def _coefficient(self):
        return -2 * cos( pi * (2*self.k + self.n - 1)/(2 * self.n) )

    def __str__(self):
        return "c1: {c1}\nc2: {c2}\nr1: {r1}\nr2: {r2}".format(
            c1=fmt(self.c1, 'F'),
            c2=fmt(self.c2, 'F'),
            r1=fmt(self.r1, 'Ohms'),
            r2=fmt(self.r2, 'Ohms'))

if __name__ == '__main__':
    parser = ArgumentParser(description=
        "calculate component values for any even order Butterworth filters "
        "using the Sallen-Key unity gain topology.")
    parser.add_argument('order', metavar='N', type=int,
        help='The order of the filter (must be even)')
    parser.add_argument('-f', '--fc', metavar='Fc', type=float,
        default=0.15915494309189535, help='The fc frequency in Hz')
    parser.add_argument('-r', '--res', metavar='R', type=float,
        help='The value of the resistors you wish to use (you must include '
            'exactly one of either the -r or -c options)')
    parser.add_argument('-c', '--cap', metavar='C', type=float,
        help='The value of the smallest capacitor you wish to use. Larger '
            'capacitor sizes will be integer multiples of this size '
            '(you must include exactly one of either the -r or -c options)')
    parser.add_argument('-p', '--print-schematic', action='store_true',
        help='Print the generic schematic of the filter stages (each stage '
            'adds 2 orders to the filter).')
    args = parser.parse_args()

    if args.print_schematic:
        print(schematic)
        print

    for i, stage in enumerate(
            design(args.order, args.fc, args.cap, args.res), 1):
        print('STAGE {0}'.format(i))
        for l in str(stage).split('\n'):
            print('    {0}'.format(l))
