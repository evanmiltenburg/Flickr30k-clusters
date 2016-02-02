import re
from glob import iglob
from collections import defaultdict, Counter
from itertools import combinations
import networkx as nx
import community
from networkx.readwrite import json_graph
from math import log
from pprint import pprint


def get_desc_and_link_counters(files):
    """
    Generates links between descriptions used to describe the same objects.
    Get a counter for the descriptions, and a counter for the links.
    """
    pattern = re.compile('\[(.*?)\]') # omitted question mark
    description_counter = defaultdict(int)
    link_counter = Counter()
    for file in files:
        with open(file) as f:
            categorized_descriptions = defaultdict(set)
            text = f.read()
            annotations = re.findall(pattern, text)
            for annotation in annotations:
                # Get the category and description from the annotation:
                category, *description = annotation.split()
                description = ' '.join(description).lower()
                # Categorize descriptions:
                categorized_descriptions[category].add(description)
                description_counter[description] += 1
            for descriptions in categorized_descriptions.values():
                link_counter.update(tuple(sorted(pair))
                                    for pair in combinations(descriptions,2))
    return description_counter, link_counter

def partitions_from_link_counter(link_counter, threshold=0):
    """
    Function that takes a link counter, constructs a graph, applies louvain clustering,
    and yields partitions from that clustering as sets. Links should occur more than
    threshold times to be considered.
    """
    G = nx.Graph()
    G.add_edges_from(pair for pair,count in link_counter.items() if count > threshold)
    for sub in sorted(nx.connected_component_subgraphs(G), key=len, reverse=True):
        partitioning = community.best_partition(sub)
        partition_sets = defaultdict(set)
        for node, partition in partitioning.items():
            partition_sets[partition].add(node)
        for s in partition_sets.values():
            yield s

def extended_partition_sets(partition_sets, below_threshold, check=True):
    """
    Function to extend the partitions created using the function above.
    Adds descriptions to the partition they have the most connections with.
    """
    item_to_num = {item: num for num, s in enumerate(partition_sets) for item in s}
    in_network = set(item_to_num.keys())
    belongs_with = defaultdict(Counter)
    remainder = []
    for a,b in below_threshold:
        a_in = a in in_network
        b_in = b in in_network
        if a_in and b_in:
            continue
        elif a_in and not b_in:
            belongs_with[b].update([item_to_num[a]])
        elif b_in and not a_in:
            belongs_with[a].update([item_to_num[b]])
        else:
            remainder.append((a,b))
    for description, c in belongs_with.items():
        first, *rest = c.most_common()
        num, count = first
        if check:
            if len(rest) == 0:
                item_to_num[description] = num
            else:
                second, *rest = rest
                num2, count2 = second
                if count > count2:
                    item_to_num[description] = num
        else:
            item_to_num[description] = num
    d = defaultdict(set)
    for item, num in item_to_num.items():
        d[num].add(item)
    return d.values(), remainder

# Create partition sets.
files = iglob('./static/Flickr30kEntities/Sentences/*.txt')
description_counter, link_counter = get_desc_and_link_counters(files)
partition_sets = list(partitions_from_link_counter(link_counter, threshold=1))

# Iteratively try to extend the partitions.
below_threshold = {pair for pair,count in link_counter.items() if count == 1}
print('iteration', 0, ';', 'unclassified:', len(below_threshold))
for i in range(1,11):
    partition_sets, below_threshold = extended_partition_sets(partition_sets,
                                                              below_threshold,
                                                              check=False)
    print('iteration', i, ';', 'unclassified:', len(below_threshold))

print('partition sets:', len(partition_sets))

# Write out the data.
partitions_in_order = sorted(partition_sets, key=len, reverse=True)
for i, s in enumerate(partitions_in_order):
    with open('clusters/' + str(i).zfill(3) + '.txt','w') as f:
        f.write('\n'.join(s))


# Cluster the remaining descriptions as much as possible.
# link_counter_rest = {pair:1 for pair in below_threshold}
# rest_partitions = [p for p in partitions_from_link_counter(link_counter, threshold=0)
#                    if len(p) > 3]
# print(len(rest_partitions))
