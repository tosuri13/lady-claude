import numpy as np
from faiss import IndexFlatIP

# NOTE: Cohere Embed - Multilingual次元数を採用
DEFAULT_INDEX_DIMENSIONS = 1024


def delete(index: IndexFlatIP, id: int) -> IndexFlatIP:
    vectors = index.reconstruct_n(0, index.ntotal)  # type: ignore
    new_vectors = np.delete(vectors, id, axis=0)

    new_index = IndexFlatIP(DEFAULT_INDEX_DIMENSIONS)
    new_index.add(new_vectors)  # type: ignore

    return new_index
