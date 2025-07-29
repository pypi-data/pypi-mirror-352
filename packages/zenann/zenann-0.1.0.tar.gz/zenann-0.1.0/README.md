# ZenANN: A High-Performance Vector Similarity Search Library for Python Users

## Basic Information

**ZenANN** is a high-performance approximate nearest neighbor (ANN) similarity search library designed to be user-friendly for Python developers. It provides multiple indexing methods, such as **IVF** (Inverted File Index), **HNSW** (Hierarchical Navigable Small World), and **hybrid-index structures** to balance between accuracy and speed. The computation kernel of ZenANN will be optimized for cache efficiency, SIMD acceleration, and algorithms enhancements beyond existing in-memory libraries.

## Problem to Solve
Similarity search is a fundamental problem in many domains, including information retrieval, natural language processing, and so on. The key challenge is to efficiently find out the nearest neighbors of a query vector in high-dimensional space. However, as the data size and dimensionality grows, the performance of traditional brute-force search (eg. KD-tree) may suffers from **Curse of Dimensionality**.

To solve this problem, **approximate nearest neighbor (ANN)** search aims to retrieve near-optimal results while significantly reducing computation time. It trades off a small loss in accuracy for significant speed improvements, making them ideal for high-dimensional vector search applications.

Although existing in-memory implementations (eg. Faiss) are highly optimized, there are still areas for improvement:
- Improved index data layout for a better cache locality
- SIMD acceleration for a specific algorithm
- Enhancements on data structures / algorithms to better match hardware characteristics

## Prospective Users
ZenANN is designed for developers and researchers working on large-scale similarity search applications, including:
- **Machine learning engineers** who use ANN search for embedding-based retrieval in NLP, computer vision, and recommendation systems.
- **Software developers** who build applications requiring fast vector search with a clear, user-friendly programming interface.
- **Data scientists** who perform large-scale similarity analysis on high-dimensional datasets.

## System Architecture
ZenANN will be implemented in C++ for high performance and exposes an intuitive Python API using pybind11.
### Index Hierarchy
There will be an abstract base index, which provides a unified interface for different index classes.
1. **Base Index Class**
    - `indexBase`: Defines the common API for all indexing methods (eg. `add()`, `search()`, `train()`)
2. **KD-tree Index Class**
    - `KDTreeIndex`: To serve as a baseline for approximate search algorithms, KD-tree is used to perform exact search.
3. **IVF Index Class**
    - `IVFIndex`: A cluster-based structure for large dataset
4. **HNSW Index Class**
    - `HNSWIndex`: A graph-based structure for accurate and efficient ANN

Note: Actual implementation detail of HNSW may be built on Faiss's interface according to development progress

### Processing Flow
1. Initialize an index (e.g., `indexBase`, `indexHNSW`)
2. Build an index with `add()` 
- Add the given vector data to a specific index instance.
- Train index with  `train()` if needed(for IVF-based Index)
- Optimize the index data layout with reorder_layout in Faiss submodule to improve cache locality.
4. Perform a query on the specified index instance using `search()`.
5. Return result set with top-k id & estimated distance for each query.

## API Description
There is a simple python examples for understanding the API design
```
import zenann

# Initialize an index for ANN search
index = zenann.HNSWIndex(dim=128, M=16, efConstruction=200)

# Add vectors to the index and conduct training / reordering
index.add(data_vectors)

# Perform a search
results = index.search(query_vector, k=5, efSearch=100)
```

## Engineering Infrastructure
### Automatic Build System
- GNU make
### Version Control
- Git
- Github
### Testing Framework
- Python: pytest
### Documentation
- Markdown
- Mermaid
### Continuous Integration
- Github Actions

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
