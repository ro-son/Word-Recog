from flask import Flask, render_template, request, jsonify
import math
import templateLibrary

app = Flask(__name__)


@app.route('/')
def recognize():
    return render_template('recognize.html')


@app.route('/decipher', methods=["POST", "GET"])
def decipher():
    if request.method == 'POST':
        gesture = request.get_json(force=True)
        result = recommend(gesture, templateLibrary.palm_os)
        return jsonify(result)
    return render_template('recognize.html')


# --- DEFINITIONS ---
# A Point is a [Num Num]

# A Gesture is an array of [Num Num]

# A BoundingBox (BB) is a [Point Point]
# requires: the coordinate values in the first point are less than or equal to
#             the respective values in the second point

# A TemplateLibrary (TL) is an array of [String Gesture]
# requires: the list is non-empty
#           each String key is unqiue
#           each Gesture value is not both vertical and horizontal
# -------------------

# produces the x-coordinate of p
def x_coord(p):
    return p[0]


# produces the y-coordinate of p
def y_coord(p):
    return p[1]


# offsets the x-coordinate and y-coordinate of each Point in g
# by x_offset and y_offset, respectively
def translate(g, x_offset, y_offset):
    for i in g:
        i[0] += x_offset
        i[1] += y_offset


# scales the x-coordinate and y-coordinate of each Point in g
# by x_scale and y_scale, respectively
def scale(g, x_scale, y_scale):
    for i in g:
        i[0] *= x_scale
        i[1] *= y_scale


# produces the BoundingBox of g
def get_b_box(g):
    minx = x_coord(g[0])
    maxx = x_coord(g[0])
    miny = y_coord(g[0])
    maxy = y_coord(g[0])

    for i in g:
        if x_coord(i) < minx:
            minx = x_coord(i)
        if x_coord(i) > maxx:
            maxx = x_coord(i)
        if y_coord(i) < miny:
            miny = y_coord(i)
        if y_coord(i) > maxy:
            maxy = y_coord(i)

    return [[minx, miny], [maxx, maxy]]


# produces the distance between a and b
def distance(a, b):
    return math.sqrt((x_coord(a) - x_coord(b)) ** 2 + (y_coord(a) - y_coord(b)) ** 2)


# produces the length of g
def gesture_length(g):
    length = 0
    for i in range(1, len(g)):
        length += distance(g[i - 1], g[i])
    return length


# produces a Gesture where each Point is from g and indexed by one element of num_list
def get_points(g, num_list):
    new_gesture = []
    for i in num_list:
        new_gesture.append(g[i])
    return new_gesture


# produces a sampling of ten points from g, the first, n/9th, 2n/9th, 3n/9th,
# and so on until the last point
def ten_sample(g):
    return get_points(g, [0,
                          math.floor(len(g) / 9.0),
                          math.floor(2 * len(g) / 9.0),
                          math.floor(3 * len(g) / 9.0),
                          math.floor(4 * len(g) / 9.0),
                          math.floor(5 * len(g) / 9.0),
                          math.floor(6 * len(g) / 9.0),
                          math.floor(7 * len(g) / 9.0),
                          math.floor(8 * len(g) / 9.0),
                          len(g) - 1])


# moves g to (0, 0) and scales it by (x_scale)x(y_scale)
def move_and_scale(g, bounding_box, x_scale, y_scale):
    translate(g, 0 - x_coord(bounding_box[0]), 0 - y_coord(bounding_box[0]))
    scale(g, x_scale, y_scale)


# normalizes g to (0,0) and a standard size
def normalize(g):
    bounding_box = get_b_box(g)
    if width_b_box(bounding_box) < 30:
        move_and_scale(g, bounding_box, 1,
                       200.0 / height_b_box(bounding_box))
    elif height_b_box(bounding_box) < 30:
        move_and_scale(g, bounding_box,
                       200.0 / width_b_box(bounding_box), 1)
    else:
        move_and_scale(g, bounding_box,
                       200.0 / width_b_box(bounding_box),
                       200.0 / height_b_box(bounding_box))


# produces the width of b_box
def width_b_box(b_box):
    return max(1, x_coord(b_box[1]) - x_coord(b_box[0]))


# produces the height of b_box
def height_b_box(b_box):
    return max(1, y_coord(b_box[1]) - y_coord(b_box[0]))


# produces the average distance between points in sub-sampled g1 and g2
# after sub-sampling them with 10 points
def geometric_10match(g1, g2):
    g1 = ten_sample(g1)
    g2 = ten_sample(g2)
    normalize(g1)
    normalize(g2)
    return avg_dist(g1, g2)


# produces the average distance between points in g1 and g2
def avg_dist(g1, g2):
    if len(g1) == 0:
        return 0
    else:
        length = 0
        for i in range(0, len(g1)):
            length += distance(g1[i], g2[i])
        return 1.0 * length / len(g1)


def recommend(candidate, template_library):
    best_rec_so_far = template_library[0][0]
    best_match_value = geometric_10match(candidate, template_library[0][1])

    for i in range(1, len(template_library)):
        if geometric_10match(candidate, template_library[i][1]) < best_match_value:
            best_rec_so_far = template_library[i][0]
            best_match_value = geometric_10match(candidate, template_library[i][1])

    return best_rec_so_far


if __name__ == '__main__':
    app.run()
