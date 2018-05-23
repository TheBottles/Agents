import math
import heapq

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


def Point_Distance(Point_List, Goal_X, Goal_Y):
    dist = [0] * len(Point_List)
    j = 0
    for P in Point_List:
        Result = Distance_Calc(Goal_X, Goal_Y, P[0], P[1])
        dist[j] = Result
        j= j + 1
    return dist


def Distance_Calc(X_Goal, Y_Goal, X, Y):
    X_Distance = math.pow((X_Goal - X), 2)
    Y_Distance = math.pow((Y_Goal - Y), 2)
    Final = math.sqrt(X_Distance + Y_Distance)
    return Final

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



def pathfinding(Start, Graph, Goal):
    #Now we do all the agorithm here
    heapOpen = []
    heapClosed = []
    Temp = StateObject()
    Temp.state = Start
    Temp.cost = Distance_Calc(Goal[0], Goal[1], Start[0], Start[1])
    Temp.backpointer = Start
    heapOpen.append(Temp)
    heapq.heapify(HeapOpen)
    
    #While 'Open' is not empty
    while len(heapOpen) > 0:
        heapq.heapify(heapOpen) #Update the heap
        Current = heapq.
    
    
    
    
    
    
    
    
    
    
    
    
    return




def A_Star():
    X = [1,2,3,4]
    Y = [1,2,3,4]
    #Account for the negative parts of the graph
    List_X = list(range(0,5))
    List_Y = list(range(0,5))
    Points = []
    '''Account for instance when there are more Y's than X's'''
    for x in List_X :
        for y in List_Y:
            Points.append([x,y])
    Dic = dict()
    Distance_List = Point_Distance(Points,4,4)
    for p in Points:
        I = connecting_points(p, Points)
        New_I = tuple(I)
        Dic[tuple(p)] = New_I
    Heap = []
    for key in Dic:
        print("This is the state: ",key)
        print(Dic[key])
    pathfinding((0,0),Dic,(4,4))
    
        
        
'''
        print("Going for ", key)
        Temp = StateObject()
        Temp.state = key
        Temp.cost = Distance_Calc(4,4,key[0],key[1])
        print("This is the state: ", Temp.state)
        print("This is the cost: ", Temp.cost)
        Heap.append(Temp)
        


    while i > 0:
        counter += 1
        print("Length of the heap is ", len(Heap))
        J = heapq.heappop(Heap)
        print("The state returned is ", J.state)
        print("The cost of this state is ", J.cost)
        i -= 1
        print("This is i: ",i)
    print(Points)
    print("Length of points is ", len(Points))
    print("We ran the loop ",counter," times")
'''




if __name__ == "__main__":
    
    A_Star()




