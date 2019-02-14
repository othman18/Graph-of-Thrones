import math

import h3graph

POS_SCALE = 3.543307
radius = 400 * POS_SCALE

inner_circle_radius = 350 * POS_SCALE


def calc_positions(count, doc_width, doc_height, r = None):

    if r is None:
        r = radius

    center_x = doc_width / 2 * POS_SCALE
    center_y = doc_height / 2 * POS_SCALE

    positions = []

    for i in range(0, count):
        degrees = (360.0 / count) * i

        radiant = (degrees / 360.0) * (2.0*math.pi)

        x = (r * math.cos(radiant)) + center_x
        y = (r * math.sin(radiant)) + center_y

        print(str(x) + ", " + str(y))

        positions.append((x, y))

    return positions


def calc_inner_circle_positions(count, doc_width, doc_height):
    center_x = doc_width / 2 * POS_SCALE
    center_y = doc_height / 2 * POS_SCALE

    positions = []

    for i in range(0, count):
        degrees = (360.0 / count) * i

        radiant = (degrees / 360.0) * (2.0*math.pi)

        x = (inner_circle_radius * math.cos(radiant)) + center_x
        y = (inner_circle_radius * math.sin(radiant)) + center_y

        print(str(x) + ", " + str(y))

        positions.append((x, y))

    return positions


# returns the nearest position from the given positions to x,y
def get_nearest_position(positions, x, y):
    nearest_posistion = None
    nearest_distance = None

    for position in positions:
        if nearest_posistion is None:
            nearest_posistion = positions
            nearest_distance = distance(position, (x,y))
        else:
            dist = distance(position, (x,y))
            if dist < nearest_distance:
                nearest_posistion = position
                nearest_distance = dist

    return nearest_posistion


# calculates a distance without using the root
def distance(p1, p2):
    return math.pow(p1[0] - p2[0], 2) + math.pow(p1[1] - p2[1], 2)


def real_distance(p1, p2):
    return math.sqrt(distance(p1, p2))


def fx_with_limit(limit, x, threshhold = 50):
    return limit * x / (x+threshhold)


def calc_outer_bezier_focus(center, n1, n2):

    # Vektor zwische n1 und n2
    v = (n1[0] - n2[0], n1[1] - n2[1])

    # Mittelpunkt zwischen n1 und n2
    middle_x = n2[0] + (v[0]/2)
    middle_y = n2[1] + (v[1]/2)

    # Vector zwischen Mittelpunkt und (Mittelpunkt von n1 und n2)
    d_x = middle_x - center[0]
    d_y = middle_y - center[1]

    dist = distance(n1, n2)

    # Skalieren
    b = dist/radius             # Faktor für Außenbogen
    fancy_var = b + radius
    vector_length = real_distance(center, (middle_x, middle_y))
    strength = fancy_var / vector_length

    n_x = center[0] + (strength * d_x)
    n_y = center[1] + (strength * d_y)

    if n_x > (h3graph.draw.WIDTH):
        n_x = h3graph.draw.WIDTH

    if (n_y < 0):
        n_y = -200
    elif (n_y > h3graph.draw.HEIGHT):
        n_y = h3graph.draw.HEIGHT + 300

    return ( n_x, n_y )


def calc_text_path(x, y):
    center_x = h3graph.draw.WIDTH/2
    center_y = h3graph.draw.HEIGHT/2

    d_x = center_x - x
    d_y = center_y - y

    start = (x-d_x/20, y-d_y/20)
    end = (x-d_x/5, y-d_y/5)

    # gradient = d_y/d_x
    # start = ((x + 50), (y + 50 * gradient))
    # end = ((x + 200), (y + 200 * gradient))

    return (start, end)