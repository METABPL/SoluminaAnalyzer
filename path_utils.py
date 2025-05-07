from importer.class_model import *

def enumerate_from(node, path, all_paths, visited, end_node_id):
    path.append(node)
    id = node.bplElementUUID
    if id == end_node_id:
        all_paths.append(path[:])
        return

    if isinstance(node, Parallel) and len(node.prevs) > 1:
        return

    if id in visited:
        all_paths.append(path[:])
        return

    visited.add(id)

    if isinstance(node, Process) or isinstance(node, SubProcess):
        start_node = None
        for child in node.bplElements:
            if isinstance(child, StartEvent):
                start_node = child
            elif end_node_id is None and isinstance(child, EndEvent):
                end_node_id = child.bplElementUUID
        if start_node is not None:
            enumerate_from(start_node, path, all_paths, visited, end_node_id)
    if isinstance(node, Parallel) and len(node.nexts) > 1:
        end_par = None
        for par_next in node.nexts:
            enumerate_from(par_next, path, all_paths, visited, end_node_id)
            end_par = path[-1]
            path.pop()
        path.append(end_par)
        if len(end_par.nexts) == 1:
            enumerate_from(end_par.nexts[0], path, all_paths, visited, end_node_id)
    elif isinstance(node, Parallel):
        print("????")
    elif isinstance(node, Exclusive):
        for exc_next in node.nexts:
            enumerate_from(exc_next, path[:], all_paths, visited.copy(), end_node_id)
    elif isinstance(node, ConnectionBase):
        path.pop()
        enumerate_from(node.toNode, path, all_paths, visited, end_node_id)
        return
    elif isinstance(node, BPLElement):
        if len(node.nexts) == 1:
            enumerate_from(node.nexts[0], path, all_paths, visited, end_node_id)
        elif len(node.prevs) > 1:
            print("Non-gateway node of type {} has more than one nexts".format(
                type(node).__name__))

def enumerate_paths(start):
    visited = set()
    all_paths = []
    path = []
    enumerate_from(start, path, all_paths, visited, None)
    return all_paths

def enumerate_all_nodes(node, nodes, visited):
    id = node.bplElementUUID
    if id in visited:
        return

    visited.add(id)
    for elem in node.bplElements:
        enumerate_all_nodes(elem, nodes, visited)

def enumerate_all(start):
    visited = set()
    nodes = []
    enumerate_all_nodes(start, nodes, visited)