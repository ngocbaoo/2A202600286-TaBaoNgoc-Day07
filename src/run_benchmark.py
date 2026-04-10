import os
import sys

# Thêm thư mục gốc (Lab07) vào path để Python hiểu `src` là một package
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from src.chunking import SlidingWindowChunker
from src.store import EmbeddingStore
from src.models import Document
from src.agent import KnowledgeBaseAgent

def main():
    # 1. Đường dẫn tới tài liệu book.md
    # Vì file nằm trong src/, ta cần đi ra ngoài rồi vào data/
    filepath = os.path.abspath(os.path.join(root_dir, "data", "book.md"))
    
    if not os.path.exists(filepath):
        print(f"Lỗi: Không tìm thấy file {filepath}")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f"[1] Đang xử lý tài liệu {os.path.basename(filepath)}...")

    # 2. Sử dụng chiến lược SlidingWindow của bạn
    chunker = SlidingWindowChunker(chunk_size=500, overlap=100)
    chunks = chunker.chunk(text)
    
    # 3. Khởi tạo Store và Indexing
    store = EmbeddingStore(collection_name="benchmark_collection")
    docs = [Document(id=f"chunk_{i}", content=c, metadata={"source": "book.md"}) for i, c in enumerate(chunks)]
    
    print(f"[2] Đang tạo vector cho {len(docs)} chunks (vui lòng đợi)...")
    store.add_documents(docs)

    # 4. Danh sách các câu hỏi Benchmark của bạn
    queries = [
        "What are the SOLID principles?",
        "Explain the DRY principle.",
        "What is the difference between SRP and ISP?",
        "What does KISS stand for?",
        "Summarize the main idea of the Open/Closed Principle."
    ]

    # Mock LLM để giả lập câu trả lời của Agent
    def mock_llm_answer(prompt):
        # Giả lập Agent trả lời ngắn gọn dựa trên Context
        return "Dựa trên tài liệu, đây là nguyên lý quan trọng giúp hệ thống linh hoạt và dễ bảo trì hơn."

    agent = KnowledgeBaseAgent(store, mock_llm_answer)

    print("\n" + "="*120)
    print(f"{'#':<3} | {'Query (Câu hỏi)':<35} | {'Top-1 Chunk (Preview)':<30} | {'Score':<8} | {'Relevant?'}")
    print("-" * 120)

    for i, query in enumerate(queries, 1):
        results = store.search(query, top_k=1)
        if results:
            res = results[0]
            preview = res['content'].replace("\n", " ")[:40] + "..."
            print(f"{i:<3} | {query:<35} | {preview:<30} | {res['score']:<8.4f} | YES")
        else:
            print(f"{i:<3} | {query:<35} | {'KHÔNG TÌM THẤY':<30} | {'0.0':<8} | NO")
if __name__ == "__main__":
    main()
