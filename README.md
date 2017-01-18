# Clustering the Flickr30k descriptions

The code in this repository clusters the referring expressions in the Flickr30k Entities data set. It corresponds to the algorithm below.

The citation for this clustered data is:
```
@inproceedings{miltenburg2016stereotyping,
	Author = {Emiel van Miltenburg},
	Booktitle = {Proceedings of Multimodal Corpora: Computer vision and language processing (MMC 2016)},
	Editor = {Jens Edlund and Dirk Heylen and Patrizia Paggio},
	Keywords = {ulm2},
	Pages = {1-4},
	Title = {Stereotyping and Bias in the Flickr30k Dataset},
	Url = {http://www.lrec-conf.org/proceedings/lrec2016/workshops/LREC2016Workshop-MCC-2016-proceedings.pdf},
Year = {2016}}
```

The citation for the original data is:
```
@article{plummer2016flickr30k,
  title={Flickr30k entities: Collecting region-to-phrase correspondences for richer image-to-sentence models},
  author={Plummer, Bryan A and Wang, Liwei and Cervantes, Chris M and Caicedo, Juan C and Hockenmaier, Julia and Lazebnik, Svetlana},
  journal={International Journal of Computer Vision},
  pages={1--20},
  year={2016},
  publisher={Springer}
}

```

**Requirements**
This code requires the Flickr30kEntities dataset. Change the path on line 92 so that `files` corresponds to a list of .txt files
containing the descriptions.

```Python
files = iglob('./static/Flickr30kEntities/Sentences/*.txt')
```

## Algorithm

### Part 1: counting

1. Start with an empty Counter to count the amount of times two expressions refer to the same entity.
2. For each set of captions, extract the referring expressions. Then:
    
    a. For each entity, create a set of expressions (of size $n$) that refer to that entity.
    
    b. For each set of referring expressions, add all the $\dbinom{n}{2}$ combinations of expressions to the counter.
    
**Result:** a Counter storing the amount of times each combination of expressions has occurred.

### Part 2: clustering the data, forming partitions

1. Create a new undirected graph G.
2. For each combination of referring expressions, if that combination occurs more than $\theta=1$ times, both referring expressions become nodes in G, connected by an edge.
3. Perform (non-parametric) Louvain clustering on G, creating partitions.

**Result:** Sets of descriptions, where each set corresponds to a cluster. Note that the union of these sets is a proper subset of the total set of descriptions.

### Part 3: extending the clusters

1. Create a cluster index, mapping each description to the ID number of their cluster.
2. Cluster previously ignored referring expressions: for each unclustered expression, count the different clusters that it is linked to. Add it to the cluster that it is linked to the most. In case of a tie, there are two options: do nothing, or randomly add it to one of the clusters it is linked to.
