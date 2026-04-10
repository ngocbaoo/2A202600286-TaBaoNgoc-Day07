import os
import sys
import json

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from chunking import (
    FixedSizeChunker, 
    SentenceChunker, 
    RecursiveChunker, 
    SlidingWindowChunker,
    ChunkingStrategyComparator
)

def main():
    filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "book.md"))
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    chunk_size = 500
    overlap = 100

    chunkers = {
        "Fixed-Size": FixedSizeChunker(chunk_size=chunk_size, overlap=overlap),
        "Sentence-Based": SentenceChunker(max_sentences_per_chunk=3),
        "Recursive": RecursiveChunker(chunk_size=chunk_size),
        "Custom Sliding Window": SlidingWindowChunker(chunk_size=chunk_size, overlap=overlap)
    }

    print(f"\n{'='*80}")
    print(f"{'CHUNK SELECTION COMPARISON':^80}")
    print(f"{'Document: book.md (' + str(len(text)) + ' chars)':^80}")
    print(f"{'='*80}\n")
    
    print(f"{'Strategy':<25} | {'Count':<8} | {'Avg Len':<10} | {'Sample (First 50 chars)':<30}")
    print("-" * 80)

    for name, chunker in chunkers.items():
        try:
            chunks = chunker.chunk(text)
            avg_len = sum(len(c) for c in chunks) / len(chunks) if chunks else 0
            sample = chunks[0].replace("\n", " ")[:30] if chunks else "N/A"
            print(f"{name:<25} | {len(chunks):<8} | {avg_len:<10.2f} | {sample:<30}...")
        except Exception as e:
            print(f"{name:<25} | Error: {str(e)}")

    print(f"\n{'='*80}")

if __name__ == "__main__":
    main()

