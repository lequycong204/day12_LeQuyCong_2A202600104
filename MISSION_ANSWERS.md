# Day 12 Lab - Mission Answers

Sinh viên: Lê Quý Công  
Mã số sinh viên: 2A202600104  
Ngày: 2026-04-18

---

## Part 1: Localhost vs Production

### Exercise 1.1: Các anti-pattern tìm thấy

Dựa trên ví dụ `01-localhost-vs-production/develop`, em xác định các anti-pattern chính như sau:

1. Hardcode API key trong source code, dễ bị lộ nếu đẩy lên GitHub công khai.
2. Cấu hình không lấy từ biến môi trường nên khó tách biệt dev, test và production.
3. Không có endpoint health check để platform kiểm tra tình trạng sống của service.
4. Không có readiness check để load balancer biết khi nào instance sẵn sàng nhận traffic.
5. Không xử lý graceful shutdown nên request đang xử lý có thể bị cắt ngang khi deploy hoặc restart.
6. Dùng logging kiểu `print()` thay vì structured logging nên khó monitor và truy vết.
7. Port bị cố định thay vì đọc từ `PORT`, làm giảm khả năng chạy trên cloud platform.

### Exercise 1.2: Chạy basic version

Các bước chạy:

```bash
cd 01-localhost-vs-production/develop
pip install -r requirements.txt
python app.py
```

Kết quả mong đợi:

- Ứng dụng chạy ở `http://localhost:8000`
- Có thể truy cập endpoint gốc để kiểm tra app hoạt động
- Tuy nhiên app mới chỉ phù hợp để demo local, chưa đạt mức production-ready

### Exercise 1.3: Bảng so sánh develop và production

| Tính năng | Develop | Production | Tại sao quan trọng? |
|-----------|---------|------------|---------------------|
| Config | Hardcode trong code | Đọc từ env vars | Dễ đổi môi trường mà không sửa source code |
| Secrets | Có thể ghi trực tiếp trong code | Đọc từ env hoặc secret manager | Tránh lộ credentials trong git |
| Port | Cố định `8000` | Đọc từ `PORT` | Tương thích với Railway, Render, Cloud Run |
| Health check | Không có | Có `/health` | Platform biết khi nào cần restart |
| Readiness | Không có | Có `/ready` | Load balancer chỉ route traffic khi app sẵn sàng |
| Logging | `print()` | Structured logging | Dễ debug và monitor hơn |
| Shutdown | Tắt đột ngột | Graceful shutdown | Tránh rơi request khi deploy |
| Quản lý config | Phân tán | Tập trung trong file config | Dễ bảo trì và mở rộng |

---

## Part 2: Docker

### Exercise 2.1: Trả lời câu hỏi Dockerfile

1. Base image của bản basic là `python:3.11`
2. Base image của bản production là `python:3.11-slim`
3. Working directory trong container là `/app`
4. Copy `requirements.txt` trước để tận dụng Docker layer cache
5. Multi-stage build giúp giảm kích thước image và tách môi trường build khỏi runtime
6. Runtime dùng non-root user để tăng bảo mật
7. `CMD` là lệnh mặc định khi start container và dễ override hơn `ENTRYPOINT`

### Exercise 2.2: Build và run basic container

Lệnh:

```bash
docker build -f 02-docker/develop/Dockerfile -t agent-develop .
docker run -p 8000:8000 agent-develop
curl http://localhost:8000/health
```

Kết quả mong đợi:

- Docker image build thành công
- Container chạy được ứng dụng ở cổng `8000`
- Có thể kiểm tra app bằng `curl`

### Exercise 2.3: So sánh image size

So sánh:

- Image basic lớn hơn vì dùng `python:3.11` và single-stage build
- Image production nhỏ hơn vì dùng `python:3.11-slim` và multi-stage build
- Mức giảm hợp lý thường vào khoảng 50-70%

Giải thích:

1. Image `slim` có ít package hệ điều hành hơn
2. Build tools chỉ tồn tại trong builder stage
3. Runtime stage chỉ giữ lại dependencies và source code cần thiết

### Exercise 2.4: Sơ đồ kiến trúc và test stack

Sơ đồ hệ thống:

```text
Client -> Nginx -> Agent -> Redis
                 -> Qdrant
```

Vai trò các thành phần:

- `nginx`: reverse proxy và entrypoint của hệ thống
- `agent`: ứng dụng FastAPI chính
- `redis`: cache hoặc shared state
- `qdrant`: vector database phục vụ RAG

Lệnh chạy stack:

```bash
docker compose -f 02-docker/production/docker-compose.yml up --build
```

Lưu ý:

- File đúng là `docker-compose.yml`, không phải `docker-compose.yaml`
- Nếu Dockerfile `COPY` file từ root như `utils/mock_llm.py` thì build context trong Compose phải trỏ đúng về root project

---

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment

Các bước deploy cơ bản bằng Railway:

```bash
cd 03-cloud-deployment/railway
railway login
railway init
railway up
```

Kết quả mong đợi:

- Railway liên kết project
- Upload source code và build service
- Trả về public URL để truy cập dịch vụ

Tại sao Railway phù hợp cho bài lab:

- Triển khai nhanh
- Ít bước cấu hình
- Thuận tiện cho demo và MVP

### Exercise 3.2: So sánh Railway và Render config

| File | Nền tảng | Vai trò |
|------|----------|---------|
| `railway.toml` | Railway | Cấu hình build/deploy cho Railway |
| `render.yaml` | Render | Blueprint / Infrastructure as Code cho Render |

Điểm quan trọng:

- `railway up` dùng ngữ cảnh Railway, không đọc `render.yaml`
- Render đọc `render.yaml`, không dùng `railway.toml`
- Mỗi nền tảng có cơ chế config riêng, không dùng lẫn trực tiếp

### Exercise 3.3: Hiểu về Cloud Run CI/CD

Trong `03-cloud-deployment/production-cloud-run`:

- `cloudbuild.yaml` là pipeline CI/CD
- `service.yaml` là file định nghĩa dịch vụ Cloud Run

Ý nghĩa:

1. `cloudbuild.yaml` quy định các bước test, build image, push image và deploy
2. `service.yaml` khai báo image, CPU, RAM, scaling, env vars, probes

Kết luận:

- `cloudbuild.yaml` thuộc phần CI/CD
- `service.yaml` thuộc phần deployment / IaC

---

## Part 4: API Security

### Exercise 4.1: API key authentication

Trong `04-api-gateway/develop/app.py`, API key được đọc từ header:

```python
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
```

Điều này có nghĩa:

- Server lấy giá trị key đúng từ biến môi trường `AGENT_API_KEY`
- Client phải gửi key trong header `X-API-Key`
- Thiếu key sẽ trả `401`
- Sai key sẽ trả `403`

Ví dụ gọi đúng:

```bash
curl -X POST "http://localhost:8000/ask?question=hello" \
  -H "X-API-Key: my-secret-key"
```

### Exercise 4.2: JWT authentication

JWT phù hợp hơn API key trong các hệ thống có người dùng thật vì:

1. JWT chứa được identity và role
2. JWT có thời gian hết hạn
3. JWT hỗ trợ xác thực stateless
4. Dễ tích hợp với cơ chế phân quyền

Flow cơ bản:

1. User đăng nhập
2. Server cấp JWT
3. Client gửi `Authorization: Bearer <token>`
4. Server xác minh chữ ký, expiry và claims

### Exercise 4.3: Rate limiting

Mục tiêu của rate limiting:

- Chống spam và abuse
- Giảm tải hệ thống
- Bảo vệ tài nguyên và chi phí

Một ngưỡng phù hợp cho bài lab là:

- `10 requests / minute / user`

Redis phù hợp vì:

1. Dùng chung được cho nhiều instance
2. Phù hợp với hệ thống stateless
3. Hỗ trợ counter có TTL rất tốt

Khi vượt giới hạn, API nên trả `429 Too Many Requests`.

### Exercise 4.4: Cost guard

Cost guard dùng để kiểm soát chi phí sử dụng model AI.

Cách triển khai hợp lý:

1. Ước tính cost cho mỗi request dựa trên token hoặc model
2. Cộng dồn chi phí theo user hoặc theo toàn hệ thống
3. Lưu số liệu vào Redis hoặc database
4. Khi vượt ngưỡng ngân sách thì chặn hoặc giảm cấp tính năng

Ví dụ chính sách:

- Dưới 80% ngân sách: hoạt động bình thường
- Từ 80% đến 100%: cảnh báo và hạn chế tác vụ đắt
- Trên 100%: từ chối request không thiết yếu

---

## Part 5: Scaling & Reliability

### Exercise 5.1: Health và readiness checks

Trong `05-scaling-reliability/develop/app.py`:

- `/health` là liveness probe
- `/ready` là readiness probe

Khác biệt:

- `/health` kiểm tra app còn sống không
- `/ready` kiểm tra app đã sẵn sàng nhận request chưa

Điều này quan trọng vì một app có thể còn chạy nhưng chưa sẵn sàng phục vụ traffic.

### Exercise 5.2: Graceful shutdown

Bản develop đã có:

- FastAPI lifespan
- Theo dõi request đang xử lý
- Bắt `SIGTERM`
- `timeout_graceful_shutdown=30`

Ý nghĩa:

1. Dừng nhận request mới một cách an toàn
2. Cho request đang xử lý hoàn tất
3. Giảm lỗi khi rolling deploy hoặc restart container

### Exercise 5.3: Stateless design

Trong `05-scaling-reliability/production/app.py`:

- Session được lưu theo `session_id`
- Nếu có Redis thì state nằm ngoài process
- Bất kỳ instance nào cũng có thể đọc lại conversation history

Tại sao quan trọng:

1. Load balancer có thể chuyển request tới bất kỳ replica nào
2. Restart một instance không làm mất toàn bộ context
3. Dễ scale ngang

### Exercise 5.4: Chạy load balanced stack

Stack production gồm:

- nhiều agent instances
- Redis làm shared state store
- Nginx làm reverse proxy và load balancer

Lệnh ví dụ:

```bash
docker compose up --scale agent=3
```

Lợi ích:

- Chia tải đều qua nhiều instance
- Hệ thống vẫn hoạt động nếu một instance bị restart

### Exercise 5.5: Test stateless behavior

Cách kiểm tra:

1. Chạy stack với nhiều agent instance
2. Tạo một conversation session
3. Gửi tiếp request với cùng `session_id`
4. Tắt một instance
5. Gửi request tiếp theo

Kết quả mong đợi:

- Conversation history vẫn còn
- Request vẫn xử lý thành công
- Không phụ thuộc vào một process cụ thể vì state nằm trong Redis

---

## Tổng kết

Qua Day 12, em rút ra các ý chính:

1. Code chạy được ở localhost chưa đồng nghĩa với production-ready.
2. Docker giúp đóng gói môi trường chạy nhất quán, nhưng build context và cấu trúc file phải đúng.
3. Railway, Render và Cloud Run có cách cấu hình deployment khác nhau, không dùng chung trực tiếp.
4. Bảo mật API không chỉ là authentication mà còn cần rate limiting và cost guard.
5. Muốn scale ổn định thì phải có health checks, graceful shutdown và kiến trúc stateless.
