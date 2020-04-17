#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ############################################################################
#
# mtn.py
# 04/17/2020 (c) Juan M. Casillas <juanm.casillas@gmail.com>
#
# calculate the MNT sheet for a given point, in lat lon
#
# https://www.mitma.gob.es/recursos_mfom/nuevcar.pdf
#
# (lon, lat)
# λο= - 9º 51’ 15”00 φο= 44º 00’ 00”00 Datum ETRS89 
#
# ∆λ= 20’ e ∆ϕ= -10’ para MTN50, 
# ∆λ= 10’ e ∆ϕ= -5’ para MTN25,
# ∆λ= 5’ e ∆ϕ= -2’ 30” para MTN10 
#
# Ejemplo: Cual será la esquina SE de la hoja MTN50 h559 <> 1922 (Cc=19 Ff=22)
# Longitud = - 9º 51’ 15” + (19/3)º = -3.520833333.. = -3º 31’ 15”
# Latitud =   44º 00’ 00” – (22/6)º  = 40.33333333...= 40º 20’ 00”
# Las restantes esquinas:
# SW -3º 51’ 15” NW -3º 51’ 15” NE -3º 31’ 15”
#    40º 20’ 00”    40º 30’ 00”    40º 30’ 00”
# En resumen, sabiendo el número de hoja CcFf, basta con sumar al “punto origen de
# numeración” lo siguiente para obtener la esquina SE y, a partir de ésta las restantes:
# MTN50 λ=λο+(Cc/3)º, ϕ= ϕο−(Ff/6)º
# MTN25 λ=λο+(Cc/6)º, ϕ= ϕο−(Ff/12)º
# MTN10 λ=λο+(Cc/12)º, ϕ= ϕο−(Ff/24)º 
#
# Sean las coordenadas de un punto P (ϕ, λ) y las del origen para la cuenta del número de
# la hoja Po (ϕο, λο), expresadas todas en grados sexagesimales y decimal de grado.
# Se supone que la función ENTERO da sólo la parte entera sin forzar o lo que es lo
# mismo el entero más próximo a cero, en cuyo caso se empleará la función oportuna (por
# ejemplo FIX u otras). 
#
# o CcFf (MTN50)=(ENTERO((λ −λο)*3)+1)*100+ENTERO((ϕο −ϕ)*6)+1
#     como la hoja es de 20’ x 10’ los factores son
#     60’/20’=3 por grado y 60’/10’=6 por grado
# o CcFf (MTN25)=(ENTERO((λ −λο)*6)+1)*100+ENTERO((ϕο −ϕ)*12)+1
#     como la hoja es de 10’ x 5’ los factores son
#     60’/10’=6 por grado y 60’/5’=12 por grado
# o CccFff (MTN10)=(ENTERO((λ −λο)*12)+1)*1000+ENTERO((ϕο −ϕ)*24) +1
#     como la hoja es de 5’ x 2.5’ los factores son
#     60’/5’=12 por grado y 60’/2.5’=24 por grado 
#
# Ejemplo
#
# ¿ Dónde se encuentra el punto ϕ=40º 22’ 25”00 λ=-(3º 29’ 06”32) ?
#
# Columna  λ −λο =-(3º 29’ 06”32) – (-9º 31’ 15”) = 6º 22’ 08”68 = 6º36907777..
# Fila     ϕο −ϕ = 44º 00’ 00” – 40º 22’ 25”00    = 3º 37’ 35”00 = 3º62638888..
#
# MTN50 ent(6º369077*3)+1= 20 ent(3º626388*6)+1 = 22 2022 (tabla) h560
#
# Los valores Cc Ff (columna fila) hallados para MTN50 servirán para dilucidar el
# cuarto de MTN25 o la correspondiente columna fila del MTN10
#
# MTN25 ent(6º369077*6)+1= 39 ent(3º626388*12)+1 = 44 3944 idem h560 - ?
#     39-20*2 = -1 es decir cuarto (I o III)
#     44-22*2 = 0  es decir cuarto (III o IV) -----------------> h560-III
#
# MTN10 ent(6º369077*12)+1=77 ent(3º626388*24)+1=88 077088 idem h560 - ?
#     77-20*4=-3 es decir col 1 (-3+4)
#     88-22*4= 0 es decir fil 4 (0+4) -------------------------> h560-14 
#
# Some dms / dd examples
#
# Datum:	ETRS89
# Latitud:	43º 46' 7,01" N
# Longitud:	8º 0' 2,86" W
# Huso UTM:	29
# Coord. X:	580 421,36
# Coord. Y:	4 846 659,01
# Altura (m):	0
#
# Datum:	ETRS89
# Latitud:	43,7686146007
# Longitud:	-8,0007934570
# Huso UTM:	29
# Coord. X:	580 421,36
# Coord. Y:	4 846 659,01
# Altura (m):	0
#
# ############################################################################

import re
import sys
from xml.dom import minidom

class MTN:
    """calculates the MTN sheet for the given lat, lon pair or bounds
    """

    #  
    # this origin is set in the doc, but later changes in the
    # same doc. The working one is th set
    #
    # origin MNT grid λ (lon)= - 9º 31’ 15” φ (lat)= 43º 50’ 00”
    # origin_dms = ('''9º 31' 15" W''', '''43º 50' 00" N''')
    # origin.lon = -9.520833333333334
    # origin.lat = 43.833333333333336
    #

    origin_dms = ('''9º 51' 15" W''', '''44º 00' 00" N''')
    origin = type('', (), {})
    origin.lon =-9.854166666666666
    origin.lat = 44.0

    # map from CC (col) FF (fila) to MTN sheet (from the document)
    mtn_from_ccff = { 
        602: 1, 2707: 117, 811: 227, 1014: 337, 3517: 447, 2122: 561, 4026: 672, 1831: 784, 
        1136: 897, 1941: 1009, 702: 2, 2807: 118, 911: 228, 1114: 338, 3617: 448, 2222: 562, 
        4326: 673, 1931: 785, 1236: 898, 2041: 1010, 802: 3, 308: 119, 1011: 229, 1214: 339, 
        1018: 449, 2322: 563, 727: 674, 2031: 786, 1336: 899, 2141: 1011, 503: 6, 408: 120, 
        1111: 230, 1314: 340, 1118: 450, 2422: 564, 827: 675, 2131: 787, 1436: 900, 2241: 1012, 
        603: 7, 508: 121, 1211: 231, 1414: 341, 1218: 451, 2522: 565, 927: 676, 2231: 788, 1536: 901, 
        2341: 1013, 703: 8, 608: 122, 1311: 232, 1514: 342, 1318: 452, 2622: 566, 1027: 677, 2331: 789,
        1636: 902, 2441: 1014, 803: 9, 708: 123, 1411: 233, 1614: 343, 1418: 453, 2722: 567, 1127: 678, 
        2431: 790, 1736: 903, 2541: 1015, 903: 10, 808: 124, 1511: 234, 1714: 344, 1518: 454, 2822: 568, 
        1227: 679, 2531: 791, 1836: 904, 942: 1016, 1003: 11, 908: 125, 1611: 235, 1814: 345, 1618: 455, 
        2922: 569, 1327: 680, 2631: 792, 1936: 905, 1042: 1017, 1103: 12, 1008: 126, 1711: 236, 1914: 346, 
        1718: 456, 3022: 570, 1427: 681, 2731: 793, 2036: 906, 1142: 1018, 1203: 13, 1108: 127, 1811: 237, 
        2014: 347, 1818: 457, 3122: 571, 1527: 682, 2831: 794, 2136: 907, 1242: 1019, 1303: 14, 1208: 128,
        1911: 238, 2114: 348, 1918: 458, 923: 572, 1627: 683, 2931: 795, 2236: 908, 1342: 1020, 1403: 15, 
        1308: 129, 2011: 239, 2214: 349, 2018: 459, 1023: 573, 1727: 684, 3031: 796, 2336: 909, 1442: 1021, 
        1903: 18, 1408: 130, 2111: 240, 2314: 350, 2118: 460, 1123: 574, 1827: 685, 3431: 798, 2436: 910, 
        1542: 1022, 404: 20, 1508: 131, 2211: 241, 2414: 351, 2218: 461, 1223: 575, 1927: 686, 3531: 799, 
        2536: 911, 1642: 1023, 504: 21, 1608: 132, 2311: 242, 2514: 352, 2318: 462, 1323: 576, 2027: 687, 
        832: 800, 2636: 912, 1742: 1024, 604: 22, 1708: 133, 2411: 243, 2614: 353, 2418: 463, 1423: 577, 
        2127: 688, 932: 801, 2736: 913, 1842: 1025, 704: 23, 1808: 134, 2511: 244, 2714: 354, 2518: 464, 
        1523: 578, 2227: 689, 1032: 802, 2836: 914, 1942: 1026, 804: 24, 1908: 135, 2611: 245, 2814: 355, 
        2618: 465, 1623: 579, 2327: 690, 1132: 803, 837: 915, 2042: 1027, 904: 25, 2008: 136, 2711: 246, 
        2914: 356, 2718: 466, 1723: 580, 2427: 691, 1232: 804, 937: 916, 2142: 1028, 1004: 26, 2108: 137, 
        2811: 247, 3014: 357, 2818: 467, 1823: 581, 2527: 692, 1332: 805, 1037: 917, 2242: 1029, 1104: 27, 
        2208: 138, 2911: 248, 3114: 358, 2918: 468, 1923: 582, 2627: 693, 1432: 806, 1137: 918, 2342: 1030, 
        1204: 28, 2308: 139, 3011: 249, 3214: 359, 3018: 469, 2023: 583, 2727: 694, 1532: 807, 1237: 919, 
        2442: 1031, 1304: 29, 2408: 140, 3111: 250, 3314: 360, 3118: 470, 2123: 584, 2827: 695, 1632: 808, 
        1337: 920, 2542: 1032, 1404: 30, 2508: 141, 3211: 251, 3414: 361, 3218: 471, 2223: 585, 2927: 696, 
        1732: 809, 1437: 921, 1143: 1033, 1504: 31, 2608: 142, 3311: 252, 3514: 362, 3318: 472, 2323: 586, 
        3727: 697, 1832: 810, 1537: 922, 1243: 1034, 1604: 32, 2708: 143, 3411: 253, 3614: 363, 3418: 473, 
        2423: 587, 3827: 698, 1932: 811, 1637: 923, 1343: 1035, 1704: 33, 2808: 144, 3511: 254, 3714: 364, 
        919: 474, 2523: 588, 3927: 699, 2032: 812, 1737: 924, 1443: 1036, 1804: 34, 2908: 145, 3611: 255, 
        3814: 365, 1019: 475, 2623: 589, 4027: 700, 2132: 813, 1837: 925, 1543: 1037, 1904: 35, 3008: 146, 
        3711: 256, 3914: 366, 1119: 476, 2723: 590, 828: 701, 2232: 814, 1937: 926, 1643: 1038, 2004: 36, 
        3108: 147, 3811: 257, 1115: 367, 1219: 477, 2823: 591, 928: 702, 2332: 815, 2037: 927, 1743: 1039, 
        2104: 37, 3208: 148, 3911: 258, 1215: 368, 1319: 478, 2923: 592, 1028: 703, 2432: 816, 2137: 928, 
        1843: 1040, 2204: 38, 3308: 149, 4011: 259, 1315: 369, 1419: 479, 3023: 593, 1128: 704, 2532: 817, 
        2237: 929, 1943: 1041, 2304: 39, 3408: 150, 312: 260, 1415: 370, 1519: 480, 3123: 594, 1228: 705, 
        2632: 818, 2337: 930, 2043: 1042, 2404: 40, 309: 151, 412: 261, 1515: 371, 1619: 481, 924: 595, 
        1328: 706, 2732: 819, 2437: 931, 2143: 1043, 2504: 41, 409: 152, 512: 262, 1615: 372, 1719: 482, 
        1024: 596, 1428: 707, 2832: 820, 2537: 932, 2243: 1044, 305: 43, 509: 153, 612: 263, 1715: 373, 
        1819: 483, 1124: 597, 1528: 708, 2932: 821, 2637: 933, 2343: 1045, 405: 44, 609: 154, 712: 264, 
        1815: 374, 1919: 484, 1224: 598, 1628: 709, 3032: 822, 2737: 934, 2443: 1046, 505: 45, 709: 155, 
        812: 265, 1915: 375, 2019: 485, 1324: 599, 1728: 710, 3132: 823, 2837: 935, 1144: 1047, 605: 46, 
        809: 156, 912: 266, 2015: 376, 2119: 486, 1424: 600, 1828: 711, 3432: 824, 838: 936, 1244: 1048, 
        705: 47, 909: 157, 1012: 267, 2115: 377, 2219: 487, 1524: 601, 1928: 712, 3532: 825, 938: 937, 
        1344: 1049, 805: 48, 1009: 158, 1112: 268, 2215: 378, 2319: 488, 1624: 602, 2028: 713, 833: 826, 
        1038: 938, 1444: 1050, 905: 49, 1109: 159, 1212: 269, 2315: 379, 2419: 489, 1724: 603, 2128: 714,
        933: 827, 1138: 939, 1544: 1051, 1005: 50, 1209: 160, 1312: 270, 2415: 380, 2519: 490, 1824: 604, 
        2228: 715, 1033: 828, 1238: 940, 1644: 1052, 1105: 51, 1309: 161, 1412: 271, 2515: 381, 2619: 491, 
        1924: 605, 2328: 716, 1133: 829, 1338: 941, 1744: 1053, 1205: 52, 1409: 162, 1512: 272, 2615: 382, 
        2719: 492, 2024: 606, 2428: 717, 1233: 830, 1438: 942, 1844: 1054, 1305: 53, 1509: 163, 1612: 273, 
        2715: 383, 2819: 493, 2124: 607, 2528: 718, 1333: 831, 1538: 943, 1944: 1055, 1405: 54, 1609: 164, 
        1712: 274, 2815: 384, 2919: 494, 2224: 608, 2628: 719, 1433: 832, 1638: 944, 2044: 1056, 1505: 55, 
        1709: 165, 1812: 275, 2915: 385, 3019: 495, 2324: 609, 2728: 720, 1533: 833, 1738: 945, 2144: 1057, 
        1605: 56, 1809: 166, 1912: 276, 3015: 386, 3119: 496, 2424: 610, 2828: 721, 1633: 834, 1838: 946, 
        2244: 1058, 1705: 57, 1909: 167, 2012: 277, 3115: 387, 3219: 497, 2524: 611, 2928: 722, 1733: 835, 
        1938: 947, 2344: 1059, 1805: 58, 2009: 168, 2112: 278, 3215: 388, 3319: 498, 2624: 612, 3828: 723, 
        1833: 836, 2038: 948, 2444: 1060, 1905: 59, 2109: 169, 2212: 279, 3315: 389, 1020: 500, 2724: 613, 
        3928: 724, 1933: 837, 2138: 949, 1145: 1061, 2005: 60, 2209: 170, 2312: 280, 3415: 390, 1120: 501, 
        2824: 614, 4028: 725, 2033: 838, 2238: 950, 1245: 1062, 2105: 61, 2309: 171, 2412: 281, 3515: 391, 
        1220: 502, 2924: 615, 829: 726, 2133: 839, 2338: 951, 1345: 1063, 2205: 62, 2409: 172, 2512: 282, 
        3615: 392, 1320: 503, 3024: 616, 929: 727, 2233: 840, 2438: 952, 1445: 1064, 2305: 63, 2509: 173, 
        2612: 283, 3715: 393, 1420: 504, 3124: 617, 1029: 728, 2333: 841, 2538: 953, 1545: 1065, 2405: 64, 
        2609: 174, 2712: 284, 3815: 394, 1520: 505, 4224: 618, 1129: 729, 2433: 842, 2638: 954, 1645: 1066, 
        2505: 65, 2709: 175, 2812: 285, 1116: 395, 1620: 506, 4324: 619, 1229: 730, 2533: 843, 2738: 955, 
        1745: 1067, 2605: 66, 2809: 176, 2912: 286, 1216: 396, 1720: 507, 925: 620, 1329: 731, 2633: 844, 
        2838: 956, 1146: 1068, 206: 67, 2909: 177, 3012: 287, 1316: 397, 1820: 508, 1025: 621, 1429: 732, 
        2733: 845, 839: 958, 1246: 1069, 306: 68, 3009: 178, 3112: 288, 1416: 398, 1920: 509, 1125: 622, 
        1529: 733, 2833: 846, 939: 959, 1346: 1070, 406: 69, 3109: 179, 3212: 289, 1516: 399, 2020: 510, 
        1225: 623, 1629: 734, 2933: 847, 1039: 960, 1446: 1071, 506: 70, 3209: 180, 3312: 290, 1616: 400, 
        2120: 511, 1325: 624, 1729: 735, 3033: 848, 1139: 961, 1546: 1072, 606: 71, 3309: 181, 3412: 291, 
        1716: 401, 2220: 512, 1425: 625, 1829: 736, 834: 851, 1239: 962, 1247: 1073, 706: 72, 3409: 182, 
        3512: 292, 1816: 402, 2320: 513, 1525: 626, 1929: 737, 934: 852, 1339: 963, 1347: 1074, 806: 73, 
        3509: 183, 3612: 293, 1916: 403, 2420: 514, 1625: 627, 2029: 738, 1034: 853, 1439: 964, 1447: 1075, 
        906: 74, 310: 184, 3712: 294, 2016: 404, 2520: 515, 1725: 628, 2129: 739, 1134: 854, 1539: 965, 
        1248: 1076, 1006: 75, 410: 185, 3812: 295, 2116: 405, 2620: 516, 1825: 629, 2229: 740, 1234: 855, 
        1639: 966, 1348: 1077, 1106: 76, 510: 186, 3912: 296, 2216: 406, 2720: 517, 1925: 630, 2329: 741, 
        1334: 856, 1739: 967, 1448: 1078, 1206: 77, 610: 187, 4012: 297, 2316: 407, 2820: 518, 2025: 631, 
        2429: 742, 1434: 857, 1839: 968, 1306: 78, 710: 188, 313: 298, 2416: 408, 2920: 519, 2125: 632, 
        2529: 743, 1534: 858, 1939: 969, 1406: 79, 810: 189, 413: 299, 2516: 409, 3020: 520, 2225: 633, 
        2629: 744, 1634: 859, 2039: 970, 1506: 80, 910: 190, 513: 300, 2616: 410, 3120: 521, 2325: 634, 
        2729: 745, 1734: 860, 2139: 971, 1606: 81, 1010: 191, 613: 301, 2716: 411, 3220: 522, 2425: 635,
        2829: 746, 1834: 861, 2239: 972, 1706: 82, 1110: 192, 713: 302, 2816: 412, 3320: 523, 2525: 636, 
        2929: 747, 1934: 862, 2339: 973, 1806: 83, 1210: 193, 813: 303, 2916: 413, 1021: 525, 2625: 637, 
        3929: 748, 2034: 863, 2439: 974, 1906: 84, 1310: 194, 913: 304, 3016: 414, 1121: 526, 2725: 638, 
        930: 750, 2134: 864, 2539: 975, 2006: 85, 1410: 195, 1013: 305, 3116: 415, 1221: 527, 2825: 639, 
        1030: 751, 2234: 865, 2639: 976, 2106: 86, 1510: 196, 1113: 306, 3216: 416, 1321: 528, 2925: 640,
        1130: 752, 2334: 866, 2739: 977, 2206: 87, 1610: 197, 1213: 307, 3316: 417, 1421: 529, 3025: 641, 
        1230: 753, 2434: 867, 2839: 978, 2306: 88, 1710: 198, 1313: 308, 3416: 418, 1521: 530, 3225: 642, 
        1330: 754, 2534: 868, 840: 980, 2406: 89, 1810: 199, 1413: 309, 3516: 419, 1621: 531, 3925: 644, 
        1430: 755, 2634: 869, 940: 981, 2506: 90, 1910: 200, 1513: 310, 3616: 420, 1721: 532, 4025: 645, 
        1530: 756, 2734: 870, 1040: 982, 2606: 91, 2010: 201, 1613: 311, 3716: 421, 1821: 533, 4225: 646, 
        1630: 757, 2834: 871, 1140: 983, 207: 92, 2110: 202, 1713: 312, 1017: 422, 1921: 534, 4325: 647, 
        1730: 758, 2934: 872, 1240: 984, 307: 93, 2210: 203, 1813: 313, 1117: 423, 2021: 535, 926: 648, 
        1830: 759, 835: 873, 1340: 985, 407: 94, 2310: 204, 1913: 314, 1217: 424, 2121: 536, 1026: 649, 
        1930: 760, 935: 874, 1440: 986, 507: 95, 2410: 205, 2013: 315, 1317: 425, 2221: 537, 1126: 650, 
        2030: 761, 1035: 875, 1540: 987, 607: 96, 2510: 206, 2113: 316, 1417: 426, 2321: 538, 1226: 651, 
        2130: 762, 1135: 876, 1640: 988, 707: 97, 2610: 207, 2213: 317, 1517: 427, 2421: 539, 1326: 652, 
        2230: 763, 1235: 877, 1740: 989, 807: 98, 2710: 208, 2313: 318, 1617: 428, 2521: 540, 1426: 653,
        2330: 764, 1335: 878, 1840: 990, 907: 99, 2810: 209, 2413: 319, 1717: 429, 2621: 541, 1526: 654, 
        2430: 765, 1435: 879, 1940: 991, 1007: 100, 2910: 210, 2513: 320, 1817: 430, 2721: 542, 1626: 655, 
        2530: 766, 1535: 880, 2040: 992, 1107: 101, 3010: 211, 2613: 321, 1917: 431, 2821: 543, 1726: 656, 
        2630: 767, 1635: 881, 2140: 993, 1207: 102, 3110: 212, 2713: 322, 2017: 432, 2921: 544, 1826: 657, 
        2730: 768, 1735: 882, 2240: 994, 1307: 103, 3210: 213, 2813: 323, 2117: 433, 3021: 545, 1926: 658, 
        2830: 769, 1835: 883, 2340: 995, 1407: 104, 3310: 214, 2913: 324, 2217: 434, 3121: 546, 2026: 659, 
        2930: 770, 1935: 884, 2440: 996, 1507: 105, 3410: 215, 3013: 325, 2317: 435, 3221: 547, 2126: 660, 
        3030: 771, 2035: 885, 2540: 997, 1607: 106, 3510: 216, 3113: 326, 2417: 436, 1022: 550, 2226: 661, 
        3430: 772, 2135: 886, 841: 998, 1707: 107, 3610: 217, 3213: 327, 2517: 437, 1122: 551, 2326: 662, 
        3530: 773, 2235: 887, 941: 999, 1807: 108, 3710: 218, 3313: 328, 2617: 438, 1222: 552, 2426: 663, 
        931: 775, 2335: 888, 1041: 1000, 1907: 109, 3810: 219, 3413: 329, 2717: 439, 1322: 553, 2526: 664, 
        1031: 776, 2435: 889, 1141: 1001, 2007: 110, 3910: 220, 3513: 330, 2817: 440, 1422: 554, 2626: 665, 
        1131: 777, 2535: 890, 1241: 1002, 2107: 111, 4010: 221, 3613: 331, 2917: 441, 1522: 555, 2726: 666, 
        1231: 778, 2635: 891, 1341: 1003, 2207: 112, 311: 222, 3713: 332, 3017: 442, 1622: 556, 2826: 667, 
        1331: 779, 2735: 892, 1441: 1004, 2307: 113, 411: 223, 3813: 333, 3117: 443, 1722: 557, 2926: 668, 
        1431: 780, 2835: 893, 1541: 1005, 2407: 114, 511: 224, 3913: 334, 3217: 444, 1822: 558, 3026: 669, 
        1531: 781, 2935: 894, 1641: 1006, 2507: 115, 611: 225, 4013: 335, 3317: 445, 1922: 559, 3826: 670, 
        1631: 782, 936: 895, 1741: 1007, 2607: 116, 711: 226, 614: 336, 3417: 446, 2022: 560, 3926: 671, 
        1731: 783, 1036: 896, 1841: 1008
    }


    def dms_to_dd(deg, minutes=0, seconds=0,direction='W'):
        """converts from degree, minutes, seconds, direction to float (standard) degrees
        
        Arguments:
            deg {float} -- degrees
        
        Keyword Arguments:
            minutes {float} -- minutes (default: {0})
            seconds {float} -- seconds (default: {0})
            direction {string} -- N,S,W,E (default: {'W'})
        
        Returns:
            float -- the value in foat format
        """

        ret = (float(deg) + float(minutes)/60 + float(seconds)/(60*60)) * (-1 if direction in ['W', 'S'] else 1)
        return ret

    def dms_to_dd_s(dms):
        """get a degree, minutes seconds string, and return the float (standard) degrees

        Arguments:
            dms {string} -- the string. Like 43º 46' 7.01" N
        
        Returns:
            float -- The float representation
        """
        deg, minutes, seconds, direction = re.split('[^\d\w\.]+', dms)
        deg = re.sub('[°º]','',deg)
        #print(deg,minutes,seconds,direction)
        ret = (float(deg) + float(minutes)/60 + float(seconds)/(60*60)) * (-1 if direction in ['W', 'S'] else 1)
        return ret

    def dd_to_dms(deg, mode='lat'):
        """convert from float to degree, minutes, seconds
        
        Arguments:
            deg {float} -- the value
        
        Keyword Arguments:
            mode {string} -- lat-itude or lon-gitude. For N/S or W/E (default: {'lat'})
        
        Returns:
            tuple (degrees, minutes, seconds, direction) -- the value converted.
        """

        sign = 1 if deg > 0 else -1
        d = int(deg)
        md = abs(deg - d) * 60
        m = int(md)
        sd = (md - m) * 60

        if mode.lower() == 'lat':
            direction = 'N' if sign > 0 else 'S'
        else:
            direction = 'E' if sign > 0 else 'W'

        return (abs(d), m, sd, direction)

    def dd_to_dms_s(deg, mode='lat'):
        """convert from float to degree, minutes, seconds, returns a string
        
        Arguments:
            deg {float} -- the value
        
        Keyword Arguments:
            mode {string} -- lat-itude or lon-gitude. For N/S or W/E (default: {'lat'})
        
        Returns:
            string -- the value converted.
        """
        
        s = '''%dº %d' %3.2f" %s''' % MTN.dd_to_dms(deg, mode)
        return s

    def where(lon,lat):
        """calculates the MTN sheet for the given lon, lat in float format
        
        Arguments:
            lon {float} -- longitude
            lat {float} -- latitude
        
        Returns:
            dict -- dict with the sheets, and the CC (col) FF (fila) code
        """

        col = lon - MTN.origin.lon
        row = MTN.origin.lat - lat

        MTN50 = "%2d%2d" % (int( col * 3) + 1, int(row * 6) + 1)
        MTN25 = "%2d%2d" % (int( col * 6) + 1, int(row * 12) + 1)
        MTN10 = "%3d%03d" % (int( col * 12) + 1, int(row * 24) + 1)

        MTN50,MTN25,MTN10 = map(lambda x: int(x), (MTN50,MTN25, MTN10))

        return { 'MTN50': (MTN50, MTN.mtn_from_ccff[MTN50]), 
                 'MTN25': (MTN25, MTN.mtn_from_ccff[MTN50]),
                 'MTN10': (MTN10, MTN.mtn_from_ccff[MTN50]) }


def read_data(docname='doc.kml'):

    def getNodeText(node):

        nodelist = node.childNodes
        result = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                result.append(node.data)
        return ''.join(result)
    
    doc = minidom.parse(docname)

    folder = doc.getElementsByTagName("Folder")[0]
    folders = folder.getElementsByTagName("Folder")

    count = 0
    for folder in folders:
        for node in folder.childNodes:
            if node.nodeType == node.TEXT_NODE:
                continue
            if node.tagName in ['name', 'open']:
                continue
            if node.nodeType == node.ELEMENT_NODE:
                lat = getNodeText(node.getElementsByTagName('LATITUD')[0])
                lon = getNodeText(node.getElementsByTagName('LONGITUD')[0])
                ref = getNodeText(node.getElementsByTagName('Referencia_MTN50_CF')[0])
                sheet = 0
                if node.getElementsByTagName('CUADRICULA___Hoja_MTN50') != []:
                    sheet = getNodeText(node.getElementsByTagName('CUADRICULA___Hoja_MTN50')[0])
                    if sheet.lower().find('Cuadrícula sin hoja MTN'.lower()) != -1:
                        sheet = 0
                    else:
                        #Cuadrícula de la hoja MTN50: 334
                        sheet = re.search(r'([\d]+)$', sheet)
                        if sheet:
                            sheet = sheet[1]
                
                        else:
                            sheet = 0
                        
                if sheet != 0:
                    print("lat, lon", lat, lon, ref, sheet)
                    count +=1
    
    print(count)


#Las coordenadas geodésicas ETRS89 de dicho origen corresponden a una longitud 
# de -9º 51' 15'' y una latitud de 44º 00' 00''. Quedando definida la esquina sureste con 
# longitud -9º 51' 15'' + (CC/3)º y latitud 44º 00' 00'' -(FF/6)º, y la esquina noroeste restando 20' 
# para la longitud y sumando 10' para la latitud. Las otras dos esquinas se obtienen a partir de éstas.
# EJEMPLO: Cálculo de la esquina Sureste de la hoja MTN50 n.º 559, correspondiente a la columna-fila 19-22 (CC=19, FF=22). 
# Longitud = -9º 51' 15'' + (19/3)º = -3,520833333= -3º 31' 15'' Latitud = 44º 00' 00'' -(22/6)º = 40,33333333 = 40º 20' 00''. 

#s = "1 602 117 2707 227 811 337 1014 447 3517 561 2122 672 4026 784 1831 897 1136 1009 1941 2 702 118 2807 228 911 338 1114 448 3617 562 2222 673 4326 785 1931 898 1236 1010 2041 3 802 119 308 229 1011 339 1214 449 1018 563 2322 674 727 786 2031 899 1336 1011 2141 6 503 120 408 230 1111 340 1314 450 1118 564 2422 675 827 787 2131 900 1436 1012 2241 7 603 121 508 231 1211 341 1414 451 1218 565 2522 676 927 788 2231 901 1536 1013 2341 8 703 122 608 232 1311 342 1514 452 1318 566 2622 677 1027 789 2331 902 1636 1014 2441 9 803 123 708 233 1411 343 1614 453 1418 567 2722 678 1127 790 2431 903 1736 1015 2541 10 903 124 808 234 1511 344 1714 454 1518 568 2822 679 1227 791 2531 904 1836 1016 942 11 1003 125 908 235 1611 345 1814 455 1618 569 2922 680 1327 792 2631 905 1936 1017 1042 12 1103 126 1008 236 1711 346 1914 456 1718 570 3022 681 1427 793 2731 906 2036 1018 1142 13 1203 127 1108 237 1811 347 2014 457 1818 571 3122 682 1527 794 2831 907 2136 1019 1242 14 1303 128 1208 238 1911 348 2114 458 1918 572 923 683 1627 795 2931 908 2236 1020 1342 15 1403 129 1308 239 2011 349 2214 459 2018 573 1023 684 1727 796 3031 909 2336 1021 1442 18 1903 130 1408 240 2111 350 2314 460 2118 574 1123 685 1827 798 3431 910 2436 1022 1542 20 404 131 1508 241 2211 351 2414 461 2218 575 1223 686 1927 799 3531 911 2536 1023 1642 21 504 132 1608 242 2311 352 2514 462 2318 576 1323 687 2027 800 832 912 2636 1024 1742 22 604 133 1708 243 2411 353 2614 463 2418 577 1423 688 2127 801 932 913 2736 1025 1842 23 704 134 1808 244 2511 354 2714 464 2518 578 1523 689 2227 802 1032 914 2836 1026 1942 24 804 135 1908 245 2611 355 2814 465 2618 579 1623 690 2327 803 1132 915 837 1027 2042 25 904 136 2008 246 2711 356 2914 466 2718 580 1723 691 2427 804 1232 916 937 1028 2142 26 1004 137 2108 247 2811 357 3014 467 2818 581 1823 692 2527 805 1332 917 1037 1029 2242 27 1104 138 2208 248 2911 358 3114 468 2918 582 1923 693 2627 806 1432 918 1137 1030 2342 28 1204 139 2308 249 3011 359 3214 469 3018 583 2023 694 2727 807 1532 919 1237 1031 2442 29 1304 140 2408 250 3111 360 3314 470 3118 584 2123 695 2827 808 1632 920 1337 1032 2542 30 1404 141 2508 251 3211 361 3414 471 3218 585 2223 696 2927 809 1732 921 1437 1033 1143 31 1504 142 2608 252 3311 362 3514 472 3318 586 2323 697 3727 810 1832 922 1537 1034 1243 32 1604 143 2708 253 3411 363 3614 473 3418 587 2423 698 3827 811 1932 923 1637 1035 1343 33 1704 144 2808 254 3511 364 3714 474 919 588 2523 699 3927 812 2032 924 1737 1036 1443 34 1804 145 2908 255 3611 365 3814 475 1019 589 2623 700 4027 813 2132 925 1837 1037 1543 35 1904 146 3008 256 3711 366 3914 476 1119 590 2723 701 828 814 2232 926 1937 1038 1643 36 2004 147 3108 257 3811 367 1115 477 1219 591 2823 702 928 815 2332 927 2037 1039 1743 37 2104 148 3208 258 3911 368 1215 478 1319 592 2923 703 1028 816 2432 928 2137 1040 1843 38 2204 149 3308 259 4011 369 1315 479 1419 593 3023 704 1128 817 2532 929 2237 1041 1943 39 2304 150 3408 260 312 370 1415 480 1519 594 3123 705 1228 818 2632 930 2337 1042 2043 40 2404 151 309 261 412 371 1515 481 1619 595 924 706 1328 819 2732 931 2437 1043 2143 41 2504 152 409 262 512 372 1615 482 1719 596 1024 707 1428 820 2832 932 2537 1044 2243 43 305 153 509 263 612 373 1715 483 1819 597 1124 708 1528 821 2932 933 2637 1045 2343 44 405 154 609 264 712 374 1815 484 1919 598 1224 709 1628 822 3032 934 2737 1046 2443 45 505 155 709 265 812 375 1915 485 2019 599 1324 710 1728 823 3132 935 2837 1047 1144 46 605 156 809 266 912 376 2015 486 2119 600 1424 711 1828 824 3432 936 838 1048 1244 47 705 157 909 267 1012 377 2115 487 2219 601 1524 712 1928 825 3532 937 938 1049 1344 48 805 158 1009 268 1112 378 2215 488 2319 602 1624 713 2028 826 833 938 1038 1050 1444 49 905 159 1109 269 1212 379 2315 489 2419 603 1724 714 2128 827 933 939 1138 1051 1544 50 1005 160 1209 270 1312 380 2415 490 2519 604 1824 715 2228 828 1033 940 1238 1052 1644 51 1105 161 1309 271 1412 381 2515 491 2619 605 1924 716 2328 829 1133 941 1338 1053 1744 52 1205 162 1409 272 1512 382 2615 492 2719 606 2024 717 2428 830 1233 942 1438 1054 1844 53 1305 163 1509 273 1612 383 2715 493 2819 607 2124 718 2528 831 1333 943 1538 1055 1944 54 1405 164 1609 274 1712 384 2815 494 2919 608 2224 719 2628 832 1433 944 1638 1056 2044 55 1505 165 1709 275 1812 385 2915 495 3019 609 2324 720 2728 833 1533 945 1738 1057 2144 56 1605 166 1809 276 1912 386 3015 496 3119 610 2424 721 2828 834 1633 946 1838 1058 2244 57 1705 167 1909 277 2012 387 3115 497 3219 611 2524 722 2928 835 1733 947 1938 1059 2344 58 1805 168 2009 278 2112 388 3215 498 3319 612 2624 723 3828 836 1833 948 2038 1060 2444 59 1905 169 2109 279 2212 389 3315 500 1020 613 2724 724 3928 837 1933 949 2138 1061 1145 60 2005 170 2209 280 2312 390 3415 501 1120 614 2824 725 4028 838 2033 950 2238 1062 1245 61 2105 171 2309 281 2412 391 3515 502 1220 615 2924 726 829 839 2133 951 2338 1063 1345 62 2205 172 2409 282 2512 392 3615 503 1320 616 3024 727 929 840 2233 952 2438 1064 1445 63 2305 173 2509 283 2612 393 3715 504 1420 617 3124 728 1029 841 2333 953 2538 1065 1545 64 2405 174 2609 284 2712 394 3815 505 1520 618 4224 729 1129 842 2433 954 2638 1066 1645 65 2505 175 2709 285 2812 395 1116 506 1620 619 4324 730 1229 843 2533 955 2738 1067 1745 66 2605 176 2809 286 2912 396 1216 507 1720 620 925 731 1329 844 2633 956 2838 1068 1146 67 206 177 2909 287 3012 397 1316 508 1820 621 1025 732 1429 845 2733 958 839 1069 1246 68 306 178 3009 288 3112 398 1416 509 1920 622 1125 733 1529 846 2833 959 939 1070 1346 69 406 179 3109 289 3212 399 1516 510 2020 623 1225 734 1629 847 2933 960 1039 1071 1446 70 506 180 3209 290 3312 400 1616 511 2120 624 1325 735 1729 848 3033 961 1139 1072 1546 71 606 181 3309 291 3412 401 1716 512 2220 625 1425 736 1829 851 834 962 1239 1073 1247 72 706 182 3409 292 3512 402 1816 513 2320 626 1525 737 1929 852 934 963 1339 1074 1347 73 806 183 3509 293 3612 403 1916 514 2420 627 1625 738 2029 853 1034 964 1439 1075 1447 74 906 184 310 294 3712 404 2016 515 2520 628 1725 739 2129 854 1134 965 1539 1076 1248 75 1006 185 410 295 3812 405 2116 516 2620 629 1825 740 2229 855 1234 966 1639 1077 1348 76 1106 186 510 296 3912 406 2216 517 2720 630 1925 741 2329 856 1334 967 1739 1078 1448 77 1206 187 610 297 4012 407 2316 518 2820 631 2025 742 2429 857 1434 968 1839 78 1306 188 710 298 313 408 2416 519 2920 632 2125 743 2529 858 1534 969 1939 79 1406 189 810 299 413 409 2516 520 3020 633 2225 744 2629 859 1634 970 2039 80 1506 190 910 300 513 410 2616 521 3120 634 2325 745 2729 860 1734 971 2139 81 1606 191 1010 301 613 411 2716 522 3220 635 2425 746 2829 861 1834 972 2239 82 1706 192 1110 302 713 412 2816 523 3320 636 2525 747 2929 862 1934 973 2339 83 1806 193 1210 303 813 413 2916 525 1021 637 2625 748 3929 863 2034 974 2439 84 1906 194 1310 304 913 414 3016 526 1121 638 2725 750 930 864 2134 975 2539 85 2006 195 1410 305 1013 415 3116 527 1221 639 2825 751 1030 865 2234 976 2639 86 2106 196 1510 306 1113 416 3216 528 1321 640 2925 752 1130 866 2334 977 2739 87 2206 197 1610 307 1213 417 3316 529 1421 641 3025 753 1230 867 2434 978 2839 88 2306 198 1710 308 1313 418 3416 530 1521 642 3225 754 1330 868 2534 980 840 89 2406 199 1810 309 1413 419 3516 531 1621 644 3925 755 1430 869 2634 981 940 90 2506 200 1910 310 1513 420 3616 532 1721 645 4025 756 1530 870 2734 982 1040 91 2606 201 2010 311 1613 421 3716 533 1821 646 4225 757 1630 871 2834 983 1140 92 207 202 2110 312 1713 422 1017 534 1921 647 4325 758 1730 872 2934 984 1240 93 307 203 2210 313 1813 423 1117 535 2021 648 926 759 1830 873 835 985 1340 94 407 204 2310 314 1913 424 1217 536 2121 649 1026 760 1930 874 935 986 1440 95 507 205 2410 315 2013 425 1317 537 2221 650 1126 761 2030 875 1035 987 1540 96 607 206 2510 316 2113 426 1417 538 2321 651 1226 762 2130 876 1135 988 1640 97 707 207 2610 317 2213 427 1517 539 2421 652 1326 763 2230 877 1235 989 1740 98 807 208 2710 318 2313 428 1617 540 2521 653 1426 764 2330 878 1335 990 1840 99 907 209 2810 319 2413 429 1717 541 2621 654 1526 765 2430 879 1435 991 1940 100 1007 210 2910 320 2513 430 1817 542 2721 655 1626 766 2530 880 1535 992 2040 101 1107 211 3010 321 2613 431 1917 543 2821 656 1726 767 2630 881 1635 993 2140 102 1207 212 3110 322 2713 432 2017 544 2921 657 1826 768 2730 882 1735 994 2240 103 1307 213 3210 323 2813 433 2117 545 3021 658 1926 769 2830 883 1835 995 2340 104 1407 214 3310 324 2913 434 2217 546 3121 659 2026 770 2930 884 1935 996 2440 105 1507 215 3410 325 3013 435 2317 547 3221 660 2126 771 3030 885 2035 997 2540 106 1607 216 3510 326 3113 436 2417 550 1022 661 2226 772 3430 886 2135 998 841 107 1707 217 3610 327 3213 437 2517 551 1122 662 2326 773 3530 887 2235 999 941 108 1807 218 3710 328 3313 438 2617 552 1222 663 2426 775 931 888 2335 1000 1041 109 1907 219 3810 329 3413 439 2717 553 1322 664 2526 776 1031 889 2435 1001 1141 110 2007 220 3910 330 3513 440 2817 554 1422 665 2626 777 1131 890 2535 1002 1241 111 2107 221 4010 331 3613 441 2917 555 1522 666 2726 778 1231 891 2635 1003 1341 112 2207 222 311 332 3713 442 3017 556 1622 667 2826 779 1331 892 2735 1004 1441 113 2307 223 411 333 3813 443 3117 557 1722 668 2926 780 1431 893 2835 1005 1541 114 2407 224 511 334 3913 444 3217 558 1822 669 3026 781 1531 894 2935 1006 1641 115 2507 225 611 335 4013 445 3317 559 1922 670 3826 782 1631 895 936 1007 1741 116 2607 226 711 336 614 446 3417 560 2022 671 3926 783 1731 896 1036 1008 1841"



from itertools import islice

def group(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())

if __name__ == "__main__":
    lat = '''43º 46' 7.01" N''' # 43.768613888888886
    lat = '''8º 0' 2.86" W''' # -8.000794444444445



    print(MTN.dms_to_dd_s(lat))
    print(MTN.dd_to_dms(-8.000794444444445,mode='lon'))

    print(MTN.dms_to_dd_s(MTN.origin_dms[0]))
    print(MTN.dms_to_dd_s(MTN.origin_dms[1]))

    #ϕ=40º 22' 25.00" λ=-(3º 29' 06.32")
    #print(MTN.dms_to_dd_s('''40º 22' 25.00" N'''))
    #print(MTN.dms_to_dd_s('''3º 29' 06.32" W'''))

    print(MTN.where(-3.485088888888889,40.37361111111111))  
    print(MTN.where(float(sys.argv[1]),float(sys.argv[2])))

    # sheet generation
    #print("---")
    #read_data()
    #list = s.split(" ")
    #print("mtn_from_ccff = {")
    #r = []
    #for i in group(list,2):
    #    r.append( "%s: %s" % (i[1], i[0]))
    #print(", ".join(r))
    #print("}")
