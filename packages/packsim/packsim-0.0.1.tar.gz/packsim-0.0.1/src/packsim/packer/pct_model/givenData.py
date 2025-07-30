# container_size: A vector of length 3 describing the size of the container in the x, y, z dimension.
# item_size_set:  A list records the size of each item. The size of each item is also described by a vector of length 3.
# import json
# import os

container_size = [5, 5, 10]
# container_size = [10,10,10]
# container_size = [1,1,1]

lower = 1
# higher = 5
higher = 3
resolution = 1
item_size_set = []
for i in range(lower, higher + 1):
    for j in range(lower, higher + 1):
        for k in range(lower, higher + 1):
                item_size_set.append((i * resolution, j * resolution , k *  resolution))

# If you want to sample item sizes from a uniform distribution in continuous domain,
# type --sample-from-distribution in your command line.

# BASE_DIR = os.path.dirname(__file__)
# action_path = os.path.join(BASE_DIR, "action.json")
# planning_time_path = os.path.join(BASE_DIR, "planning_time.json")

# with open(action_path, "r") as f:
#     actions = json.load(f)

# with open(planning_time_path, "r") as f:
#     planning_times = json.load(f)

# with open("action.json", "r") as f:
#     actions = json.load(f)

# with open("planning_time.json", "r") as f:
#     planning_times = json.load(f)

# num = len(actions)
