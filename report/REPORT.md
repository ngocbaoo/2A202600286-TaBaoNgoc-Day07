# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** [Tạ Bảo Ngọc]
**Nhóm:** [D1]
**Ngày:** [10/4/2026]

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> *Viết 1-2 câu:* 
Có nghĩa là 2 vector có hướng giống nhau -> nội dung về mặt ngữ nghĩa gần như giống hoặc liên quan đến nhau

**Ví dụ HIGH similarity:**
- Sentence A: "Tôi thích ăn phở"
- Sentence B: "Tôi thích ăn bún"
- Tại sao tương đồng: Cả hai câu đều nói về việc thích ăn một loại đồ ăn, và "phở" và "bún" đều là các loại đồ ăn phổ biến ở Việt Nam.

**Ví dụ LOW similarity:**
- Sentence A: "Tôi thích ăn phở"
- Sentence B: "Tôi ghét ăn bún"
- Tại sao khác: Câu A nói về việc thích ăn phở, trong khi câu B nói về việc ghét ăn bún. Cả hai câu đều nói về việc ăn đồ ăn, nhưng một câu thể hiện sự yêu thích và một câu thể hiện sự không thích.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> *Viết 1-2 câu:* Cosine chỉ quan tâm đến hướng của vector, không quan tâm đến độ dài vector -> phù hợp với text embeddings vì độ dài của vector thường không mang nhiều ý nghĩa ngữ nghĩa

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* 

Stride:

$$
\text{stride} = 500 - 50 = 450
$$

Số chunks:

$$
\text{chunks} = \left\lceil \frac{10000 - 50}{450} \right\rceil
= \left\lceil \frac{9950}{450} \right\rceil
= \lceil 22.11 \rceil = 23
$$

> *Đáp án:* 23 chunks

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> *Viết 1-2 câu:* stride = 500 - 100 = 400
-> số chunks tăng (≈ 25 chunks). Overlap lớn giúp giữ ngữ cảnh giữa các chunk tốt hơn ít bị mất thông tin ở ranh giới, nhưng đổi lại tốn nhiều tài nguyên hơn.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Software Engineering 

**Tại sao nhóm chọn domain này?**
> *Viết 2-3 câu:* Do tài liệu dài và có cấu trúc rõ ràng, phù hợp để thử nghiệm các chiến lược chunking khác nhau. 
Ngoài ra tài liệu còn chứa các thông tin dạng bảng, ảnh, công thức. Việc hiểu và truy xuất chính xác các nguyên lý như SOLID, DRY, KISS là một bài toán thực tế và hữu ích cho các kỹ sư phần mềm.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | Information Systems Management|https://onlinelibrary.wiley.com/doi/book/10.1002/9781394297696?msockid=342527e00a4661fb18ff345a0bdc6080 | 503401| `{"category": "software-engineering", "source": "book.md"}`|

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| category | string | "software-engineering" | Giúp lọc các tài liệu theo chủ đề lớn, hữu ích khi hệ thống có nhiều domain khác nhau. |
| source | string | "book.md" | Cho phép truy xuất nguồn gốc của chunk, giúp xác minh thông tin và cung cấp thêm ngữ cảnh cho người dùng. |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| book.md| FixedSizeChunker (`fixed_size`) | 1119 | 499.82 | LOW |
| book.md| SentenceChunker (`by_sentences`) | 3877 | 128.28 | MEDIUM |
| book.md| RecursiveChunker (`recursive`) | 1398 | 358.34 | HIGH |

### Strategy Của Tôi

**Loại:** Sliding Window + Overlap

**Mô tả cách hoạt động:**
> *Viết 3-4 câu: strategy chunk thế nào? Dựa trên dấu hiệu gì?*
Chiến lược này sử dụng cơ chế cửa sổ trượt (sliding window) với kích thước cố định là 500 ký tự và khoảng chồng lấp (overlap) là 100 ký tự. Tuy nhiên, thay vì cắt cứng tại một vị trí cố định, thuật toán sẽ thực hiện "look-back" trong vùng overlap để tìm dấu xuống dòng (`\n`) gần nhất. Nếu tìm thấy, nó sẽ cắt tại đó để giữ cho nội dung của từng chunk được toàn vẹn về mặt hình thức (không bị cắt đôi dòng văn bản).

**Tại sao tôi chọn strategy này cho domain nhóm?**
> *Viết 2-3 câu: domain có pattern gì mà strategy khai thác?*
Với domain Software Engineering, tài liệu thường chứa các khối văn bản ngắn, danh sách liệt kê hoặc các đoạn code mẫu. Việc ưu tiên cắt tại dấu xuống dòng giúp các định nghĩa về nguyên lý phần mềm hoặc các bước hướng dẫn kỹ thuật được hiển thị đầy đủ trong một chunk, giúp LLM hiểu ngữ cảnh tốt hơn khi sinh câu trả lời.

**Code snippet (nếu custom):**
```python
class SlidingWindowChunker:
    """
    A sliding window chunker that tries to split at newlines within 
    the overlap zone to prevent cutting lines in half.
    """
    def __init__(self, chunk_size: int = 500, overlap: int = 100) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + self.chunk_size
            if end >= text_len:
                chunks.append(text[start:].strip())
                break
            
            overlap_start = end - self.overlap
            search_zone = text[overlap_start : end]
            last_newline = search_zone.rfind('\n')
            
            if last_newline != -1:
                actual_end = overlap_start + last_newline + 1
                chunks.append(text[start:actual_end].strip())
                start = actual_end
            else:
                chunks.append(text[start:end].strip())
                start = end - self.overlap
                
        return [c for c in chunks if c]
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| `book.md` | RecursiveChunker | 1398 | 358.34 | 8/10 |
| `book.md` | Sliding Window + Overlap | 1086 | 462.35 | 7/10|

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tạ Bảo Ngọc | Sliding Window + Overlap | 4 | Giữ vẹn câu/khối logic, tối ưu length | bị trùng dữ liệu -> tăng số chunk |
| Nguyễn Tuấn Hưng | Semantic Chunking | 9.5 | Giữ trọn vẹn ngữ cảnh của từng mục, truy xuất chính xác. | Các chunk có thể rất lớn, không phù hợp với các mô hình có giới hạn context nhỏ. |
| Lê Minh Hoàng | SoftwareEngineeringChunker (Custom RecursiveTrunker) | 8 | Bảo tồn hoàn hảo cấu trúc tài liệu kỹ thuật nhờ ngắt theo Header; Giữ được mối liên kết logic. | Kích thước chunk trung bình lớn, gây tốn context window của mô hình. |
| Nguyễn Xuân Hải | Parent-Child Chunking| 8 |Child nhỏ giúp tìm kiếm vector đúng mục tiêu, ít nhiễu | Gửi cả khối Parent lớn vào Prompt làm tăng chi phí API.
| Nguyễn Đăng Hải | DocumentStructureChunker | 6.3 | Giữ ngữ cảnh theo heading/list/table; grounding tốt cho tài liệu dài | Phức tạp hơn và tốn xử lý hơn; lợi thế giảm khi dữ liệu ít cấu trúc |
|Thái Minh Kiên | Agentic Chunking | 8 | chunk giữ được ý nghĩa trọn vẹn, retrieval chính xác hơn, ít trả về nửa vời, Không cần một rule cố định cho mọi loại dữ liệu | Với dataset lớn cost sẽ tăng mạnh,  chậm hơn pipeline thường, không ổn định tuyệt đối |
Trần Trung Hậu |Token-Based Chunking (Chia theo Token) | 8 | Kiểm soát chính xác tuyệt đối giới hạn đầu vào (context window) và chi phí API của LLM. | Cắt rất máy móc, dễ làm đứt gãy ngữ nghĩa của một từ hoặc một câu giữa chừng.


**Strategy nào tốt nhất cho domain này? Tại sao?**
`Semantic Chunking` là tốt nhất cho domain này vì nó tôn trọng cấu trúc logic của tài liệu, đảm bảo mỗi chunk là một đơn vị thông tin hoàn chỉnh. Điều này giúp hệ thống RAG truy xuất được ngữ cảnh đầy đủ để trả lời các câu hỏi về các nguyên lý cụ thể một cách chính xác nhất.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> *Viết 2-3 câu: dùng regex gì để detect sentence? Xử lý edge case nào?*
Sử dụng regex `(?<=[.!?])\s+|\n` để tách văn bản thành các câu. Việc sử dụng lookbehind `(?<=[.!?])` giúp giữ lại các dấu kết thúc câu (., !, ?) đi kèm với câu thay vì bị tách riêng. Sau đó, gom các câu lại thành từng nhóm dựa trên `max_sentences_per_chunk` để tạo thành các chunk hoàn chỉnh.

**`RecursiveChunker.chunk` / `_split`** — approach:
> *Viết 2-3 câu: algorithm hoạt động thế nào? Base case là gì?*
Sử dụng thuật toán đệ quy chia để trị. Bắt đầu với separator có ưu tiên cao nhất (ví dụ: `\n\n`), nếu một đoạn văn vẫn dài hơn `chunk_size`, nó sẽ tiếp tục được chia nhỏ bằng separator tiếp theo (`\n`, `. `, v.v.). Base case là khi đoạn văn đã đủ nhỏ hoặc không còn separator nào để chia, lúc đó sẽ thực hiện chia cắt cứng theo độ dài.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> *Viết 2-3 câu: lưu trữ thế nào? Tính similarity ra sao?*
Hệ thống hỗ trợ cả ChromaDB (sử dụng `EphemeralClient` cho sự cô lập) và lưu trữ in-memory. Khi thêm tài liệu, mỗi chunk được gán một ID duy nhất và lưu kèm embedding cùng metadata. Khi tìm kiếm, sử dụng Cosine Similarity ($dot(a, b) / (||a|| \cdot ||b||)$) để tìm các chunk có hướng vector tương đồng nhất với query.

**`search_with_filter` + `delete_document`** — approach:
> *Viết 2-3 câu: filter trước hay sau? Delete bằng cách nào?*
Sử dụng Metadata Pre-filtering: lọc các bản ghi thỏa mãn điều kiện metadata trước khi tính toán similarity để đảm bảo kết quả chính xác theo yêu cầu. Với `delete_document`, hệ thống so sánh số lượng bản ghi trước và sau khi thực hiện xóa theo `doc_id` để trả về trạng thái boolean chính xác.

### KnowledgeBaseAgent

**`answer`** — approach:
> *Viết 2-3 câu: prompt structure? Cách inject context?*
Triển khai theo mô hình RAG chuẩn: Retrieval (lấy top-k chunk từ store) -> Augmentation (nhúng các chunk vào prompt template làm Context) -> Generation (LLM sinh câu trả lời). Điều này giúp Agent trả lời dựa trên dữ liệu thực tế thay vì chỉ kiến thức có sẵn trong mô hình.

### Test Results

```
===================================== test session starts ======================================
collected 42 items                                                                              

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED     [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED              [  4%] 
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED       [  7%] 
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED        [  9%] 
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED             [ 11%] 
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED   [ 16%] 
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED    [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED  [ 21%] 
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                    [ 23%] 
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED    [ 26%] 
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED               [ 28%] 
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED           [ 30%] 
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                     [ 33%] 
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                    [ 45%] 
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED      [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED        [ 50%] 
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED              [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED   [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED     [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED      [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED               [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED              [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED         [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED     [ 71%] 
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED    [ 76%] 
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED          [ 78%] 
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED    [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates
 PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

====================================== 42 passed in 1.11s ======================================
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 |Hôm nay trời rất đẹp và xanh |Thời tiết hôm nay thật tuyệt vời. | low | -0.0913 |Đúng |
| 2 |Tôi đang học lập trình Python |Món phở bò này rất ngon | low | 0.0957 |Đúng |
| 3 | Tôi thích ăn táo mỗi ngày |Apple vừa ra mắt iphone mới | low | 0.0957 |Đúng |
| 4 | Anh ấy vừa qua đời | Anh ấy vừa mất | low | 0.0539 |Đúng |
| 5 | Tôi yêu Việt Nam | Tôi yêu Việt Nam | high | 1.0 |Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> *Viết 2-3 câu:* Câu "Anh ấy vừa qua đời" và "Anh ấy vừa mất" có nghĩa gần như giống nhau nhưng lại có điểm số cosine similarity thấp. Điều này cho thấy embeddings biểu diễn nghĩa dựa trên sự tương đồng về từ vựng và cấu trúc câu, chứ không phải sự tương đồng về ngữ nghĩa.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | What are the SOLID principles? | SOLID is an acronym for five design principles: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion. |
| 2 | Explain the DRY principle. | Don't Repeat Yourself means every piece of knowledge must have a single, unambiguous representation in a system. |
| 3 | What is the difference between SRP and ISP? | SRP is about a class having one reason to change, while ISP is about clients not depending on interfaces they don't use. |
| 4 | What does KISS stand for? | Keep It Simple, Stupid. |
| 5 | Summarize the main idea of the Open/Closed Principle. | Software entities should be open for extension but closed for modification. |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | What are the SOLID principles? | addressed. Otherwise, they are pendin... | -0.3087 | NO | Dựa trên tài liệu, chỉ thấy nhắc đến việc các vấn đề đang pending... |
| 2 | Explain the DRY principle. | cooperation agreements. With the reje... | -0.2314 | NO | Tài liệu không giải thích DRY, chỉ đề cập đến thỏa thuận hợp tác... |
| 3 | What is the difference between SRP and ISP? | workstations and users, processing ti... | -0.1875 | NO | Dữ liệu tìm thấy nói về workstations và thời gian xử lý, không có SRP... |
| 4 | What does KISS stand for? | system’s development trajectory in or... | -0.2890 | NO | Không có định nghĩa KISS. Tài liệu đang nói về quỹ đạo phát triển hệ thống... |
| 5 | Summarize the main idea of the Open/Closed Principle. | _Data Analytics and Big Data_ SZONIEC... | -0.2328 | NO | Có vẻ như nguyên lý này liên quan đến Data Analytics và Big Data... |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 0 / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> *Viết 2-3 câu:* Học được sự ưu việt của phương pháp \`Semantic Chunking\` từ bạn Tuấn Hưng. Mặc dù chiến lược \`Sliding Window\` của tôi giữ được dạng câu, nhưng việc dùng NLP để nhận diện ngữ nghĩa giúp phân tách các khối thông tin một cách tự nhiên và chính xác hơn hẳn, tránh việc cắt đứt một ý tưởng liên tục.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> *Viết 2-3 câu:* Visualize các chunking method một cách chi tiết để thấy được điểm mạnh, điểm yếu của từng phương pháp. 

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> *Viết 2-3 câu:* Thay vì chỉ dựa vào độ dài và ký tự xuống dòng, tôi sẽ thiết kế một pipeline làm sạch dữ liệu tốt hơn (bỏ noise) và kết hợp cắt theo cấu trúc Markdown (Heading/List) trước, sau đó mới dùng Window/Overlap cho các khối lớn. Đồng thời, tôi sẽ triển khai mô hình Embedding thực thụ ngay từ đầu.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 10/ 10 |
| Chunking strategy | Nhóm | 15/ 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 5/ 5 |
| Results | Cá nhân | 10/ 10 |
| Core implementation (tests) | Cá nhân | 30/ 30 |
| Demo | Nhóm | 4/ 5 |
| **Tổng** | | **89/ 100** |
