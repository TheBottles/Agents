
import math
import heapq
from coordgrabber import *
import numpy as np
from unitselection import *


'''Script to implement A* algorithm for path from one point
in X/Y plane to the other point'''

'''The Objects that are going in the heap'''
class StateObject:
    def __init__(self):
        self.state = ()
        self.cost = 0
        self.backpointer = None
    def __lt__(self,other):
        return self.cost < other.cost
    def __cmp__(self,other):
        return cmp(self.cost, other.cost)
    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return False
    def __str__(self):
        return "%s" % (str(self.state))

'''Get a list of all the points that can go out from one single point'''
def connecting_points(Current, Points):
    connections = []
    for P in Points:
        if (P[0] == Current[0] + 1) and (P[1] == Current[1]):
            connections.append(tuple(P))
        elif (P[0] == Current[0] - 1) and (P[1] == Current[1]):
            connections.append(tuple(P))
        elif (P[0] == Current[0]) and (P[1] == Current[1] + 1):
            connections.append(tuple(P))
        elif (P[0] == Current[0]) and (P[1] == Current[1] - 1):
            connections.append(tuple(P))
    return connections


'''Check if a StateObject is in a list of states'''
def find_state(ObjectList, Sub):
    for x in ObjectList:
        if x.state == Sub:
            return True
    return False
'''Get the index of the state in the list'''
def find_loc(StateList, Atom):
    i = 0
    while i < len(List):
        if StateList[i].state == Atom:
            break
        i += 1
    return i

def heuristic(obs, location, target):
    # Take the number of enemy units
    # Our distance to target locations
    # Distance to center of mass of enemy units
    X, Y = location
    X_Goal, Y_Goal = target
    NUM_HOSTILE = get_num_enemies(obs)
    TARGET_DISTANCE =  Distance_Calc((X_Goal, Y_Goal), (X, Y))
    Enemy_Locations = get_enemy_coords(obs)
    X_Enemy, Y_Enemy = Enemy_Locations[0].mean(), Enemy_Locations[1].mean()
    ENEMY_DISTANCE = Distance_Calc((X_Enemy, Y_Enemy), (X, Y))

    # print( "%5.2f %5.2f" % (TARGET_DISTANCE, ENEMY_DISTANCE * .5))
    return NUM_HOSTILE + TARGET_DISTANCE - (ENEMY_DISTANCE * .5)

"Converts an (x,y) coordinate to neighbor coordinates"
def Graph(location, shape):
    x,y = location
    thresh = 10
    neighbors = [(x-thresh, y-thresh),  (x-thresh, y), (x-thresh, y+thresh), (x, y-thresh), (x+thresh, y-thresh), (x+thresh,y-thresh), (x+thresh, y), (x+thresh, y+thresh)]
    goto = []
    for n in neighbors:
        if ( n[0] < 0  ) or ( n[0] >= shape[0]) or ( n[1] < 0 ) or (n[1] >= shape[1]) or np.isnan(n).any():
            continue
        goto.append(n)
    # explored.update(set(goto))
    return goto
'''Function that makes list of circle points
def getCirclePoints(Point_One, Point_Two):
    points = []
    Circle_X = int((Point_one[0] + Point_Two[0])/2)
    Circle_Y = int((Point_One[1] + Point_Two[1])/2)

    temp1 = math.pow((Point_One[0] - Point_Two[0]),2)
    temp2 = math.pow((Point_One[1] - Point_Two[1]),2)
    radius = math.sqrt(temp1 + temp2)

    return points
''' 
#Leave this in case we need it 

'''Check what the point gives when we plug it into the circle function'''
def circleEquation(r, Cx, Cy, Point):
    resultOne = Point[0] - Cx
    resultOne = math.pow(resultOne, 2) 

    resultTwo = Point[1] - Cy
    resultTwo = math.pow(resultTwo, 2)

    Total = resultOne + resultTwo

    #Maybe this could be the cost 
    Diff  = r - Total 
    return Diff


def pathfinding(obs, Start, Goal):
    d = 15 
    T = []
    D = []
    Waypoint = []
    Flankpoint = [] 

    Circle_X = int((Start[0] + Goal[0])/2)
    Circle_Y = int((Start[1] + Goal[1])/2)
    temp1 = math.pow((Start[0] - Goal[0]),2)
    temp2 = math.pow((Start[1] - Goal[1]),2)
    radius = math.sqrt(temp1 + temp2)
    slope = (Start[1] - Goal[1])/(Start[0] - Goal[0])

    xd = (d/(math.sqrt(1 + (slope*slope))) + Goal[0])
    yd = ((d*slope)/(math.sqrt(1 + (slope*slope)))) + Goal[1]

    D.append(xd) 
    D.append(yd)


    xt = (- d/(math.sqrt(1 + (slope*slope))) + Goal[0])
    yt = (- (d*slope)/(math.sqrt(1 + (slope*slope)))) + Goal[1]

    T.append(xt)
    T.append(yt) 


    if Distance_Calc(Start, D) < Distance_Calc(Start, Goal):
        Waypoint.append(D[0])
        Waypoint.append(D[1])
        Flankpoint.append(T[0])
        Flankpoint.append(T[1])
    elif Distance_Calc(Start, Goal) < Distance_Calc(Start, D):
        Waypoint.append(T[0])
        Waypoint.append(T[1])
        Flankpoint.append(D[0])
        Flankpoint.append(D[1])

    distancew = Distance_Calc(Goal, Waypoint)
    distancet = Distance_Calc(Goal, Flankpoint)
    print("Distance to waypoint is", distancew)
    print("Other distance to flankpoint is ", distancet)



    print("WE ARE IN PATH FINDING")
    print("We are at ", Start)
    print("They are at ", Goal)
    print("Slope is ", slope)
    #print("We are going to", xd, " and ", yd)
    #print("Middle of the circle is at ", Circle_X, " and ", Circle_Y)
    #print("The other is at ", xt, " and ", yt)
    print("Waypoint is ", Waypoint)
    print("Flankpoint is ", Flankpoint)









'''A* implementation using the class slides'''
def AStar_Algo(obs, Start, Goal):

    #Now we do all the agorithm here
    #Not Implemented, just teting with it 
    
    #Circle_Y/X are the coordinates for the middle of the circle
    #Now we can use the formula to see how far off each of these points are from the circle 
    
    
    heapOpen = []
    heapClosed = []
    Temp = StateObject()
    Temp.state = Start
    Temp.cost = Distance_Calc(Goal, Start) + 1
    Temp.backpointer = None
    heapOpen.append(Temp)
    heapq.heapify(heapOpen)
    explored = set()

    shape = get_map_size(obs)

    final = None
    # While 'Open' is not empty
    while len(heapOpen) > 0:
        heapq.heapify(heapOpen) #Update the heap
        Current = heapq.heappop(heapOpen)
        Current.state = (int(Current.state[0]), int(Current.state[1]))
        distance_to_target = Distance_Calc (Goal, Current.state)
        if distance_to_target <= 15:
                final = StateObject()
                final.state = Goal
                final.cost = 0
                final.backpointer = Current
                # print("We got the current ", Current.state)
                # print("This is the closed:")
                # for s in heapClosed:
                #     print("    ", s.state, " ", s.cost, " ", s.backpointer)
                # print("This is open: ")
                # for y in heapOpen:
                #     print("    ", y.state, " ", y.cost, " ", y.backpointer)
                break
        else:
            Neighbors = Graph(Current.state, shape)
            for n in Neighbors:
                #There's 3 cases but only took accound for 2 so far
                
                #print("This is the shape ", shape)
                Temp = StateObject() #Create the StateObj for heap
                #Distance from the goal + cost of moving one square
                # fn = Distance_Calc(Goal[0], Goal[1], n[0], n[1]) + 1
                fn = Distance_Calc(n, Goal)
                # print(fn)
                Temp.state = n
                Temp.cost = fn
                Temp.backpointer = Current
                if find_state(heapOpen, Temp):
                    index = find_loc(heapOpen, Temp)
                    if heapOpen[index].cost > fn:
                        heapClosed[index].cost = fn
                        heapOpen[index].backpointer = Current

                        index = find_loc(heapClosed,Temp)
                        heapClosed[index].cost = fn
                        heapClosed[index].backpointer = Current
                else:
                    heapOpen.append(Temp)
                heapClosed.append(Temp)
        # print("loopdy-loop")s

    path = []


    current = final
    while current:
        path.append(current.state)
        current = current.backpointer

    try:
        return path[-2]
    except IndexError:
        return Goal


'''For this algorithm we start at a "start" point and a "finish" point.
We then make a dictionary that represents the "graph" that is the map.
Each key in the dictionary is a tuple that represents a point and the value
for each key is a tuple of tuples that represents all the other points
that the current key connects to.'''
def A_Star(obs, location, target, flank = False):
    #Account for the negative parts of the graph
    '''For the sake of implementation I started with 0,0
    but this will change based on where in the map we are
    since we are not always going to be at (0,0)'''


    #if Distance_Calc(location, target) > 15 and not flank: 
        #return AStar_Algo(obs,location, target)
    #elif flank:
    pathfinding(obs, location, target)
    return AStar_Algo(obs,location, target)




if __name__ == "__main__":
    #These will change
    print(A_Star(None, (0,0), (6,10)))
