# Kịch bản báo cáo giữa kỳ - Agentic Video Retrieval

## 1. Tên đề tài

**Đề tài 12 - Hệ thống agent phân tích dữ liệu tự động**  
Hướng triển khai: **Xây dựng AI Agent hỗ trợ tìm kiếm nội dung video bằng ngôn ngữ tự nhiên trên dữ liệu AIC 2026**.

## 2. Phần đã chạy được

- Nhận mục tiêu tìm kiếm bằng tiếng Việt.
- Planner tách đối tượng, hành động, bối cảnh và tạo query truy xuất.
- Agent gọi video retrieval tool qua API.
- Search tool trả keyframe, video ID, timestamp, score và object match.
- Agent tự tính điểm chất lượng Top-K.
- Nếu chưa đạt ngưỡng, Agent viết lại query và gọi tool lần hai.
- Frontend hiển thị kế hoạch, số lần thử, điểm tự đánh giá, keyframe và liên kết mở video đúng timestamp.
- Workflow n8n nhận webhook và điều phối Agent API.
- Có chế độ demo cục bộ không cần API key; chế độ AIC thật dùng CLIP feature, object metadata và index hiện có.

## 3. Luồng trình diễn 5 phút

1. Mở `http://localhost:3000/kis/search`.
2. Nhập: `Tìm cảnh một người đang đi xe đạp ngoài đường`.
3. Chỉ ra planner đã tách `person`, `bicycle`, `riding`, `street`.
4. Chỉ ra lần gọi search tool, điểm chất lượng và quyết định `accepted`.
5. Mở keyframe hạng 1 và video tại timestamp tương ứng.
6. Đổi ngưỡng chất lượng trong API lên cao để minh họa nhánh `rewrite_and_retry` nếu cần.
7. Mở n8n và cho thấy luồng Webhook -> AI Agent API -> Response.

## 4. Câu trả lời khi giảng viên hỏi “đây là Agent hay workflow?”

Workflow n8n chỉ làm nhiệm vụ điều phối. Phần Agent nhận **goal**, tự tạo kế hoạch, gọi search tool, quan sát kết quả, đánh giá theo ngưỡng và quyết định **trả kết quả hay sửa truy vấn rồi hành động lại**. Nhánh quyết định này làm hệ thống khác với automation tuyến tính cố định.

## 5. Phân biệt demo và dữ liệu AIC thật

Chế độ demo dùng sáu keyframe và một video minh họa để bảo đảm báo cáo chạy ổn định, không phụ thuộc mạng hoặc API key. Chế độ thật giữ nguyên API/UI nhưng thay search function bằng hybrid engine: CLIP feature + PCA/R-tree + object BoW + domain rerank. File Excel được cung cấp là danh sách URL tải dữ liệu, không chứa trực tiếp keyframe/video.

## 6. Việc sau giữa kỳ

- Tải các gói AIC cần thiết và build index thật.
- Cấu hình MiniMax/OpenAI-compatible planner và so sánh với planner offline.
- Xây tập query đánh giá; báo cáo Recall@K, MRR, latency và chi phí LLM/query.
- Thêm feedback phù hợp/không phù hợp và lưu log thực nghiệm.
- So sánh query gốc với Agent query refinement bằng cùng tập kiểm thử.

## 7. Phương án dự phòng

- Quay sẵn một video demo 2-3 phút.
- Giữ planner offline để không phụ thuộc API MiniMax.
- Dùng demo dataset nếu AIC index chưa build xong.
- Nếu n8n lỗi, gọi trực tiếp endpoint `/api/kis/agent/search/` từ Swagger; lõi Agent vẫn chạy đầy đủ.
