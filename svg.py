import h3graph


def main():
    graph = h3graph.Graph()
    graph.load('got.graphml')
    graph.define_node_positions()
    graph.update_graph()
    graph.draw()


if __name__ == '__main__':
    main()
