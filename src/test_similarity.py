import os
import sys

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, "..", "src"))
if src_dir not in sys.path:
    sys.path.append(src_dir)

from chunking import compute_similarity
from embeddings import _mock_embed

def run_test(sentence1, sentence2):
    # 1. Get embeddings
    vec1 = _mock_embed(sentence1)
    vec2 = _mock_embed(sentence2)
    
    # 2. Compute similarity
    score = compute_similarity(vec1, vec2)
    
    print(f"\n" + "="*50)
    print(f"Sentence A: \"{sentence1}\"")
    print(f"Sentence B: \"{sentence2}\"")
    print(f"-"*50)
    print(f"COSINE SIMILARITY SCORE: {score:.4f}")
    
    if score > 0.8:
        print("Đánh giá: Rất tương đồng (High Similarity)")
    elif score > 0.4:
        print("Đánh giá: Có liên quan (Medium Similarity)")
    else:
        print("Đánh giá: Ít tương đồng (Low Similarity)")
    print("="*50 + "\n")

if __name__ == "__main__":
    # BẠN CÓ THỂ THAY ĐỔI 2 CÂU DƯỚI ĐÂY
    s1 = "Tôi thích ăn táo mỗi ngày"
    s2 = "Apple vừa ra mắt iphone mới"
    
    run_test(s1, s2)
    
    # Thêm một ví dụ khác về sự khác biệt
    run_test("Anh ấy vừa qua đời", "Anh ấy vừa mất")
