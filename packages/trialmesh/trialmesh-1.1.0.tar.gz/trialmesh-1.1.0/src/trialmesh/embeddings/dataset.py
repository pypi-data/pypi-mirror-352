# src/trialmesh/embeddings/dataset.py

from torch.utils.data import Dataset
from typing import List


class EmbeddingDataset(Dataset):
    """Dataset for efficient batching of text to embed.

    This class implements PyTorch's Dataset interface to provide efficient
    loading and batching of text data for embedding generation.

    Attributes:
        texts (List[str]): List of texts to encode
        ids (List[str]): List of document IDs corresponding to texts
        max_length (int): Maximum sequence length for tokenization
    """

    def __init__(self, texts: List[str], ids: List[str], max_length: int = 512):
        """Initialize an embedding dataset.

        Args:
            texts: List of texts to encode
            ids: List of document IDs corresponding to texts
            max_length: Maximum sequence length (not used directly, but useful for reference)
        """
        self.texts = texts
        self.ids = ids
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        """Get a single item from the dataset.

        This method returns a dictionary containing the text and ID
        for the specified index.

        Args:
            idx: Index of the item to retrieve

        Returns:
            Dictionary with 'text' and 'id' keys
        """
        return {
            "text": self.texts[idx],
            "id": self.ids[idx]
        }