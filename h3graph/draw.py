import os
import base64
import svgwrite
import h3graph.calc as calc

from svgwrite.shapes import Circle, Line
from svgwrite.container import Group
from svgwrite.image import Image
from svgwrite.path import Path
from svgwrite.pattern import Pattern
from svgwrite.text import Text
from svgwrite.text import TextPath
from svgwrite.gradients import RadialGradient

NO_PARENTS = False
NO_SIBLINGS = False
EXPERIMENTAL = False
SCALE = 20
POS_SCALE = 3.543307
HEIGHT_IN_MM = 1189
WIDTH_IN_MM = 841
WIDTH = WIDTH_IN_MM * POS_SCALE
HEIGHT = HEIGHT_IN_MM * POS_SCALE
NODE_RADIUS = 40
OFFSET_Y = 0
OFFSET_X = (WIDTH - (2 * 400 * POS_SCALE)) / 2 + 20   # current circle radius = 400 * POS_SCALE --> (WIDTH - (2*400*POS_SCALE)) / 2
ROOT_PATH_IMAGES = os.path.join('.', 'assets', 'images', 'persons', '')


def draw_name(drawing, x, y, node):
    name = getattr(node, "name", None)
    if name is not None:
        drawing.add(Text(name, insert=(x, y + NODE_RADIUS + SCALE), text_anchor="middle"))

        if EXPERIMENTAL:
            (start, end) = calc.calc_text_path(x, y)

            text_anchor = "text-anchor: start"

            if start[0] < WIDTH/2:
                tmp = start
                start = end
                end = tmp
                text_anchor = "text-anchor: end"

            path_string = "M {} {} L {} {}".format(start[0], start[1], end[0], end[1])
            p = Path(d=path_string)

            tp = TextPath(path=p, text=name, style=text_anchor)

            # TextPath has to be child of Text
            text = svgwrite.text.Text("")
            text.add(tp)
            drawing.add(p)
            drawing.add(text)


def draw_house(drawing, x, y, node):
    house = getattr(node, "house-birth", None)
    if house is not None:
        drawing.add(Text(house, insert=(x, y + NODE_RADIUS + 2 * SCALE), text_anchor="middle"))


def draw_death(drawing, x, y, node, death_symbol):
    status = getattr(node, "status", None)
    if status is not None:
        if status == "Deceased":
            u = drawing.use(death_symbol, insert=(x + NODE_RADIUS + 10, y - 20), size=(10, 20))
            drawing.add(u)


def load_styling(drawing, filename):
    with open(filename, 'r') as f:
        css_string = f.read()    # .replace('\n', '')
        drawing.defs.add(drawing.style(css_string))


def load_font_css(drawing, font_css_path):
    # the font has to be base64 encoded in css file
    with open(font_css_path, 'r') as f:
        css_string = f.read()    # .replace('\n', '')
        drawing.defs.add(drawing.style(css_string))


def prepare_character_images(drawing):
    # Load images base64 encoded to embed into svg file
    character_images = dict()

    for index in range(0, 84):
        p = Pattern(x=0, y=0, width="100%", height="100%", viewBox="0 0 512 512")
        image_path = ROOT_PATH_IMAGES + str(index) + ".jpeg"

        # Loading the image an convert it to base64 to integrate it directly
        # into the graphic.
        base64_prefix_href = "data:image/jpeg;base64,"
        with open(image_path, 'rb') as image:
            base64_encoded_string = base64.standard_b64encode(image.read())
        href_base64_img = base64_prefix_href + base64_encoded_string.decode('utf-8')

        i = Image(href=href_base64_img, x="0%", y="0%", width=512, height=512)
        p.add(i)
        drawing.defs.add(p)
        character_images[index] = p

    return character_images


def create_arrow_marker(drawing):
    # ARROW MARKER
    # Creating a viewport for the marker.
    # Each viewport has a distance "SCALE" to the center of the node.
    arrow_marker = drawing.marker(
        refX=50, refY=5, orient="auto", markerWidth=10 + NODE_RADIUS, markerHeight=10, markerUnits="userSpaceOnUse")
    arrow_marker.add(drawing.path("M 0 0 L 10 5 L 0 10 z"))  # Draws an arrow as a marker
    # Adds the marker to the def section (invisible)
    drawing.defs.add(arrow_marker)
    return arrow_marker


def load_death_symbol(drawing):
    # DEATH SYMBOL
    death_symbol = Group()
    death_symbol.add(Path(id="death", d="M 10 0 L 10 40 M 0 12 L 20 12", stroke_width="5"))
    drawing.defs.add(death_symbol)
    return death_symbol


def draw_background(drawing):

    rad = RadialGradient(center=("50%","50%"), r="50%", focal=("50%", "50%"))
    rad.add_stop_color(offset="0%", color="rgb(170,170,170)", opacity="1")
    rad.add_stop_color(offset="90%", color="rgb(0,0,0)", opacity="1")
    drawing.defs.add(rad)

    size = max(WIDTH, HEIGHT) / 1.25

    c = Circle(center=(WIDTH/2, HEIGHT/2), r=size, fill=rad.get_paint_server())

    drawing.add(c)
    # center = (WIDTH/2, HEIGHT/2)
    # gradient = RadialGradient(center, WIDTH/1.5)


def draw_graph(graph):
    # Draws the graph by creating a document, loading css & images, and inserting edges and nodes

    # # Create a document

    drawing = svgwrite.Drawing(filename="res.svg", size=('%dmm' %WIDTH_IN_MM, '%dmm' %HEIGHT_IN_MM))

    # Load styling
    load_styling(drawing, "assets/css/svg.css")
    load_font_css(drawing, "assets/css/got-font.css")

    draw_background(drawing)
    drawing.add(Text("Game  of  Thrones", insert=(WIDTH/2 + 50, 300), class_="headline"))

    # Load arrow marker for directed edges
    arrow_marker = create_arrow_marker(drawing)

    # Load cross for dead characters
    death_symbol = load_death_symbol(drawing)

    # load background images for nodes
    character_images = prepare_character_images(drawing)

    # draw edges
    for e in graph.edges:
        start = (OFFSET_X + e.sourceNode.x, OFFSET_Y + e.sourceNode.y)
        end = (OFFSET_X + e.targetNode.x, OFFSET_Y + e.targetNode.y)

        single_edge_nodes = graph.get_single_edge_nodes()

        if e.sourceNode in single_edge_nodes or e.targetNode in single_edge_nodes:
            line = Line(start=start, end=end)

            hasattr(e, "relation")
            relation = e.get("relation")
            if relation is not None:
                line["class"] = relation

            if e.directed:
                line["marker-end"] = arrow_marker.get_funciri()

            drawing.add(line)
        else:
            # use a bezier
            center_x =  WIDTH / 2
            center_y = HEIGHT / 2

            # calculates the avg position of the center of the graph, start and end point
            avg_x = int((center_x + start[0] + end[0]) / 3)
            avg_y = int((center_y + start[1] + end[1]) / 3)

            p1 = avg_x
            p2 = avg_y

            if e.get("relation") == "father" or e.get("relation") == "mother":
                if NO_PARENTS:
                    continue

            # trying to get sibling relations edges to the outer of the circle...
            if e.get("relation") == "sibling" or e.get("relation") == "father" or e.get("relation") == "mother":
                if NO_SIBLINGS:
                    continue

                node_distance = calc.real_distance(start, end)
                if node_distance < (500 * POS_SCALE):  # this is a distance threshold
                    (p1, p2) = calc.calc_outer_bezier_focus((center_x, center_y), (start[0], start[1]), (end[0], end[1]))

            path_string = "M {} {} Q {} {} {} {}".format(start[0], start[1], p1, p2, end[0], end[1])
            path = Path(d=path_string)
            relation = e.get("relation")
            if relation is not None:
                path["class"] = relation

            if e.score_relevance(graph.max_edge_count, graph.median_edge_count) > 0:
                path["class"] = path["class"] + " HiRel"

            if e.directed:
                path["marker-end"] = arrow_marker.get_funciri()

            drawing.add(path)

    # draw nodes
    for n in graph.nodes:
        x = OFFSET_X + n.x  # * POS_SCALE
        y = OFFSET_Y + n.y  # * POS_SCALE
        f = character_images.get(n.id)
        if f is not None:
            c = Circle(center=(x, y), r=NODE_RADIUS, fill=f.get_paint_server())
        else:
            c = Circle(center=(x, y), r=NODE_RADIUS, fill="green")  # , fill_opacity="0.4")

        drawing.add(c)

        draw_death(drawing, x, y, n, death_symbol)
        draw_name(drawing, x, y, n)
        draw_house(drawing, x, y, n)

    # save the svg file
    drawing.save()
