# Business Performance Pipeline — Hướng dẫn Setup

## Tổng quan

Pipeline chạy **hàng tuần**, trả lời ba câu hỏi: chuyện gì đã xảy ra → vì sao → sắp tới thế nào và nên làm gì.

```
Thứ 2, 08:00  GitHub Actions (weekly_analysis.yml)
              → check_data.py: data có mới không? sai schema không?
              → compute_metrics.py: làm sạch, KPI, YoY, mùa vụ, nguyên nhân,
                backtest 5 model dự báo (SARIMA, Prophet, Holt-Winters...)
              → assemble_report.py: chart + narrative + insights.json
              → render_html.py: report HTML
              → commit kết quả vào repo + upload artifact

Thứ 2, 09:00  GitHub Actions (weekly_email.yml)
              → send_report.py: có insights.json tuần này không?
              → Nếu có → gửi email tóm tắt + đính kèm file report
              → Nếu không → bỏ qua, không báo đỏ

Bất kỳ lúc nào  GitHub Actions (validate_data.yml)
              → Chạy khi push đổi config.yaml hoặc file data
              → Báo lỗi ngay nếu schema lệch

(Tùy chọn)    Claude Routine — rà soát narrative giữa hai mốc trên
              → Xem Bước 5; không bắt buộc, pipeline chạy đủ khi không có
```

> **Vì sao phân tích chạy trên Actions chứ không phải Routine:** `statsmodels`
> và `prophet` cần môi trường có wheel dựng sẵn. Runner Ubuntu x86-64 của
> GitHub có; máy Windows ARM64 và sandbox của Routine thì không chắc. Chạy trên
> Actions là cách duy nhất đảm bảo SARIMA và Prophet thực sự được dùng.

> Mỗi bước tự kiểm tra đầu vào. Bước sau không chạy nếu bước trước chưa có output — email không gửi mail rỗng khi phân tích lỗi.

---

## Cấu trúc repo

```
business-analytics/                   ← GitHub repo root
├── .github/workflows/
│   ├── weekly_analysis.yml           ← thứ 2, 08:00: chạy toàn bộ phân tích
│   ├── weekly_email.yml              ← thứ 2, 09:00: gửi email + report
│   └── validate_data.yml             ← kiểm schema khi đổi data
├── ai_analyst/                       ← bộ máy phân tích (8 agent, 24 skill)
│   └── data/raw/techworld_data.csv   ← data mẫu đang dùng
├── data/
│   ├── pipeline/{stem}/              ← kết quả trung gian + insights.json
│   └── reports/                      ← business_report_YYYY-MM-DD.html
├── logs/
│   └── last_analyzed.json            ← fingerprint lần phân tích gần nhất
├── CLAUDE.md                         ← instructions cho Claude Routine
├── config.yaml                       ← ⭐ nơi duy nhất cần sửa khi đổi data
├── check_data.py                     ← cổng kiểm tra + ghi state
├── compute_metrics.py                ← tính mọi con số (deterministic)
├── assemble_report.py                ← dựng chart + narrative + insights.json
├── send_report.py                    ← gửi email + đính kèm report
├── requirements.txt                  ← cho workflow email (nhẹ)
└── requirements-analysis.txt         ← cho workflow phân tích (có statsmodels, prophet)
```

---

## Bước 1 — Tạo repo và đẩy code

```bash
cd "path/to/github_actions"
git init
git remote add origin https://github.com/your-username/business-analytics.git
git add .
git commit -m "initial setup"
git push -u origin main
```

> Repo nên để **Private** — data kinh doanh không nên public. Repo private free có
> 2000 phút Actions/tháng; pipeline này dùng ~1 phút/tuần, thừa sức trong hạn mức.

---

## Bước 2 — Cấp quyền write cho GitHub Actions

Repo → **Settings** → **Actions** → **General** → **Workflow permissions** → chọn **"Read and write permissions"** → **Save**.

---

## Bước 3 — Kiểm tra data chạy được

Chạy local trước khi lên lịch:

```bash
pip install -r requirements-analysis.txt
python check_data.py --json
```

> Trên Windows ARM64, `statsmodels` và `prophet` sẽ cài lỗi — bỏ qua được.
> Pipeline vẫn chạy, chỉ tự loại 3 model đó và ghi lý do vào phần rủi ro của
> report. Trên GitHub Actions thì cài đủ.

Kết quả mong đợi:

| In ra | Nghĩa |
|---|---|
| `RUN` | Sẵn sàng phân tích |
| `SKIP` | Data không đổi từ lần trước — bình thường |
| `ERROR` | Sai schema hoặc thiếu file — sửa `config.yaml` |

---

## Bước 4 — Setup email

### 4a — Tạo Gmail App Password

Vào https://myaccount.google.com/apppasswords → tạo password tên `business-analytics` → copy 16 ký tự.

> Không thấy mục này: account dùng Passkey hoặc Google Workspace — Google chặn tính năng này, không có workaround.

### 4b — Thêm GitHub Secrets

Repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**:

| Secret name | Value |
|---|---|
| `GMAIL_USER` | your-email@gmail.com |
| `GMAIL_APP_PASSWORD` | 16 ký tự vừa tạo |
| `EMAIL_TO` | email nhận (có thể giống `GMAIL_USER`) |

Email gồm: headline, 4 KPI, các finding chính, dự báo, khuyến nghị hành động, rủi ro — và **file report HTML đính kèm**.

---

## Bước 5 — Chạy thử lần đầu

Đừng chờ đến thứ 2. Chạy tay để biết pipeline hoạt động:

1. Tab **Actions** → **"Weekly Business Analysis"** → **"Run workflow"**
   → tick **force** nếu đã từng chạy rồi
2. Chờ ~1 phút (đo thực tế: cài dependency 24s, phân tích 11s)
3. Mở log step **"Kiểm tra thư viện dự báo"** — phải thấy `OK statsmodels` và `OK prophet`
4. Mở log step **"Tính metrics"** — có bảng so sánh MAPE của cả 5 model và dòng
   `← chọn` ở model thắng
5. Tab **Code** → thư mục `data/reports/` phải có file HTML mới
6. Tab **Actions** → **"Weekly Business Email"** → **"Run workflow"** để test gửi mail

Nếu step nào đỏ, log sẽ nói rõ nguyên nhân — xem mục Troubleshooting bên dưới.

---

## Bước 6 — (Tùy chọn) Claude Routine rà soát narrative

**Không bắt buộc.** Actions đã lo trọn vẹn: tính số, dựng narrative, render report,
gửi mail. Routine chỉ thêm giá trị ở một việc mà script không làm được — đọc lại
kết luận và hỏi "đây có thật là điều quan trọng nhất tuần này không?".

Nếu muốn có, tạo Routine chạy **thứ 2, 08:30** (giữa lúc phân tích xong và lúc mail đi):

| Setting | Giá trị |
|---|---|
| **Trigger** | Weekly, thứ 2, 08:30 |
| **Connector** | repo `business-analytics` |
| **Model** | Sonnet |

Routine cần PAT để push. Tạo tại https://github.com/settings/tokens?type=beta
(**Repository access**: chỉ repo này · **Permissions → Contents**: Read and write),
và allow app tại https://github.com/apps/claude/installations/select_target.

**Instructions:**

```
Trước khi push, chạy lệnh sau để dùng PAT:
git remote set-url origin https://<YOUR_PAT>@github.com/your-username/business-analytics.git

---

GitHub Actions đã chạy phân tích lúc 08:00 và commit kết quả. Việc của bạn là rà
soát, KHÔNG phải tính lại.

1. Đọc data/pipeline/{stem}/insights.json.
2. Kiểm tra 3 điều:
   - headline có đúng là chuyện quan trọng nhất trong data không?
   - mỗi khuyến nghị có thực thi được không, hay chỉ là câu chữ chung chung?
   - có finding nào mâu thuẫn với ai_analyst/.claude/agent-memory/ không?
3. Cần sửa thì sửa vào insights.json và report_context.json — KHÔNG sửa file HTML.
4. Nếu có sửa, render lại (lệnh một dòng):
   python ai_analyst/scripts/render_html.py --stem {stem} --pipeline-dir data/pipeline/{stem} --output data/reports/business_report_{YYYY-MM-DD}.html
5. Commit và push. Nếu không sửa gì thì báo "không có gì cần chỉnh" và dừng.

Không chạy lại compute_metrics.py — số liệu đã có và đã được commit.
Không tường thuật từng bước, chỉ báo kết quả cuối.
```

> Thay `<YOUR_PAT>` và `your-username` bằng thông tin thực. Không share routine
> này với ai. PAT hết hạn → tạo token mới → update Instructions.

---

## Đổi sang data thật

Đây là việc bạn sẽ làm sau khi thử xong với data mẫu.

1. **Đặt file mới** vào repo, ví dụ `data/raw/ket_qua_kinh_doanh.csv`
2. **Sửa `config.yaml`:**
   ```yaml
   data:
     file: data/raw/ket_qua_kinh_doanh.csv
     stem: kqkd
     business_context: >
       Mô tả ngắn về doanh nghiệp, ngành, kênh bán.
   schema:
     date: Ngay_Ban            # đổi cho khớp tên cột thực tế
     date_format: "%d/%m/%Y"
     revenue: Doanh_Thu
     profit: Loi_Nhuan
     dimensions: [Chi_Nhanh, Nhom_Hang, Kenh_Ban]
   ```
3. **Push** → workflow `validate_data.yml` chạy và báo ngay nếu tên cột lệch
4. Lần chạy kế tiếp fingerprint đã đổi → pipeline tự phân tích lại từ đầu

**Yêu cầu tối thiểu của data:** một cột thời gian + một cột doanh thu. Mọi thứ khác là tùy chọn — thiếu `profit` thì bỏ phần phân tích biên lợi nhuận, không báo lỗi.

**Số kỳ tối thiểu để có forecast tin cậy:** 24 kỳ (2 năm theo tháng). Ít hơn thì pipeline vẫn chạy nhưng sẽ ghi cảnh báo vào phần rủi ro.

---

## Tùy chỉnh nhanh

| Muốn thay đổi | Sửa ở đâu |
|---|---|
| File data / tên cột | `config.yaml` → `data.file`, `schema` |
| Grain phân tích (tháng/tuần) | `config.yaml` → `analysis.grain` |
| Tầm dự báo | `config.yaml` → `forecast.horizon` |
| Model dự báo | `config.yaml` → `forecast.models` |
| Số khuyến nghị | `config.yaml` → `strategy.max_actions` |
| Tắt dự báo / chiến lược | `config.yaml` → `forecast.enabled`, `strategy.enabled` |
| Định dạng report (HTML/PPTX) | `config.yaml` → `report.format` |
| Không đính kèm file vào mail | `config.yaml` → `email.attach_report: false` |
| Giờ gửi email | `weekly_email.yml` → `cron` |
| Ngày chạy phân tích | Claude Routine trigger |

---

## Troubleshooting

### `check_data.py` báo ERROR sai schema
Tên cột trong `config.yaml` không khớp file data. Script in ra danh sách cột thực tế có trong file — copy đúng tên vào `schema`.

### `check_data.py` báo SKIP dù muốn chạy lại
Data chưa đổi nên pipeline không chạy lại. Dùng `python check_data.py --force`, hoặc xoá `logs/last_analyzed.json`.

### Email không gửi dù phân tích đã chạy
Kiểm tra `data/pipeline/{stem}/insights.json` có trên GitHub không:
- **Không có** → workflow phân tích lỗi hoặc bị SKIP; xem log "Weekly Business Analysis"
- **Có nhưng cũ hơn 7 ngày** → script cố tình bỏ qua để không gửi lại report cũ
- **Có và mới** → xem log "Weekly Business Email", thường là sai Gmail App Password

### Email gửi được nhưng thiếu phần nào đó
`insights.json` thiếu trường tương ứng. Mỗi phần trong email (KPI, findings, forecast, strategy, risks) tự ẩn nếu trường của nó rỗng — nên mail thiếu mục nghĩa là agent chưa ghi mục đó.

### Report đính kèm quá nặng
Giới hạn 20MB. Vượt thì email vẫn gửi nhưng không kèm file. Giảm số chart hoặc dùng `report.format: html` thay vì `both`.

### Log báo `MISS statsmodels` hoặc `MISS prophet`
Bước cài dependency lỗi. Xem log step "Install dependencies". Thường do pin
version trong `requirements-analysis.txt` xung đột — nới lỏng ràng buộc rồi push lại.
Pipeline vẫn chạy được không có chúng, chỉ là dự báo dùng model đơn giản hơn.

### Report ghi "Model sarima, prophet không chạy được"
Đúng như trên — thư viện chưa cài được. Nếu chạy trên máy Windows ARM64 thì đây
là chuyện bình thường, không sửa được; chạy trên Actions mới có đủ.

### Workflow phân tích báo "Không model dự báo nào chạy được"
Cả 5 model đều lỗi. Gần như chắc chắn là chuỗi thời gian quá ngắn — cần tối thiểu
khoảng 12 kỳ. Kiểm tra `descriptive_output.json` xem `totals.periods` là bao nhiêu,
hoặc tắt tạm bằng `forecast.enabled: false` trong config.yaml.

### Lỗi 403 khi Routine push
Toggle "Allow unrestricted git push" không ổn định — dùng PAT theo Bước 4.
