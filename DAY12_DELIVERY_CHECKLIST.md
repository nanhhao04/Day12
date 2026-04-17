#  Delivery Checklist — Day 12 Lab Submission

> **Student Name:** Nguyễn Anh Hào   
> **Student ID:** 2A202600131
> **Date:** 17/04/2026

---

##  Submission Requirements

Submit a **GitHub repository** containing:

### 1. Mission Answers (40 points)

Create a file `MISSION_ANSWERS.md` with your answers to all exercises:

```markdown
# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. **Hardcoded Secrets**: API Key và link Database nằm trực tiếp trong code, gây rủi ro bảo mật nghiêm trọng.
2. **Thiếu Config Management**: Các cài đặt như DEBUG, MAX_TOKENS bị gán cứng, không linh hoạt giữa các môi trường.
3. **Logging không chuyên nghiệp**: Dùng `print()` thay vì logging library, gây khó khăn khi quản lý log trên server.
4. **Không có Health Check**: Hệ thống không biết khi nào app bị treo để tự động khởi động lại.
5. **Fix cứng Host/Port**: Lắng nghe tại `localhost:8000` thay vì đọc từ biến môi trường `PORT`, dẫn đến fail khi chạy trên Container/Cloud.

| Feature | Develop (Basic) | Production (Advanced) | Tại sao quan trọng? |
| :--- | :--- | :--- | :--- |
| **Config** | Hardcode trong code | Biến môi trường (.env) | Bảo mật và dễ dàng thay đổi cấu hình mà không cần sửa code. |
| **Health check** | Không có | Có `/health` & `/ready` | Giúp Cloud Platform giám sát trạng thái và tự động phục hồi app. |
| **Logging** | `print()` | Structured JSON Log | Máy có thể đọc và phân tích log tự động trên quy mô lớn. |
| **Shutdown** | Đột ngột | Graceful (SIGTERM) | Đảm bảo các request dở dang được hoàn thành trước khi tắt app. |
| **Binding** | `localhost` | `0.0.0.0` | Để container có thể nhận kết nối từ mạng bên ngoài. |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. **Base image**: `python:3.11` (Bản đầy đủ).
2. **Working directory**: `/app`.
3. **Tại sao COPY requirements.txt trước?**: Để tận dụng Layer Cache. Docker sẽ không chạy lại `pip install` nếu file này không đổi, giúp build cực nhanh.
4. **CMD vs ENTRYPOINT**: `CMD` cung cấp lệnh mặc định và dễ bị ghi đè, trong khi `ENTRYPOINT` quy định mục đích chính của container và khó ghi đè hơn.

### Exercise 2.3: Image size comparison
- **Develop**: ~1.66 GB
- **Production**: ~236 MB
- **Chênh lệch**: Giảm ~86% nhờ kỹ thuật Multi-stage build và base image slim.

### Exercise 2.4: Docker Compose stack
- **Kiến trúc**: Nginx (Load Balancer) đứng trước Agent.
- **Luồng dữ liệu**: Client -> Nginx (Port 80) -> Agent (Port 8000). Nginx đóng vai trò Reverse Proxy, giúp ẩn port thực của Agent và có thể chia tải sau này.

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://your-app.railway.app
- Screenshot: [Link to screenshot in repo]

## Part 4: API Security

### Exercise 4.1-4.3: Test results
[Paste your test outputs]

### Exercise 4.4: Cost guard implementation
[Explain your approach]

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
[Your explanations and test results]
```

---

### 2. Full Source Code - Lab 06 Complete (60 points)

Your final production-ready agent with all files:

```
your-repo/
├── app/
│   ├── main.py              # Main application
│   ├── config.py            # Configuration
│   ├── auth.py              # Authentication
│   ├── rate_limiter.py      # Rate limiting
│   └── cost_guard.py        # Cost protection
├── utils/
│   └── mock_llm.py          # Mock LLM (provided)
├── Dockerfile               # Multi-stage build
├── docker-compose.yml       # Full stack
├── requirements.txt         # Dependencies
├── .env.example             # Environment template
├── .dockerignore            # Docker ignore
├── railway.toml             # Railway config (or render.yaml)
└── README.md                # Setup instructions
```

**Requirements:**
-  All code runs without errors
-  Multi-stage Dockerfile (image < 500 MB)
-  API key authentication
-  Rate limiting (10 req/min)
-  Cost guard ($10/month)
-  Health + readiness checks
-  Graceful shutdown
-  Stateless design (Redis)
-  No hardcoded secrets

---

### 3. Service Domain Link

Create a file `DEPLOYMENT.md` with your deployed service information:

```markdown
# Deployment Information

## Public URL
https://your-agent.railway.app

## Platform
Railway / Render / Cloud Run

## Test Commands

### Health Check
```bash
curl https://your-agent.railway.app/health
# Expected: {"status": "ok"}
```

### API Test (with authentication)
```bash
curl -X POST https://your-agent.railway.app/ask \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "question": "Hello"}'
```

## Environment Variables Set
- PORT
- REDIS_URL
- AGENT_API_KEY
- LOG_LEVEL

## Screenshots
- [Deployment dashboard](screenshots/dashboard.png)
- [Service running](screenshots/running.png)
- [Test results](screenshots/test.png)
```

##  Pre-Submission Checklist

- [ ] Repository is public (or instructor has access)
- [ ] `MISSION_ANSWERS.md` completed with all exercises
- [ ] `DEPLOYMENT.md` has working public URL
- [ ] All source code in `app/` directory
- [ ] `README.md` has clear setup instructions
- [ ] No `.env` file committed (only `.env.example`)
- [ ] No hardcoded secrets in code
- [ ] Public URL is accessible and working
- [ ] Screenshots included in `screenshots/` folder
- [ ] Repository has clear commit history

---

##  Self-Test

Before submitting, verify your deployment:

```bash
# 1. Health check
curl https://your-app.railway.app/health

# 2. Authentication required
curl https://your-app.railway.app/ask
# Should return 401

# 3. With API key works
curl -H "X-API-Key: YOUR_KEY" https://your-app.railway.app/ask \
  -X POST -d '{"user_id":"test","question":"Hello"}'
# Should return 200

# 4. Rate limiting
for i in {1..15}; do 
  curl -H "X-API-Key: YOUR_KEY" https://your-app.railway.app/ask \
    -X POST -d '{"user_id":"test","question":"test"}'; 
done
# Should eventually return 429
```

---

##  Submission

**Submit your GitHub repository URL:**

```
https://github.com/your-username/day12-agent-deployment
```

**Deadline:** 17/4/2026

---

##  Quick Tips

1.  Test your public URL from a different device
2.  Make sure repository is public or instructor has access
3.  Include screenshots of working deployment
4.  Write clear commit messages
5.  Test all commands in DEPLOYMENT.md work
6.  No secrets in code or commit history

---

##  Need Help?

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review [CODE_LAB.md](CODE_LAB.md)
- Ask in office hours
- Post in discussion forum

---

**Good luck! **
