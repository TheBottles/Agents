
import math
import heapq

'''Script to implement A* algorithm for path from one point
in X/Y plane to the other point'''

'''The Objects that are going in the heap'''
class StateObject:
    def __init__(self):
        self.state = ()
        self.cost = 0
        self.backpointer = ()
    def __lt__(self,other):
        return self.cost < other.cost
    def __cmp__(self,other):
        return cmp(self.cost, other.cost)
    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return False


def Point_Distance(Point_List, Goal_X, Goal_Y):
    dist = [0] * len(Point_List)
    j = 0
    for P in Point_List:
        Result = Distance_Calc(Goal_X, Goal_Y, P[0], P[1])
        dist[j] = Result
        j= j + 1
    return dist

'''Distanc from any point to our goal coordinates'''
def Distance_Calc(X_Goal, Y_Goal, X, Y):
    X_Distance = math.pow((X_Goal - X), 2)
    Y_Distance = math.pow((Y_Goal - Y), 2)
    Final = math.sqrt(X_Distance + Y_Distance)
    return Final

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



'''A* implementation using the class slides'''
def pathfinding(Start, Graph, Goal):
    #Now we do all the agorithm here
    heapOpen = []
    heapClosed = []
    Temp = StateObject()
    Temp.state = Start
    Temp.cost = Distance_Calc(Goal[0], Goal[1], Start[0], Start[1]) + 1
    Temp.backpointer = Start
    heapOpen.append(Temp)
    heapq.heapify(heapOpen)

    #While 'Open' is not empty
    while len(heapOpen) > 0:
        heapq.heapify(heapOpen) #Update the heap
        Current = heapq.heappop(heapOpen)
        if Current.state == Goal:
                print("We got the current ", Current.state)
                print("This is the closed:")
                for s in heapClosed:
                    print(s.state, " ", s.cost, " ", s.backpointer)
                print("This is open: ")
                for y in heapOpen:
                    print(y.state, " ", y.cost, " ", y.backpointer)
                break
        else:
            Neighbors = Graph[Current.state]
            for n in Neighbors:
                #There's 3 cases but only took accound for 2 so far
                Temp = StateObject() #Create the StateObj for heap
                #Distance from the goal + cost of moving one square
                fn = Distance_Calc(Goal[0], Goal[1], n[0], n[1]) + 1
                Temp.state = n
                Temp.cost = fn
                Temp.backpointer = Current.state
                if find_state(heapOpen, Temp):
                    index = find_loc(heapOpen, Temp)
                    if heapOpen[index].cost > fn:
                        heapClosed[index].cost = fn
                        heapOpen[index].backpointer = Current.state

                        index = find_loc(heapClosed,Temp)
                        heapClosed[index].cost = fn
                        heapClosed[index].backpointer = Current.state
                else:
                    heapOpen.append(Temp)
                heapClosed.append(Temp)

    path = []
    done = False
    X = Goal
    while done == False:
        if X == Start:
            path.append(X)
            done == True
            break
        for y in heapClosed:
            if y.state == X:
                path.append(y.state)
                X = y.backpointer
                break

    print("Finished")
    print(path)
    return

'''For this algorithm we start at a "start" point and a "finish" point.
We then make a dictionary that represents the "graph" that is the map.
Each key in the dictionary is a tuple that represents a point and the value
for each key is a tuple of tuples that represents all the other points
that the current key connects to.'''
def A_Star(X,Y):
    #Account for the negative parts of the graph
    '''For the sake of implementation I started with 0,0
    but this will change based on where in the map we are
    since we are not always going to be at (0,0)'''
    List_X = list(range(0,X + 1))
    List_Y = list(range(0,Y + 1))
    Points = []
    '''Account for instance when there are more Y's than X's'''
    for x in List_X :
        for y in List_Y:
            Points.append([x,y])
    Dic = dict()
    for p in Points:
        I = connecting_points(p, Points)
        New_I = tuple(I)
        Dic[tuple(p)] = New_I
    Heap = []

    for key in Dic:
        print("This is the state: ",key)
        print(Dic[key])

    pathfinding((0,0),Dic,(X,Y))



if __name__ == "__main__":
    #These will change
    A_Star(6,10)
