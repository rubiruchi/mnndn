def dijkstra(topo, src):
    """Run Dijkstra's algorithm on a topology.
       returns dict(dst=( distance, path ))"""

    Q = set()
    dist = dict()
    prev = dict()

    for v in topo.nodes():
        dist[v] = float('inf')
        prev[v] = None
        Q.add(v)

    dist[src] = 0

    while len(Q) > 0:
        u = min(Q, key=lambda v:dist[v])
        Q.remove(u)

        for v in [ vv for vv in Q if (vv in topo.g.edge[u].keys()) and (vv in Q) ]:
            alt = dist[u] + topo.linkInfo(u, v).get('cost', 10)
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u

    paths = dict()
    for dst in topo.nodes():
        path = [ dst ]
        while path[0] != src:
            path.insert(0, prev[path[0]])
        paths[dst] = ( dist[dst], path )
    return paths
