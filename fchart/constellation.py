from math import pi

class BscStar:
    def __init__(self):
        """
        This class has the following fields:

        - name           name of star
        - constellation  three letter constellation abbreviation, e.g. AND
        - ra             right ascension in radians (J2000)
        - dec            declination in radians (J2000)
        - mag            magnitude
        """
        self.number = None
        self.const_number = ''
        self.greek = ''
        self.constellation=''
        self.ra=-1.0
        self.dec=0.0
        self.mag=-100.0


class Constellation:
    def __init__(self):
        """
        This class has the following fields:

        - name           name of star
        - shape lines    constellation lines
        """
        self.name = ''
        self.lines = []

class ConstellationCatalog:

    def __init__(self, bsc5_filename='', constell_filename=''):
        self.bright_stars = import_bsc5(bsc5_filename)
        self.constellations = import_constellation(constell_filename, self)

def parse_bsc5_line(line):
    star = BscStar()

    star.number = int(line[:4].strip())
    star.name = line[4:14].strip()
    star.constellation = line[11:14].upper()
    star.constell_number = line[4:7].strip().upper()

    star.greek = line[7:10].strip().lower()
    if line[75:77].strip() != '':
        star.ra = float(line[75:77])*pi/12.0 + float(line[77:79])*pi/(12.0*60.0) + float(line[79:83])*pi/(12*60.0*60)
        star.dec = float(line[83]+'1')*(float(line[84:86])*pi/180.0 + float(line[86:88])*pi/(180.0*60) + float(line[88:90])*pi/(180.0*60*60))
        star.mag = float(line[102]+'1') * float(line[103:107])
    return star


def parse_constellation_line(line, const_catalog):
    constell = Constellation()
    constell.name = line[0:3].upper()
    star_count = int(line[3:7].strip())
    star_stack = []
    for i in range(0, star_count):
        index = 8 + i * 5
        star_id = int(line[index:index + 4].strip())
        if len(star_stack) > 1 and star_stack[-2] == star_id:
            star_stack.pop()
        else:
            star_stack.append(star_id)
            if len(star_stack)>1:
                constell.lines.append((star_stack[-2], star_stack[-1]))
                s1 = const_catalog.bright_stars[star_stack[-2]-1]
                s2 = const_catalog.bright_stars[star_stack[-1]-1]
    return constell


def import_bsc5(filename):
    # Import all saguaro objects that are not NGC or IC objects, or M40
    bsc_star_list = []

    sf = open(filename, 'r')
    lines = sf.readlines()
    sf.close()

    for line in lines:
        bsc_star = parse_bsc5_line(line)
        bsc_star_list.append(bsc_star)
    return bsc_star_list


def import_constellation(filename, const_catalog):
    # Import all saguaro objects that are not NGC or IC objects, or M40
    constellation_list = []

    sf = open(filename, 'r')
    lines = sf.readlines()
    sf.close()

    for line in lines:
        line = line.strip()
        if line.startswith('#') or line == '':
            continue
        constell = parse_constellation_line(line, const_catalog)
        constellation_list.append(constell)
    return constellation_list

__all__ = ['BscStar' , 'Constellation', 'ConstellationCatalog', 'import_bsc5', 'import_constellation']
