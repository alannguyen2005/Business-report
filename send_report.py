"""
send_report.py
--------------
Gửi email tóm tắt kết quả kinh doanh + đính kèm file report.

Không tự tính toán gì. Chỉ đọc `insights.json` do pipeline phân tích sinh ra
rồi dựng email — mọi con số trong mail đến từ đúng một nguồn với report.

Input : data/pipeline/{stem}/insights.json  (schema: xem CLAUDE.md)
        data/reports/business_report_{date}.html
Output: email HTML + attachment

Env (GitHub Secrets): GMAIL_USER, GMAIL_APP_PASSWORD, EMAIL_TO

Exit code:
  0 → gửi thành công, HOẶC bỏ qua có lý do chính đáng (chưa có report)
  1 → lỗi gửi mail
"""

import json
import mimetypes
import os
import smtplib
import sys
from datetime import date
from email.message import EmailMessage
from pathlib import Path

import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent
CONFIG = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))

STEM = CONFIG["data"]["stem"]
INSIGHTS_FILE = ROOT / "data" / "pipeline" / STEM / "insights.json"
REPORTS_DIR = ROOT / CONFIG["report"]["output_dir"]
MAX_ATTACHMENT_MB = 20          # giới hạn thực tế của Gmail SMTP
STALE_AFTER_DAYS = 7            # report cũ hơn ngưỡng này thì không gửi lại

# Bảng màu — khớp theme của report để mail và file nhìn cùng một hệ
INK, MUTED, LINE = "#1a1d21", "#6b7280", "#e5e7eb"
UP, DOWN, ACCENT = "#177245", "#b3261e", "#2563eb"


# ─── ĐỌC INSIGHTS ────────────────────────────────────────────────────────────

def load_insights():
    if not INSIGHTS_FILE.exists():
        print("Không tìm thấy data/pipeline/{}/insights.json. "
              "Pipeline phân tích chưa chạy xong — bỏ qua gửi mail.".format(STEM))
        return None
    try:
        data = json.loads(INSIGHTS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print("insights.json hỏng, không parse được: {}. Bỏ qua gửi mail.".format(exc))
        return None

    generated = data.get("generated_at", "")
    try:
        gen_date = date.fromisoformat(str(generated)[:10])
    except (ValueError, TypeError):
        print("insights.json thiếu `generated_at` hợp lệ (nhận: {!r}). "
              "Bỏ qua gửi mail.".format(generated))
        return None

    age = (date.today() - gen_date).days
    if age > STALE_AFTER_DAYS:
        print("Report cũ {} ngày (tạo {}), quá ngưỡng {} ngày. "
              "Pipeline tuần này có thể chưa chạy — bỏ qua.".format(
                  age, gen_date, STALE_AFTER_DAYS))
        return None

    return data


def find_report(insights):
    """Ưu tiên đường dẫn insights khai báo; nếu sai thì lấy file mới nhất."""
    declared = insights.get("report_file")
    if declared:
        path = ROOT / declared
        if path.exists():
            return path
        print("insights.json trỏ tới {} nhưng file không tồn tại — "
              "tìm report mới nhất thay thế.".format(declared))

    if not REPORTS_DIR.exists():
        return None
    candidates = sorted(
        (p for p in REPORTS_DIR.glob("*.html") if p.is_file()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


# ─── DỰNG EMAIL ──────────────────────────────────────────────────────────────

def esc(value):
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def kpi_row(kpis):
    if not kpis:
        return ""
    cells = []
    for k in kpis[:4]:
        direction = (k.get("direction") or "").lower()
        color = UP if direction == "up" else DOWN if direction == "down" else MUTED
        delta = ""
        if k.get("delta"):
            delta = ("<div style=\"color:{};font-size:13px;margin-top:2px\">{}</div>"
                     .format(color, esc(k["delta"])))
        cells.append(
            "<td style=\"padding:12px 16px;border:1px solid {line};vertical-align:top\">"
            "<div style=\"color:{muted};font-size:11px;text-transform:uppercase;"
            "letter-spacing:.4px\">{label}</div>"
            "<div style=\"color:{ink};font-size:20px;font-weight:600;margin-top:4px\">{value}</div>"
            "{delta}</td>".format(
                line=LINE, muted=MUTED, ink=INK, delta=delta,
                label=esc(k.get("label", "")), value=esc(k.get("value", "")))
        )
    return ("<table cellspacing=\"0\" cellpadding=\"0\" style=\"border-collapse:collapse;"
            "width:100%;margin:16px 0\"><tr>{}</tr></table>".format("".join(cells)))


def bullet_section(title, items, renderer):
    if not items:
        return ""
    body = "".join(renderer(item, idx) for idx, item in enumerate(items, 1))
    return ("<h3 style=\"color:{ink};font-size:15px;margin:24px 0 8px\">{title}</h3>"
            "<div>{body}</div>".format(ink=INK, title=esc(title), body=body))


def render_finding(f, idx):
    evidence = ""
    if f.get("evidence"):
        evidence = ("<div style=\"color:{};font-size:12px;margin-top:3px\">{}</div>"
                    .format(MUTED, esc(f["evidence"])))
    return ("<div style=\"margin:0 0 12px;padding-left:12px;border-left:3px solid {line}\">"
            "<div style=\"color:{ink};font-size:14px;font-weight:600\">{idx}. {title}</div>"
            "<div style=\"color:{ink};font-size:13px;margin-top:3px\">{detail}</div>"
            "{evidence}</div>".format(
                line=LINE, ink=INK, idx=idx, evidence=evidence,
                title=esc(f.get("title", "")), detail=esc(f.get("detail", ""))))


def render_action(a, idx):
    meta = " · ".join(
        "{}: {}".format(label, esc(a[key]))
        for key, label in (("impact", "Tác động"), ("effort", "Công sức"),
                           ("owner_hint", "Bộ phận"))
        if a.get(key)
    )
    meta_html = ""
    if meta:
        meta_html = ("<div style=\"color:{};font-size:12px;margin-top:3px\">{}</div>"
                     .format(MUTED, meta))
    rationale = ""
    if a.get("rationale"):
        rationale = ("<div style=\"color:{};font-size:13px;margin-top:3px\">{}</div>"
                     .format(INK, esc(a["rationale"])))
    return ("<div style=\"margin:0 0 12px;padding-left:12px;border-left:3px solid {accent}\">"
            "<div style=\"color:{ink};font-size:14px;font-weight:600\">{idx}. {action}</div>"
            "{rationale}{meta}</div>".format(
                accent=ACCENT, ink=INK, idx=idx, rationale=rationale, meta=meta_html,
                action=esc(a.get("action", ""))))


def build_body(insights, report):
    period = insights.get("data_period") or {}
    period_txt = ""
    if period:
        period_txt = "Dữ liệu {} → {}".format(period.get("start", "?"), period.get("end", "?"))

    conf = insights.get("confidence") or {}
    conf_txt = ""
    if conf.get("grade"):
        conf_txt = " · Độ tin cậy: <b>{}</b>".format(esc(conf["grade"]))
        if conf.get("note"):
            conf_txt += " ({})".format(esc(conf["note"]))

    parts = [
        "<div style=\"font-family:-apple-system,Segoe UI,Arial,sans-serif;"
        "max-width:680px;color:{}\">".format(INK),
        "<h2 style=\"margin:0 0 4px;font-size:19px\">Business Review — {}</h2>".format(
            esc(insights.get("generated_at", ""))),
        "<div style=\"color:{};font-size:12px\">{}{}</div>".format(
            MUTED, esc(period_txt), conf_txt),
    ]

    if insights.get("headline"):
        parts.append(
            "<p style=\"font-size:15px;line-height:1.5;margin:16px 0;padding:12px 16px;"
            "background:#f7f8fa;border-radius:6px\">{}</p>".format(esc(insights["headline"]))
        )

    parts.append(kpi_row(insights.get("kpis") or []))
    parts.append(bullet_section("Phát hiện chính", insights.get("findings") or [], render_finding))

    forecast = insights.get("forecast") or {}
    if forecast.get("summary"):
        parts.append(
            "<h3 style=\"color:{ink};font-size:15px;margin:24px 0 8px\">Dự báo {horizon}</h3>"
            "<div style=\"font-size:13px;line-height:1.5\">{summary}</div>".format(
                ink=INK, horizon=esc(forecast.get("horizon", "")),
                summary=esc(forecast["summary"]))
        )
        if forecast.get("model"):
            parts.append("<div style=\"color:{};font-size:12px;margin-top:3px\">"
                         "Model: {}</div>".format(MUTED, esc(forecast["model"])))

    parts.append(bullet_section("Khuyến nghị hành động",
                                insights.get("strategy") or [], render_action))

    risks = insights.get("risks") or []
    if risks:
        items = "".join("<li style=\"margin-bottom:4px\">{}</li>".format(esc(r)) for r in risks)
        parts.append(
            "<h3 style=\"color:{ink};font-size:15px;margin:24px 0 8px\">Rủi ro cần theo dõi</h3>"
            "<ul style=\"font-size:13px;line-height:1.5;margin:0;padding-left:20px\">{items}</ul>"
            .format(ink=INK, items=items)
        )

    if report:
        parts.append(
            "<p style=\"color:{muted};font-size:12px;margin-top:24px;padding-top:12px;"
            "border-top:1px solid {line}\">Report đầy đủ đính kèm: <b>{name}</b> — "
            "mở bằng trình duyệt.</p>".format(muted=MUTED, line=LINE, name=esc(report.name))
        )

    parts.append("<p style=\"color:{};font-size:11px\">Tự động tạo bởi "
                 "Business Performance Pipeline</p></div>".format(MUTED))
    return "\n".join(p for p in parts if p)


# ─── GỬI ─────────────────────────────────────────────────────────────────────

def send(html_body, subject, attachment):
    try:
        user = os.environ["GMAIL_USER"]
        password = os.environ["GMAIL_APP_PASSWORD"]
    except KeyError as exc:
        raise SystemExit("Thiếu GitHub Secret: {}".format(exc.args[0]))
    to = os.environ.get("EMAIL_TO", user)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to
    msg.set_content("Email này ở định dạng HTML. Xem file report đính kèm.")
    msg.add_alternative(html_body, subtype="html")

    if attachment:
        size_mb = attachment.stat().st_size / 1048576
        if size_mb > MAX_ATTACHMENT_MB:
            print("Report {:.1f}MB vượt giới hạn {}MB — gửi mail không kèm file.".format(
                size_mb, MAX_ATTACHMENT_MB))
        else:
            ctype, _ = mimetypes.guess_type(attachment.name)
            maintype, _, subtype = (ctype or "application/octet-stream").partition("/")
            msg.add_attachment(attachment.read_bytes(), maintype=maintype,
                               subtype=subtype, filename=attachment.name)
            print("Đính kèm {} ({:.2f}MB)".format(attachment.name, size_mb))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
    print("✓ Đã gửi email đến {}".format(to))


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    if not (CONFIG.get("email") or {}).get("enabled", True):
        print("email.enabled = false trong config.yaml — bỏ qua.")
        return 0

    insights = load_insights()
    if insights is None:
        return 0                            # bỏ qua có lý do, không phải lỗi

    report = find_report(insights)
    if report is None:
        print("Không tìm thấy file report nào — vẫn gửi email tóm tắt không đính kèm.")

    subject = CONFIG["email"].get("subject_pattern", "Business Review — {date}").format(
        date=insights.get("generated_at", date.today().isoformat())
    )
    attach = report if CONFIG["email"].get("attach_report", True) else None
    send(build_body(insights, report), subject, attach)
    return 0


if __name__ == "__main__":
    sys.exit(main())
