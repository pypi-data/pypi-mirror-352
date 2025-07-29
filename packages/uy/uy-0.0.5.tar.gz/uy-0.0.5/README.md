# uy
Based on https://github.com/pbharrin/machinelearninginaction/blob/master/Ch12/fpGrowth.py

To install:	```pip install uy```

## Description
The `uy` package implements the FP-Growth algorithm for frequent itemset mining, avoiding the costly generation of candidate sets involved in algorithms like Apriori. This implementation includes functions to construct the FP-tree, update it, and mine the frequent itemsets from it. The package is designed to efficiently find frequent itemsets in a given dataset, which is crucial for tasks such as market basket analysis, association rule learning, and anomaly detection.

## Main Components
- **treeNode**: A class representing a node in the FP-tree. Each node contains links to parent and child nodes, a count of occurrences, and methods to manage the node's data.
- **createTree**: A function to build the FP-tree from the dataset. It also constructs a header table that helps in tree traversal.
- **updateTree**: Used to add items to the FP-tree during its construction.
- **mineTree**: Once the FP-tree is constructed, this function is used to mine the frequent itemsets from the tree using the header table.
- **loadSimpDat**: A utility function to load a simple example dataset.
- **createInitSet**: Converts a list of transactions into a dictionary format expected by `createTree`.

## Usage Examples

### Loading Data and Creating Initial Set
```python
from uy import loadSimpDat, createInitSet

# Load example data
simpDat = loadSimpDat()

# Create initial set from data
initSet = createInitSet(simpDat)
```

### Building the FP-Tree
```python
from uy import createTree

# Minimum support
minSup = 3

# Create FP-tree and header table
myFPtree, myHeaderTab = createTree(initSet, minSup)
```

### Mining Frequent Itemsets
```python
from uy import mineTree

# List to hold the mined frequent itemsets
freqItems = []

# Mine the tree
mineTree(myFPtree, myHeaderTab, minSup, set([]), freqItems)

# Print the frequent itemsets
print(freqItems)
```

## Documentation

### Class: treeNode
- **__init__(self, nameValue, numOccur, parentNode)**: Initialize a new tree node.
- **inc(self, numOccur)**: Increment the count of occurrences for the node.
- **disp(self, ind=1)**: Display the subtree rooted at this node.
- **__str__(self, ind=1)**: Return a string representation of the subtree rooted at this node.
- **__repr__(self, ind=1)**: Return the string representation for interactive environments.

### Function: createTree
- **createTree(dataSet, minSup=1)**: Create the FP-tree from the dataset. It returns the root of the FP-tree and the header table.

### Function: updateTree
- **updateTree(items, inTree, headerTable, count)**: Update the FP-tree with given items.

### Function: mineTree
- **mineTree(inTree, headerTable, minSup, preFix, freqItemList)**: Mine the FP-tree to find frequent itemsets that meet the minimum support.

### Function: loadSimpDat
- **loadSimpDat()**: Load a simple hardcoded dataset for demonstration purposes.

### Function: createInitSet
- **createInitSet(dataSet)**: Convert dataset into a format suitable for the FP-tree construction.

By using these functions and classes, users can perform efficient frequent itemset mining in various datasets, which is a foundational technique in many data mining applications.