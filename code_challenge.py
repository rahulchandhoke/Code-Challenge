
# coding: utf-8

# In[100]:


import networkx as nx
from copy import deepcopy


# In[101]:


# Reading the Entity Relationships. 
G_dict = {"FRIENDS_WITH":nx.Graph()}
other_rels = {}
type_dict = {}
f_rel = open("entity_relationships.txt")
f_rel.readline()
for line in f_rel.readlines():
    values = line.split()
    # Modeling person to person relationships using Graphs
    if values[2] == "Person" and values[4] == "Person":
        if values[0] not in G_dict:
            G_dict[values[0]] = nx.Graph()
        G_dict[values[0]].add_node(values[1])
        G_dict[values[0]].add_node(values[3])
        G_dict[values[0]].add_edge(values[1],values[3])
    # Adding attributes associated with person. Eg: C PLAYS_FOR Q
    elif values[2] == "Person": 
        G_dict["FRIENDS_WITH"].add_node(values[1])
        G_dict["FRIENDS_WITH"].node[values[1]][values[0]] = values[3]
    # Storing non person relationships in a dictionary for easy access. Eg: School X BELONGS_TO District Y
    else:
        if values[0] not in other_rels:
            other_rels[values[0]] = {}
        other_rels[values[0]][values[1]] = values[3]
    type_dict[values[1]] = values[2]
    type_dict[values[3]] = values[4]
nx.draw(G_dict["FRIENDS_WITH"],with_labels=True)


# In[102]:


# Reading the Entity Properties. Creating a lookup dictionary to get the properties and subsequent values for each ID.
f_prop = open("entity_properties.txt")
f_prop.readline()
lookup_dict = {}
for line in f_prop.readlines():
    values = line.strip().split(" ",2)
    if values[0] not in lookup_dict:
        lookup_dict[values[0]] = {}
    if values[1] not in lookup_dict[values[0]]:
        lookup_dict[values[0]][values[1]] = [values[2]]
    else:
        lookup_dict[values[0]][values[1]] += [values[2]]


# In[103]:


# Returns all fully connected cliques in the graph greater than or equal to a given size. Default size is 3.
def cliques(G,size=3,return_type="name"):
    clq = nx.find_cliques(G)
    clqs = []
    for i in clq:
        if len(i) >= size:
            clqs.append(i)
    if return_type == "name":
        return(id_to_name(clqs))
    return clqs


# In[104]:


# Returns densely connected subgraphs of a minimum size based on density threshold. Default size is 3 and threshold is 0.7.
# Density is defined as the number of edges in the subgraph divided by the max number of edges the subgraph can have.
def approx_cliques(G,size=3,threshold = 0.7,return_type="name"):
    clq = [set(x) for x in cliques(G,size,return_type="id")]
    all_nodes = set(G.nodes())
    results = deepcopy(clq)
    while clq:
        cur = clq.pop(0)
        not_in_cur = list(all_nodes-cur)
        for node in not_in_cur:   
            candidate = cur.union(set([node]))
            sub_graph = G.subgraph(list(candidate))
            if nx.density(sub_graph) >= threshold and candidate not in clq:
                clq.append(candidate)
                results.append(candidate)
    supersets = []
    for i in range(len(results)):
        flag = 0
        for j in range(i+1,len(results)):
            if results[j].union(results[i]) == results[j]:
                flag = 1
                break
        if flag == 0:
            supersets.append(results[i])
    supersets = [list(x) for x in supersets]
    if return_type == "name":
        return(id_to_name(supersets))
    return supersets


# In[105]:


# Returns all the people in the graph who are a part of a particular type of relationship. Example: People who attend a school.
# Can also be specific and query for a particular school.
def getnode_by_value(G,rel,val=""):
    node_attr = nx.get_node_attributes(G,rel)
    if val=="":
        return list(node_attr.keys())
    return [i for i in node_attr if node_attr[i] == val]


# In[106]:


# Returns the percentage of people who take part in a relationship. Example: Percentage of people who play for the Bulldogs.
def percentage(G,rel,type_val,val=""):
    if val:
        val = lookup_by_value(type_val,"",val)[0]
    deno = G.number_of_nodes()
    num = len(getnode_by_value(G,rel,val))
    return round(((num*1.0)/deno)*100.00,2)


# In[107]:


# Returns the ID of an entity given the name. Example: Returns 'A' if 'Ally' is given.
def lookup_by_value(type_val,prop,val):
    results = []
    if prop == "":
        for i in lookup_dict:
            if type_dict[i] == type_val:
                for prop in lookup_dict[i]:
                    if val in lookup_dict[i][prop] :
                        results.append(i)
                        break
    else:
        for i in lookup_dict:
            if type_dict[i] == type_val and prop in lookup_dict[i] and val in lookup_dict[i][prop]:
                results.append(i)
    return results


# In[108]:


# Returns the value of a particular relationship for a person. Eg: What car does Molly drive?
def person_rel_query(person, rel):
    person_id = lookup_by_value("Person","Name",person)[0]
    person_info = G_dict["FRIENDS_WITH"].node[person_id]
    result = []
    if rel in person_info:
        result = person_info[rel]
        result = lookup_dict[result]
    return result


# In[109]:


# Returns the relationship groups for a particular person based on size and threshold. Default threshold is 0.7 and minumum 
# size is 3. Example: What is Emilio's friend circle? or What is Molly's study group?
def relationship_group(rel,person,threshold = 0.7, size=3):
    person_id = lookup_by_value("Person","Name",person)[0]
    clqs = approx_cliques(G_dict[rel],size,threshold,return_type="id")
    results = []
    for i in clqs:
        if person_id in i:
            results.append(i)
    return id_to_name(results)


# In[110]:


# Returns the names corresponding to a list of IDs.
def id_to_name(id_list):
    results = []
    for i in id_list:
        circle = []
        for j in i:
            circle.append(lookup_dict[j]["Name"][0])
        results.append(circle)
    return results


# In[111]:


# Returns a list of people who satify a given condition. Example: All the people who attend USC.
def find_all(rel,type_val,val):
    id_list = lookup_by_value(type_val,"",val)
    results = []
    if rel in other_rels:
        for i in id_list:
            results += [x for x in other_rels[rel] if other_rels[rel][x] == i]
    else:
        for i in id_list:
            results += getnode_by_value(G_dict["FRIENDS_WITH"],rel,i)
    circle = []
    for j in results:
        circle.append(lookup_dict[j]["Name"][0])
    results = circle
    return list(set(results))


# In[112]:


# Running multiple tests to show sample queries that can be performed on the data.
def run_tests():
    print("Friend Cliques: ",cliques(G_dict["FRIENDS_WITH"]))
    print("Friend Groups with Density > 0.75:",approx_cliques(G_dict["FRIENDS_WITH"],threshold=0.75))
    print("Emilio's Friend Groups:",relationship_group("FRIENDS_WITH","Emilio"))
    print("Ally's Study Groups:",relationship_group("STUDIES_WITH","Ally",size=2))
    print("What car does Molly drive? ",person_rel_query("Molly", "DRIVES"))
    print("Who all drive a Volkswagen? ",find_all("DRIVES","Car","Volkswagen"))
    print("What schools belong to the district Shermer? ",find_all("BELONGS_TO","District","Shermer"))
    print("Who all live in district Shermer? ",find_all("LIVES_IN","District","Shermer"))
    print("What percentage of people attend school? ",percentage(G_dict["FRIENDS_WITH"],"ATTENDS","School"))
    print("What percentage of people attend USC? ",percentage(G_dict["FRIENDS_WITH"],"ATTENDS","School","USC"))
run_tests()

