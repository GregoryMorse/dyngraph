def d(x, y, nodeweight): return nodeweight[y] #infinity for walls
def hEuclidean(x, goal):
    return abs(x[0] - goal[0]) ** 2 + abs(x[1] - goal[1]) ** 2
def hManhattan(x, goal):
    return abs(x[0] - goal[0]) + abs(x[1] - goal[1])
def reconstruct_path(cameFrom, current):
    total_path = current
    while current in cameFrom:
        current = cameFrom[current]
        total_path.append(current)
    return total_path.reverse()
def A_star(start, goal, h, d, g, coord, nodeweight):
    openSet = {start}
    cameFrom = {}
    gScore = {n: None for n in g}
    gScore[start] = 0
    fScore = {n: None for n in g}
    fScore[start] = h(coord[start], coord[goal])
    while len(openSet) != 0:
        nonInf = list(filter(lambda n: not fScore[n] is None, openSet))        
        current = min(nonInf, key=lambda n: fScore[n]) if len(nonInf) != 0 else next(iter(openSet))
        if current == goal:
            return reconstruct_path(cameFrom, current)
        openSet.remove(current)
        for neighbor in g[current]:
            tentative_gScore = None if gScore[current] is None or d(coord[current], coord[neighbor], nodeweight) is None else gScore[current] + d(coord[current], coord[neighbor], nodeweight)
            if tentative_gScore < gScore[neighbor]:
                cameFrom[neighbor] = current
                gScore[neighbor] = tentative_gScore
                fScore[neighbor] = None if tentative_gScore is None else tentative_gScore + h(coord[neighbor], coord[goal])
                if neighbor not in openSet:
                    openSet.add(neighbor)
def make_grid(size):
    g = {} #adjacency list sizeXsize index -> neighbor indexes
    coord = {} #map node -> x, y coordinates
    for i in range(size):
        for j in range(size):
            n = len(g)
            g[n] = []
            if i != 0: g[n].append((i - 1) * size + j)
            if j != 0: g[n].append(i * size + j - 1)
            if i != size-1: g[n].append((i + 1) * size + j)
            if j != size-1: g[n].append(i * size + j + 1)
            coord[n] = (i, j) #i=n//size, j=n%size
    return g, coord
g, coord = make_grid(10)
nodeweight = {n: 1 if True else None for n in g}
A_star(1, 10, hManhattan, d, g, coord, nodeweight)