import heapq

from coordgrabber import *
from unitselection import *

PI = math.pi

"""Script to implement A* algorithm for path from one point\n'
 'in X/Y plane to the other point"""


class StateObject:
    """The Objects that are going in the heap"""

    def __init__(self):
        self.state = ()
        self.cost = 0
        self.back_pointer = None

    def __lt__(self, other):
        return self.cost < other.cost

    def __cmp__(self, other):
        return cmp(self.cost, other.cost)

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __str__(self):
        return "%s" % (str(self.state))


def connecting_points(current, points):
    """Get a list of all the points that can go out from one single point"""
    connections = []
    for P in points:
        if (P[0] == current[0] + 1) and (P[1] == current[1]):
            connections.append(tuple(P))
        elif (P[0] == current[0] - 1) and (P[1] == current[1]):
            connections.append(tuple(P))
        elif (P[0] == current[0]) and (P[1] == current[1] + 1):
            connections.append(tuple(P))
        elif (P[0] == current[0]) and (P[1] == current[1] - 1):
            connections.append(tuple(P))
    return connections


def find_state(objects, sub):
    """Check if a StateObject is in a list of states"""

    for x in objects:
        if x.state == sub:
            return True
    return False


def find_loc(states, atom):
    """Get the index of the state in the list"""
    i = 0
    while i < len(states):
        if states[i].state == atom:
            break
        i += 1
    return i


def graph(location, shape):
    """Converts an (x,y) coordinate to neighbor coordinates"""
    x, y = location
    thresh = 10
    neighbors = [(x - thresh, y - thresh), (x - thresh, y), (x - thresh, y + thresh), (x, y - thresh),
                 (x + thresh, y - thresh), (x + thresh, y - thresh), (x + thresh, y), (x + thresh, y + thresh)]
    goto = []
    for n in neighbors:
        if (n[0] < 0) or (n[0] >= shape[0]) or (n[1] < 0) or (n[1] >= shape[1]) or np.isnan(n).any():
            continue
        goto.append(n)
    return goto


def dubins(obs, Start, Goal):
    d = 15
    T = []
    D = []
    way_point = []
    flank_point = []

    slope = (Start[1] - Goal[1]) / (Start[0] - Goal[0])

    xd = (d / (math.sqrt(1 + (slope * slope))) + Goal[0])
    yd = ((d * slope) / (math.sqrt(1 + (slope * slope)))) + Goal[1]

    D.append(xd)
    D.append(yd)

    xt = (- d / (math.sqrt(1 + (slope * slope))) + Goal[0])
    yt = (- (d * slope) / (math.sqrt(1 + (slope * slope)))) + Goal[1]

    T.append(xt)
    T.append(yt)

    if distance(Start, D) < distance(Start, Goal):
        way_point.append(D[0])
        way_point.append(D[1])
        flank_point.append(T[0])
        flank_point.append(T[1])

    elif distance(Start, Goal) < distance(Start, D):
        way_point.append(T[0])
        way_point.append(T[1])
        flank_point.append(D[0])
        flank_point.append(D[1])

    distancew = distance(Goal, way_point)
    distancet = distance(Goal, flank_point)
    print("Distance to waypoint is", distancew)
    print("Other distance to flankpoint is ", distancet)

    print("WE ARE IN PATH FINDING")
    print("We are at ", Start)
    print("They are at ", Goal)
    print("Slope is ", slope)
    print("Waypoint is ", way_point)
    print("Flankpoint is ", flank_point)


def a_star(obs, start, goal):
    """A* implementation using the class slides"""

    # Now we do all the agorithm here
    # Not Implemented, just teting with it

    # Circle_Y/X are the coordinates for the middle of the circle
    # Now we can use the formula to see how far off each of these points are from the circle

    heapOpen = []
    heapClosed = []
    Temp = StateObject()
    Temp.state = start
    Temp.cost = distance(goal, start) + 1
    Temp.back_pointer = None
    heapOpen.append(Temp)
    heapq.heapify(heapOpen)
    explored = set()

    shape = get_map_size(obs)

    final = None
    # While 'Open' is not empty
    while len(heapOpen) > 0:
        heapq.heapify(heapOpen)  # Update the heap
        Current = heapq.heappop(heapOpen)
        Current.state = (int(Current.state[0]), int(Current.state[1]))
        distance_to_target = distance(goal, Current.state)
        if distance_to_target <= 15:
            final = StateObject()
            final.state = goal
            final.cost = 0
            final.back_pointer = Current
            # print("We got the current ", Current.state)
            # print("This is the closed:")
            # for s in heapClosed:
            #     print("    ", s.state, " ", s.cost, " ", s.backpointer)
            # print("This is open: ")
            # for y in heapOpen:
            #     print("    ", y.state, " ", y.cost, " ", y.backpointer)
            break
        else:
            Neighbors = graph(Current.state, shape)

            # Artificially add a direct line of path
            theta = math.atan2(start[1] - goal[1], start[0] - goal[0])
            x = round(math.cos(theta) * 10)
            y = round(math.sin(theta) * 10)
            Neighbors.append((x, y))

            for n in Neighbors:
                # There's 3 cases but only took accound for 2 so far

                # print("This is the shape ", shape)
                Temp = StateObject()  # Create the StateObj for heap
                # Distance from the goal + cost of moving one square
                # fn = Distance_Calc(Goal[0], Goal[1], n[0], n[1]) + 1
                fn = distance(n, goal)
                # print(fn)
                Temp.state = n
                Temp.cost = fn
                Temp.back_pointer = Current
                if find_state(heapOpen, Temp):
                    index = find_loc(heapOpen, Temp)
                    if heapOpen[index].cost > fn:
                        heapClosed[index].cost = fn
                        heapOpen[index].back_pointer = Current

                        index = find_loc(heapClosed, Temp)
                        heapClosed[index].cost = fn
                        heapClosed[index].back_pointer = Current
                else:
                    heapOpen.append(Temp)
                heapClosed.append(Temp)
        # print("loopdy-loop")s

    path = []

    current = final
    while current:
        path.append(current.state)
        current = current.back_pointer

    try:
        return path[-3]
    except IndexError:
        return goal


def arc_position(head_on_pos, flanker_pos, enemy_pos, radius, arc_length):
    theta_increment = arc_length / radius

    theta_head = math.atan2(enemy_pos[1] - head_on_pos[1], enemy_pos[0] - head_on_pos[0])
    theta_flank = math.atan2(enemy_pos[1] - flanker_pos[1], enemy_pos[0] - flanker_pos[0])

    theta_total = theta_head - theta_flank

    pos_angle = PI / 2 - abs(theta_total + theta_increment)
    neg_angle = PI / 2 - abs(theta_total - theta_increment)

    if PI / 2 - abs(theta_total) <= theta_increment:
        next_theta = PI / 2
    elif pos_angle < neg_angle:
        next_theta = theta_flank + theta_increment
    else:
        next_theta = theta_flank - theta_increment

    next_x = int(round(radius * math.cos(next_theta) + enemy_pos[0]))
    next_y = int(round(radius * math.sin(next_theta) + enemy_pos[1]))

    return next_x, next_y


if __name__ == "__main__":
    print(a_star(None, (0, 0), (6, 10)))
