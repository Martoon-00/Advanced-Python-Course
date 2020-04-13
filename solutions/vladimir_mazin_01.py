# First part
def shape(m):
    return len(m), len(m[0])


def print_map(m, pos):
    n_rows, n_cols = shape(m)
    for row in range(n_rows):
        for col in range(n_cols):
            if pos[0] == row and pos[1] == col:
                print('@', end='')
            elif m[row][col]:
                print('.', end='')
            else:
                print('#', end='')
        print()


def neighbours(m, pos):
    n_rows, n_cols = shape(m)
    row, col = pos
    res = []
    shifts = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    for dr, dc in shifts:
        neighbour_row = row + dr
        neighbour_col = col + dc
        is_neighbour = neighbour_row in range(n_rows) and \
            neighbour_col in range(n_cols) and \
            m[neighbour_row][neighbour_col]
        if is_neighbour:
            res.append((neighbour_row, neighbour_col))
    return res


def find_route_step(m, cur_pos, cur_path, visited):
    n_rows, n_cols = shape(m)

    is_exit = cur_pos[0] == 0 or cur_pos[0] == n_rows - 1 or \
        cur_pos[1] == 0 or cur_pos[1] == n_cols - 1
    if is_exit:
        return cur_path

    for neighbour in neighbours(m, cur_pos):
        if neighbour not in visited:
            cur_path.append(neighbour)
            visited.add(neighbour)
            new_path = find_route_step(m, neighbour, cur_path, visited)
            if new_path:
                return new_path
            cur_path.pop()
            visited.remove(neighbour)
    return []


def find_route(m, initial):
    return find_route_step(m, initial, [initial], {initial})


def escape(m, initial):
    way_out = find_route(m, initial)
    for pos in way_out:
        print_map(m, pos)
        print()

# Second part


def hamming(seq1, seq2):
    res = 0
    for i in range(len(seq1)):
        if seq1[i] != seq2[i]:
            res += 1
    return res


def hba1(path, distance):
    lines = open(path, 'r').read().splitlines()
    distances = {}
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            distances[(i, j)] = distance(lines[i], lines[j])
    return min(distances, key=distances.get)

# Third part


def kmers(seq, k=2):
    d = {}
    for i in range(len(seq) + 1 - k):
        sub_seq = seq[i:i + k]
        d[sub_seq] = d.get(sub_seq, 0) + 1
    return d


def distance1(seq1, seq2):
    dist = 0
    d1 = kmers(seq1)
    d2 = kmers(seq2)
    keys = d1.keys() | d2.keys()
    for key in keys:
        dist += abs(d1.get(key, 0) - d2.get(key, 0))
    return dist

assert shape([[0]]) == (1, 1), "ERROR"