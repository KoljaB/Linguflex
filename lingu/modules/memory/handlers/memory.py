import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import faiss
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import uuid
from datetime import datetime

class Memory:
    def __init__(self, save_dir: str = "memory_data"):
        self.save_dir = save_dir
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = 384  # Dimension of the 'all-MiniLM-L6-v2' model embeddings
        self.index = None
        self.memories = []
        self.memory_set = set()  # For fast duplicate checking
        self.tfidf_vectorizer = TfidfVectorizer()
        self.tfidf_matrix = None

        # Create save directory if it doesn't exist
        os.makedirs(self.save_dir, exist_ok=True)

        # Load existing data if available
        self.load()

    def add(self, text: str, user_id: str = "", metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        if text not in self.memory_set:
            memory_id = str(uuid.uuid4())
            embedding = self.model.encode([text])[0]
            memory = {
                "id": memory_id,
                "text": text,
                "user_id": user_id,
                "metadata": metadata or {},
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "history": []
            }
            self.memories.append(memory)
            self.memory_set.add(text)

            if self.index is None:
                self.index = faiss.IndexFlatL2(self.dimension)
            self.index.add(np.array([embedding]))
            self._update_tfidf()
            self.save()
            return memory
        else:
            return None

    def remove(self, text: str) -> bool:
        """Remove a memory by its text content."""
        for i, memory in enumerate(self.memories):
            if memory["text"] == text:
                removed_memory = self.memories.pop(i)
                self.memory_set.remove(text)
                
                if self.memories:
                    # Rebuild the FAISS index
                    new_embeddings = np.array([self.model.encode([m["text"]])[0] for m in self.memories])
                    self.index = faiss.IndexFlatL2(self.dimension)
                    self.index.add(new_embeddings)
                else:
                    # If all memories are removed, reset the index
                    self.index = None
                
                self._update_tfidf()
                self.save()
                # print(f"Removed memory: {removed_memory}")
                return True
        
        print(f"Memory with text '{text}' not found.")
        return False

    def update(self, memory_id: str, data: str) -> Dict[str, Any]:
        for memory in self.memories:
            if memory["id"] == memory_id:
                old_text = memory["text"]
                memory["history"].append({
                    "prev_value": old_text,
                    "new_value": data,
                    "updated_at": datetime.now().isoformat()
                })
                memory["text"] = data
                memory["updated_at"] = datetime.now().isoformat()

                # Update the index
                old_embedding = self.model.encode([old_text])[0]
                new_embedding = self.model.encode([data])[0]
                self.index.remove_ids(np.array([self.memories.index(memory)]))
                self.index.add(np.array([new_embedding]))

                self._update_tfidf()
                self.save()
                return memory
        return None  # Memory not found

    def clear(self):
        """Clear all memories and reset the index."""
        self.index = None
        self.memories = []
        self.memory_set = set()
        self.tfidf_vectorizer = TfidfVectorizer()
        self.tfidf_matrix = None

        # Remove saved data files
        index_path = os.path.join(self.save_dir, "faiss_index.bin")
        data_path = os.path.join(self.save_dir, "data.pkl")

        if os.path.exists(index_path):
            os.remove(index_path)
        if os.path.exists(data_path):
            os.remove(data_path)

        print("All memories have been cleared.")

    def search(self, query: str, user_id: str = None, k: int = 5) -> List[tuple[Dict[str, Any], float, float, float]]:
        if self.index is None:
            return []

        # Semantic similarity search
        query_embedding = self.model.encode([query])[0].reshape(1, -1)
        distances, indices = self.index.search(query_embedding, k)

        # Keyword matching
        query_tfidf = self.tfidf_vectorizer.transform([query])
        tfidf_similarities = cosine_similarity(query_tfidf, self.tfidf_matrix)[0]

        # Combine scores
        combined_scores = []
        for i, (idx, dist) in enumerate(zip(indices[0], distances[0])):
            if idx != -1:  # FAISS uses -1 for empty slots
                semantic_similarity = 1 / (1 + dist)  # Convert distance to similarity score
                tfidf_similarity = tfidf_similarities[idx]
                combined_score = 0.7 * semantic_similarity + 0.3 * tfidf_similarity  # Adjust weights as needed
                combined_scores.append((idx, combined_score, semantic_similarity, tfidf_similarity))

        # Sort by combined score
        combined_scores.sort(key=lambda x: x[1], reverse=True)

        # Filter and return top k results
        results = []
        for idx, combined_score, semantic_similarity, tfidf_similarity in combined_scores:
            memory = self.memories[idx]
            if user_id is None or memory["user_id"] == user_id:
                results.append((memory, combined_score, semantic_similarity, tfidf_similarity))
            if len(results) == k:
                break

        return results

    def get_all(self) -> List[Dict[str, Any]]:
        return self.memories

    def history(self, memory_id: str) -> List[Dict[str, Any]]:
        for memory in self.memories:
            if memory["id"] == memory_id:
                return memory["history"]
        return []

    def _update_tfidf(self):
        if self.memories:
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform([m["text"] for m in self.memories])
        else:
            self.tfidf_matrix = None
            self.tfidf_vectorizer = TfidfVectorizer()  # Reset the vectorizer

    def save(self):
        if self.index is not None and self.index.ntotal > 0:
            faiss.write_index(self.index, os.path.join(self.save_dir, "faiss_index.bin"))
        else:
            # If the index is empty, remove the existing file if it exists
            index_path = os.path.join(self.save_dir, "faiss_index.bin")
            if os.path.exists(index_path):
                os.remove(index_path)
        
        with open(os.path.join(self.save_dir, "data.pkl"), "wb") as f:
            pickle.dump((self.memories, self.memory_set, self.tfidf_vectorizer), f)

    def load(self):
        index_path = os.path.join(self.save_dir, "faiss_index.bin")
        data_path = os.path.join(self.save_dir, "data.pkl")

        if os.path.exists(index_path) and os.path.exists(data_path):
            self.index = faiss.read_index(index_path)
            with open(data_path, "rb") as f:
                self.memories, self.memory_set, self.tfidf_vectorizer = pickle.load(f)
            self._update_tfidf()

    def find_by_words(self, *words: str) -> Optional[str]:
        """
        Find the first memory containing all the specified words.
        
        :param words: Variable number of words to search for
        :return: The text of the first memory containing all words, or None if not found
        """
        if not words:
            return None

        words_lower = [word.lower() for word in words]
        
        for memory in self.memories:
            memory_text_lower = memory["text"].lower()
            if all(word in memory_text_lower for word in words_lower):
                return memory["text"]
        
        return None


# Example usage
if __name__ == "__main__":
    m = Memory()
    m.clear()

    # Add a memory
    result = m.add("I am working on improving my tennis skills. Suggest some online courses.")
    print("Added memory:", result)

    # Update a memory
    if result:
        updated = m.update(result["id"], "Likes to play tennis on weekends")
        print("Updated memory:", updated)

    result = m.add("I like ice cream.", user_id="alice")
    print("Added memory:", result)

    # Search for memories
    related_memories = m.search("What are the users hobbies on saturday and sunday?")
    print("Search results:")
    for memory, combined_score, semantic_similarity, tfidf_similarity in related_memories:
        print(f"Text: {memory['text']}")
        print(f"User ID: {memory['user_id']}")
        print(f"Combined Score: {combined_score:.4f}")
        print(f"Semantic Similarity: {semantic_similarity:.4f}")
        print(f"TF-IDF Similarity: {tfidf_similarity:.4f}")
        print("-" * 50)

    # Get all memories
    all_memories = m.get_all()
    print("All memories:", all_memories)

    # Get memory history
    if result:
        history = m.history(result["id"])
        print("Memory history:", history)