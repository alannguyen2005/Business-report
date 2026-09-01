# Business Performance Analyst

## Mục tiêu

Mỗi tuần, phân tích kết quả kinh doanh và trả lời đủ **ba câu hỏi**:

1. **Chuyện gì đã xảy ra?** — kết quả kỳ vừa rồi so với cùng kỳ / kỳ trước
2. **Vì sao?** — nguyên nhân gốc, không dừng ở mô tả con số
3. **Sắp tới thế nào và nên làm gì?** — dự báo + khuyến nghị hành động có ước lượng tác động

Output: **1 file HTML report** + **1 file `insights.json`** (nguồn dữ liệu cho email).

---

## Data

Mọi thứ đọc từ `config.yaml` — **KHÔNG hardcode** tên file, tên cột, hay ngưỡng nào.

| Cần gì | Đọc ở đâu trong config.yaml |
|---|---|
| File data | `data.file` |
| Tên run (đặt tên thư mục/report) | `data.stem` |
| Bối cảnh doanh nghiệp | `data.business_context` |
| Cột nào là ngày/doanh thu/lợi nhuận/chiều | `schema.*` |
| Grain, cách so sánh, số finding | `analysis.*` |
| Bật dự báo, tầm dự báo, model | `forecast.*` |
| Số khuyến nghị, có cần sizing không | `strategy.*` |
| Định dạng & thư mục report | `report.*` |

> Đổi sang data khác = sửa `data.file` + `schema` trong config.yaml. Không sửa file này.

---

## Ai chạy bước nào

**GitHub Actions (`weekly_analysis.yml`) chạy tự động Bước 0, 1, 2, 4, 7 mỗi thứ 2.**
Bạn không cần làm lại những bước đó — số liệu đã được tính và commit vào repo.

Việc của agent là **Bước 3** (rà soát narrative) và **Bước 5** (kiểm tra report).
Chỉ chạy lại các bước khác khi Actions lỗi, hoặc khi được yêu cầu chạy tay.

Tài liệu vẫn mô tả đủ 8 bước để khi cần chạy tay thì có đường đi rõ ràng.

---

## Nhiệm vụ khi được gọi

### Bước 0 — Cổng kiểm tra (BẮT BUỘC chạy trước)

```bash
python check_data.py --json
```

Xử lý theo exit code — **không tự suy diễn thay script**:

| Exit | Nghĩa | Làm gì |
|---|---|---|
| `0` (RUN) | Data mới hoặc đã đổi | Tiếp tục Bước 1 |
| `10` (SKIP) | Data không đổi / quá cũ | **Dừng ngay**, báo lý do script in ra, không phân tích |
| `1` (ERROR) | Thiếu file hoặc sai schema | **Dừng ngay**, báo lỗi để người sửa `config.yaml` |

> Muốn phân tích lại dù data không đổi: `python check_data.py --force`.

---

### Bước 1 — Tính toàn bộ con số (deterministic)

```bash
python compute_metrics.py
```

Script này làm sạch data, chấm điểm tin cậy, và tính **mọi** con số cho ba tầng
phân tích. Ghi ra `data/pipeline/{stem}/`:

| File | Nội dung |
|---|---|
| `profile.json` | Vấn đề chất lượng data + grade tin cậy A–F |
| `descriptive_output.json` | Chuỗi theo kỳ, tổng, YoY, xu hướng (có p-value/R²), mùa vụ, cắt lát theo chiều |
| `diagnostic_output.json` | Đóng góp biến động theo chiều, kiểm tra Simpson's paradox, tách sản lượng vs giá trị đơn, rủi ro tập trung |
| `predictive_output.json` | Backtest các model, model thắng, điểm dự báo + khoảng tin cậy |

**Không tự tính lại bất kỳ số nào bằng tay hay bằng code viết tạm.** Script là
nguồn sự thật duy nhất — nhờ vậy tuần này và tuần sau so sánh được với nhau.

**Quy tắc dừng:** script trả exit 1 khi grade = F → dừng, báo data không đủ chất
lượng để kết luận.

---

### Bước 2 — Lắp ráp report và narrative

```bash
python assemble_report.py
```

Đọc 4 file JSON ở Bước 1, ghi ra:

- `chart_specs.json` — dữ liệu 5 chart cho D3
- `report_context.json` — narrative theo schema của skill `html-report`
- `insights.json` — hợp đồng với email (schema ở Bước 7)

Narrative dựng theo luật, không phải template cứng: ví dụ nếu hiệu ứng giá lấn át
hiệu ứng sản lượng thì câu chuyện tự chuyển thành "bào mòn giá trị đơn". Data
tuần sau khác đi thì kết luận cũng khác đi.

---

### Bước 3 — Rà soát và làm sâu narrative (việc của agent)

Đây là nơi agent thực sự đóng góp. Đọc `insights.json` vừa sinh ra và kiểm tra:

1. **Headline có đúng là điều quan trọng nhất không?** Nếu data tuần này có
   chuyện lớn hơn mà luật chưa bắt được → sửa `headline` trong `insights.json`
   và `big_answer` trong `report_context.json`.
2. **Khuyến nghị có thực thi được không?** Loại bỏ hành động chung chung, bổ
   sung ngữ cảnh ngành mà script không biết.
3. **Có finding nào sai hướng không?** Đối chiếu với
   `ai_analyst/.claude/agent-memory/` — nếu dataset đã được phân tích trước đó,
   so với kết luận cũ để phát hiện thay đổi bất thường.

Cần đào sâu hơn thì gọi agent (chỉ khi thật sự cần, xem mục Token efficiency):

| Việc | Agent | Skills |
|---|---|---|
| Nghi ngờ chất lượng data | `data-profiler` | `data-prep`, `validate` |
| Cần drill-down nguyên nhân sâu hơn | `diagnostic-investigator` | `diagnostic`, `size-opportunity` |
| Cần viết lại narrative cho lãnh đạo | `story-builder` | `data-storytelling` |
| Cần thêm/sửa chart | `visualizer` | `chart-data`, `chart-render` |

**Sửa narrative thì sửa vào file JSON, không sửa vào HTML đã render.** Sửa xong
chạy lại Bước 4 để render lại.

---

### Bước 4 — Render report HTML

```bash
python ai_analyst/scripts/render_html.py --stem {stem} --pipeline-dir data/pipeline/{stem} --output data/reports/business_report_{YYYY-MM-DD}.html
```

`--pipeline-dir` là bắt buộc — không có nó script sẽ tìm trong
`ai_analyst/data/pipeline/` chứ không phải repo root.

Report gồm 3 section theo màu: descriptive (xanh dương) → diagnostic (tím) →
predictive (xanh lá), mỗi section có tiêu đề nói kết luận chứ không nói tên chỉ số.

Nếu `report.format` là `pptx` hoặc `both`, chạy thêm
`ai_analyst/scripts/build_pptx_v3.py`.

---

### Bước 5 — Kiểm tra report trước khi gửi

Mở file HTML và xác nhận:

- Không có chuỗi `No data for:` hay `Unsupported type:` hiển thị trong nội dung
  (hai chuỗi này có trong mã JS nhúng — chỉ lỗi khi chúng xuất hiện ở phần thân)
- Số trong report khớp với `data/pipeline/{stem}/*.json`
- Tiếng Việt hiển thị đúng (file phải là UTF-8)

---

### Bước 6 — Schema `insights.json` (hợp đồng với email)

`assemble_report.py` ở Bước 2 đã sinh file này. Mục này là **đặc tả để đối chiếu
khi sửa tay ở Bước 3** — `send_report.py` đọc đúng schema dưới đây, sai một
trường là mục tương ứng biến mất khỏi email.

```json
{
  "generated_at": "2026-09-01",
  "data_period": { "start": "2022-01-01", "end": "2024-06-29" },
  "headline": "Một câu: tình hình cốt lõi + hàm ý.",
  "confidence": { "grade": "C", "note": "lý do ngắn nếu grade là C/D" },
  "kpis": [
    { "label": "Doanh thu", "value": "$1.83M", "delta": "-4.1% so với 2022", "direction": "down" }
  ],
  "executive": {
    "summary": ["Câu văn xuôi cho lãnh đạo — không thuật ngữ, không thống kê."],
    "outlook": "Dự báo nói bằng khoảng, không nêu tên model hay sai số."
  },
  "findings": [
    { "title": "Kết luận, không phải tên chỉ số",
      "detail": "1-2 câu giải thích",
      "evidence": "con số/kiểm định chứng minh" }
  ],
  "forecast": {
    "horizon": "6 tháng",
    "model": "SARIMA(1,1,1)(1,0,0,12)",
    "summary": "1-2 câu về hướng đi và khoảng dự báo",
    "points": [ { "period": "2024-07", "value": 58000, "lo": 51000, "hi": 65000 } ]
  },
  "strategy": [
    { "action": "...", "rationale": "...", "impact": "+$120K/năm",
      "effort": "Trung bình", "owner_hint": "Merchandising", "priority": 1 }
  ],
  "risks": ["..."],
  "report_file": "data/reports/business_report_2026-09-01.html"
}
```

**Hai tầng ngôn ngữ — đây là quy ước quan trọng nhất của file này:**

| Trường | Đi vào đâu | Viết cho ai |
|---|---|---|
| `executive.summary`, `executive.outlook`, `kpis`, `strategy` | **Email** | Lãnh đạo không chuyên về dữ liệu. Cấm dùng: MAPE, p-value, R², tên model, điểm tin cậy, "hiệu ứng giá/sản lượng", "nghịch lý Simpson", AOV, YoY |
| `findings`, `risks`, `confidence` | **Report HTML** | Người muốn kiểm chứng. Bắt buộc kèm bằng chứng thống kê |

Cùng một nguồn số, khác cách kể. Sửa narrative ở Bước 3 phải giữ đúng ranh giới
này — đẩy thuật ngữ vào email là làm hỏng mục đích của nó.

Quy ước khác:

- `direction` chỉ nhận `"up"` / `"down"` / `"flat"` — quyết định màu trong email
- `report_file` là đường dẫn **tương đối từ repo root**, phải trỏ đúng file vừa tạo
- `generated_at` là ngày hôm nay dạng `YYYY-MM-DD` — email bỏ qua report cũ hơn 7 ngày
- Số trong `kpis`/`strategy` là **chuỗi đã format sẵn** (có $, %, dấu phẩy); số trong `forecast.points` là **số thuần** để vẽ chart

---

### Bước 7 — Đóng sổ

```bash
python check_data.py --record      # ghi fingerprint vào logs/last_analyzed.json
git add data/ logs/ && git commit -m "analysis: business review {YYYY-MM-DD}" && git push
```

Chạy `--record` **sau khi** report và `insights.json` đã ghi xong. Chạy sớm sẽ khiến lần chạy lỗi bị đánh dấu là đã hoàn thành.

---

## Agents và skills được phép dùng

Hệ thống agent nằm tại `./ai_analyst`. Đọc `./ai_analyst/CLAUDE.md` để nắm convention trước khi gọi.

Bước 1, 2, 4 là script deterministic — **không cần agent**. Agent chỉ vào cuộc ở
Bước 3, và chỉ khi có lý do cụ thể:

| Khi nào gọi | Agent | Skills |
|---|---|---|
| Nghi ngờ số liệu bất thường, cần soi lại chất lượng data | `data-profiler` | `data-prep`, `validate` |
| Cần drill-down sâu hơn mức script tính | `diagnostic-investigator` | `diagnostic`, `size-opportunity` |
| Cần viết lại narrative cho đối tượng cụ thể | `story-builder` | `data-storytelling` |
| Cần thêm loại chart mới | `visualizer` | `chart-data`, `chart-render`, `html-report` |
| Muốn thay model dự báo bằng SARIMA/Prophet | `predictive-trainer` | `forecast-train`, `model-evaluate` |

**Không gọi** `question-framer` (câu hỏi đã cố định trong file này) và `quality-reviewer` (chỉ gọi khi report ra kết quả bất thường cần thẩm định).

Các bước chạy tuần tự — mỗi bước đọc file mà bước trước ghi ra đĩa. Không có bước nào chạy song song được.

---

## Đổi sang data khác

1. Đặt file mới vào repo, sửa `data.file` trong `config.yaml`
2. Sửa block `schema` cho khớp tên cột mới (bỏ trống trường nào data không có)
3. Sửa `data.business_context` và `data.stem`
4. Push → workflow `validate_data.yml` tự kiểm tra schema và báo lỗi ngay nếu lệch
5. Lần chạy kế tiếp fingerprint đã đổi nên pipeline tự chạy lại từ đầu

Pipeline không giả định gì về ngành hay tên cột — chỉ cần `schema.date` và `schema.revenue` là chạy được. Thiếu `schema.profit` thì bỏ qua phần phân tích biên lợi nhuận, không báo lỗi.

---

## Token efficiency — BẮT BUỘC

- Chỉ gọi 6 agent trong bảng trên. Không chạy `/run` full pipeline của `ai_analyst`.
- Không đọc `references/` của skill trừ khi gặp lỗi thật sự cần tra.
- Đọc memory của agent trong `ai_analyst/.claude/agent-memory/` **trước** khi profile lại data — dataset đã biết thì không phân tích lại từ đầu.
- Không tường thuật từng bước. Chỉ báo khi xong, khi dừng (kèm lý do), hoặc khi lỗi.
- Data lớn: đọc bằng pandas trong Bash, không đọc CSV thô vào context.

---

## Lưu ý

- **Không bịa số.** Mọi con số trong report và `insights.json` phải truy được về file trong `data/pipeline/{stem}/`.
- Nếu một chiều thiếu data ở vài kỳ → note trong `risks`, không im lặng bỏ qua.
- Report đọc trong 5 phút — ưu tiên bảng, chart, bullet. Không viết đoạn văn dài.
- Dữ liệu quá khứ không đảm bảo tương lai: mọi dự báo phải kèm khoảng tin cậy và tên model.
