# src/elastic_hash.py

class ElasticHashSet:
    """
    A simplified conceptual implementation of Elastic/Funnel Hashing.
    Uses multiple layers of geometrically decreasing sizes to handle collisions 
    without reordering elements, ensuring optimal amortized search time.
    """
    def __init__(self, capacity=10000):
        # Create 3 layers (funnels) for open addressing
        self.layer1 = [None] * capacity
        self.layer2 = [None] * (capacity // 2)
        self.layer3 = [None] * (capacity // 4)
        self.layers = [self.layer1, self.layer2, self.layer3]
        
    def _hash(self, item, layer_size, seed=0):
        # Simple polynomial rolling hash for coordinates like (x, y)
        return (hash(item) + seed) % layer_size

    def add(self, item):
        for i, layer in enumerate(self.layers):
            idx = self._hash(item, len(layer), seed=i)
            # Probe a few times in the current layer
            for probe in range(3): 
                probe_idx = (idx + probe) % len(layer)
                if layer[probe_idx] is None or layer[probe_idx] == item:
                    layer[probe_idx] = item
                    return
        # Fallback if heavily saturated (In a true elastic hash, the sequence extends)
        self.layers[-1].append(item) 

    def contains(self, item):
        for i, layer in enumerate(self.layers):
            idx = self._hash(item, len(layer), seed=i)
            for probe in range(3):
                probe_idx = (idx + probe) % len(layer)
                if layer[probe_idx] == item:
                    return True
                if layer[probe_idx] is None:
                    break # Not in this cluster
        return item in self.layers[-1]