class AdjNode:
    def __init__(self, data):
        self.vertex = data
        self.next = None

visited = set()

class Graph:
    def __init__(self, vertices):
        self.V = vertices
        self.graph = [None] * self.V

    # Add edges
    def add_edge(self, src, dest):
        node = AdjNode(dest)
        node.next = self.graph[src]
        self.graph[src] = node

    #        node = AdjNode(src)
    #        node.next = self.graph[dest]
    #        self.graph[dest] = node

    # search child
    def search_child(self, parent, child):
        if parent not in visited:
#            print("Welcome to search_child. Parent {} and child {}".format(parent,child))
            visited.add(parent)
            temp = self.graph[parent]
            while temp:
                if temp.vertex == child:
                    return True
                if self.search_child_dfs(temp, child) == True:
                    return True
                temp = temp.next

        return False

        # search child

    def search_child_dfs(self, parent, child):
        if parent.vertex not in visited:
#            print("Welcome to search_child_dfs. Parent {} and child {}".format(parent.vertex,child))
            visited.add(parent.vertex)
            temp = self.graph[parent.vertex]
            while temp:
                if temp.vertex == child:
                    return True
                if self.search_child_dfs(temp, child) == True:
                    return True
                temp = temp.next

        return False

    # Print the graph
    def print_graph(self):
        for i in range(self.V):
            print("Adjacency list of vertex {}\n head".format(i))
            temp = self.graph[i]
            while temp:
                print(" -> {}".format(temp.vertex))
                temp = temp.next
            print(" \n")


as_array = []
AS_Array = []

with open("20200501_as_rel.txt") as fp:
    V = 400000
    # Create graph and edges
    graph = Graph(V)

    for line in fp:

        as_array = line.split('|')

        if as_array[2] == "-1\n":
            graph.add_edge(int(as_array[0]), int(as_array[1]))

#    graph.print_graph()

 #   print(" there is relationship-> {}".format(graph.search_child(3, 5)))

# sys.exit(0)

# heavy hitter with no parents
countries_list = ["Turkey_top_AS_list.txt", "Ukraine_top_AS_list.txt", "australia_top_AS_list.txt",
                  "china_top_AS_list.txt",
                  "colombia_top_AS_list.txt", "egypt_top_AS_list.txt", "germany_top_AS_list.txt",
                  "india_top_AS_list.txt", "iran_top_AS_list.txt", "italy_top_AS_list.txt", "japan_top_AS_list.txt",
                  "north_korea_top_AS_list.txt", "russia_top_AS_list.txt", "singapore_top_AS_list.txt",
                  "south_africa_top_AS_list.txt",
                  "south_korea_top_AS_list.txt", "uk_top_AS_list.txt", "united_states_top_AS_list.txt"]

full_as_countries_list = ["Turkey_full_AS_list.txt", "Ukraine_full_AS_list.txt", "australia_full_AS_list.txt",
                          "china_full_AS_list.txt",
                          "colombia_full_AS_list.txt", "egypt_full_AS_list.txt", "germany_full_AS_list.txt",
                          "india_full_AS_list.txt", "iran_full_AS_list.txt", "italy_full_AS_list.txt",
                          "japan_full_AS_list.txt",
                          "north_korea_full_AS_list.txt", "russia_full_AS_list.txt", "singapore_full_AS_list.txt",
                          "south_africa_full_AS_list.txt",
                          "south_korea_full_AS_list.txt", "uk_full_AS_list.txt", "united_states_full_AS_list.txt"]
country_index = 0
heavy_hitter_list_len = 0
full_as_list_len = 0
child_count = [0]*400000
i=0
for country_top_AS_list in countries_list:
    for fg in xrange(0, len(child_count)):
        child_count[fg] = 0
#    print(country_top_AS_list);
    with open(country_top_AS_list) as my_file:
        AS_array = my_file.readlines()
        AS_array = [s.strip('\n') for s in AS_array]
#        print("In country {}, top ASes {}".format(country_top_AS_list,AS_array));
        for ASp in AS_array:
            for ASc in AS_array:
                visited.clear()
                if graph.search_child(int(ASp), int(ASc)):
                    AS_array.remove(ASc)
#                    print("Parent {} and child {} relation is true".format(ASp, ASc))
#            print("parent number checked {} from country {}".format(i,country_top_AS_list))
#            i=i+1
#            if i==450:
#                sys.exit(0)
#        print("Heavy hitter for country {} is {}. Total number of heavy hitter ASes with no parent is {}".format(
#            country_top_AS_list, AS_array, len(AS_array)));

    heavy_hitter_file = country_top_AS_list.strip('_top_AS_list.txt') + "_" + str(len(AS_array)) + "_heavy_hitter.txt"
    with open(heavy_hitter_file, 'w') as filehandle:
        filehandle.writelines("%s\n" % place for place in AS_array)


    #Calculating % of internet covered in heavy_hitter file. ((final_child list)/full AS list)
    #ToDo: check if child_count array is properly getting assigned or not.
    full_as_country_file = full_as_countries_list[country_index];

    with open(heavy_hitter_file) as hhf:
        heavy_hitter_list = hhf.readlines()
        heavy_hitter_list = [x.strip('\n') for x in heavy_hitter_list]
        heavy_hitter_list_len = len(heavy_hitter_list)
        with open(full_as_country_file) as facf:
            full_as_list = facf.readlines()
            full_as_list = [x.strip('\n') for x in full_as_list]
            full_as_list_len = len(full_as_list)
            for hhp in heavy_hitter_list:
                for fac in full_as_list:
                    visited.clear()
                    if graph.search_child(int(hhp), int(fac)) == True:
                        child_count[int(fac)] = 1
#                        print("Parent {} and child {} relation is true. Child count flag is {}".format(int(hhp), int(fac),child_count[int(fac)]))
#                print("parent number checked {} from country {}".format(i,country_top_AS_list))
#                i=i+1
    final_child_count = 0
    for flag in child_count:
         if flag == 1:
            final_child_count +=1
    print("country {}, heavy_hitter {}, child count {}, full_as_list_length {}, % of AS covered by heavy hitter ASes is {}".format(country_top_AS_list,
        heavy_hitter_list_len,final_child_count, full_as_list_len, (100*(final_child_count)/full_as_list_len)))

    country_index += 1

