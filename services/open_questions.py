"""Nghi vấn / quyết định nghiên cứu, tổng hợp cho trang "Giải thích thuật
ngữ" -- bản dịch tiếng Việt và tiếng Nhật tóm tắt, không tự thêm/bớt mục so
với nguồn.

Nguồn duy nhất: deliverables/session00/08_unresolved_decisions_register.md
("Unresolved Decisions Register — Merged", Session 00, 2026-11-04) -- tài
liệu này tự mô tả là "merges, without re-judging, every open item from
Sessions 01-07" (CLAUDE.md mục 3/5: không tự chốt quyết định ở đây, chỉ ghi
lại và chỉ rõ chủ sở hữu). Bản tiếng Nhật (`text_ja`/`owner_ja`) dịch trực
tiếp từ cùng nguồn gốc tiếng Anh này (không dịch gián tiếp qua bản tiếng
Việt, để tránh lệch nghĩa qua 2 lượt dịch) -- thêm 2026-11-08.

Phạm vi lấy vào: chỉ phần A (quyết định nghiên cứu/lâm sàng), B (logic tìm
kiếm D1-D4/Q/QC) và C (mô hình dữ liệu CSV) của tài liệu gốc -- đây là các
mục ảnh hưởng trực tiếp tới việc đọc/diễn giải kết quả tìm kiếm. Phần D
(INT-00-xx, phát hiện ở mức triển khai/code/tài liệu) và E (housekeeping)
là backlog kỹ thuật/QA, không phải nghi vấn nghiên cứu -- xem thẳng file gốc
nếu cần đầy đủ cả 5 phần.

Mỗi mục giữ nguyên trạng thái như ghi trong tài liệu gốc (status_raw, tiếng
Anh, nguyên văn) để tra cứu chéo -- không tự nâng mục nào lên "đã xác minh".

Mục D (thêm 2026-11-12, nguồn riêng -- KHÔNG từ 08_unresolved_decisions_
register.md ở trên): trạng thái migrate sang model v1.3.1 (1 trục
D4_注射区分 + group theo tháng, thay 3-trục Q10/Q20/Q30/D3-matrix cũ ở mục
A/B/C bên trên). Lấy trực tiếp, không diễn giải thêm, từ Mục 0 ("Đã giải
quyết" + "Còn tồn đọng") và Mục 5 ("Decisions required") của
deliverables/session00/15_addendum_v1.3.1_migration_plan_2026-11-11.md --
addendum này tự ghi rõ là "Phân tích khác biệt + kế hoạch sửa (plan only)",
không tự phê duyệt mục nào; các mục đánh "✅ ĐÃ XỬ LÝ"/"Resolved" trong mục D
dưới đây đã được xác nhận trực tiếp trong văn bản addendum đó.
"""
from __future__ import annotations

from dataclasses import dataclass

STATUS_UNVERIFIED = "unverified"  # "Open..." trong tài liệu gốc
STATUS_RESOLVED = "resolved"      # "Resolved..." / "Confirmed..."
STATUS_PROPOSED = "proposed"      # "Proposed, unapproved" / "...blocked on..."


@dataclass(frozen=True)
class OpenQuestion:
    id: str
    section: str  # "A" | "B" | "C"
    status_bucket: str  # STATUS_*
    status_raw: str  # nguyên văn tiếng Anh từ tài liệu gốc, giữ để tra cứu chéo
    text_vi: str  # nội dung mục (dịch tóm tắt) -- với mục đã chốt, đây chính là thông tin xác nhận
    text_ja: str  # bản dịch tiếng Nhật, dịch trực tiếp từ nguồn tiếng Anh (không qua text_vi)
    owner_vi: str
    owner_ja: str


SECTIONS: dict[str, dict[str, str]] = {
    "A": {"vi": "A. Quyết định nghiên cứu / lâm sàng (model v1.0)", "ja": "A. 研究・臨床上の決定（v1.0モデル）"},
    "B": {"vi": "B. Logic tìm kiếm D1–D4 / Q / QC (model v1.0)", "ja": "B. D1〜D4／Q／QC 検索ロジック（v1.0モデル）"},
    "C": {"vi": "C. Mô hình dữ liệu CSV / xuất dữ liệu (model v1.0)", "ja": "C. CSVデータモデル／出力（v1.0モデル）"},
    "D": {
        "vi": "D. Migrate v1.3.1 — đã giải quyết & còn tồn đọng (addendum 15, 2026-11-11)",
        "ja": "D. v1.3.1移行 — 解決済み・未解決（addendum15、2026-11-11）",
    },
}

SECTION_OWNERS_VI: dict[str, str] = {
    "A": "Chủ dự án / bác sĩ",
    "B": "Chủ dự án",
    "C": "Chủ dự án / phụ trách bảo mật dữ liệu",
    "D": "Mixed — xem addendum 15 Mục 5",
}

SECTION_OWNERS_JA: dict[str, str] = {
    "A": "チーム責任者／医師",
    "B": "チーム責任者",
    "C": "チーム責任者／データ保護担当",
    "D": "混在 — addendum15 Mục5参照",
}

SOURCE_FILE = "deliverables/session00/08_unresolved_decisions_register.md"
SOURCE_FILE_V131 = "deliverables/session00/15_addendum_v1.3.1_migration_plan_2026-11-11.md"

_OWNER_PROJECT_DOCTOR_VI = "Chủ dự án / bác sĩ"
_OWNER_PROJECT_DOCTOR_JA = "チーム責任者／医師"
_OWNER_PROJECT_VI = "Chủ dự án"
_OWNER_PROJECT_JA = "チーム責任者"
_OWNER_MASTER_DOC_VI = "Người giữ Master Document"
_OWNER_MASTER_DOC_JA = "マスタードキュメント管理者"
_OWNER_PROJECT_SECURITY_VI = "Chủ dự án / phụ trách bảo mật dữ liệu"
_OWNER_PROJECT_SECURITY_JA = "チーム責任者／データ保護担当"
_OWNER_ENGINEER_VI = "Engineer"
_OWNER_ENGINEER_JA = "エンジニア"

QUESTIONS: list[OpenQuestion] = [
    # ------------------------------------------------------------ A. Nghiên cứu/lâm sàng
    OpenQuestion("UQ01", "A", STATUS_UNVERIFIED, "Open",
                 "Mức khuyến cáo CQ18 (hướng dẫn điều trị viêm phổi 2024) về bao phủ vi khuẩn kỵ khí cho viêm phổi "
                 "hít — chưa xác nhận.",
                 "2024年肺炎診療ガイドラインCQ18：誤嚥性肺炎における嫌気性菌カバーの推奨度 — 未確認。",
                 _OWNER_PROJECT_DOCTOR_VI, _OWNER_PROJECT_DOCTOR_JA),
    OpenQuestion("UQ02", "A", STATUS_UNVERIFIED, "Open",
                 "Tài liệu hướng dẫn sử dụng kháng sinh hợp lý, mục 6(2) (\"sử dụng phù hợp trong chăm sóc tại "
                 "nhà\") — nội dung chưa xác nhận.",
                 "抗菌薬適正使用の手引き 6(2)項（「在宅医療における適正使用」）— 内容未確認。",
                 _OWNER_PROJECT_DOCTOR_VI, _OWNER_PROJECT_DOCTOR_JA),
    OpenQuestion("UQ03", "A", STATUS_UNVERIFIED, "Open",
                 "9 thành phần chưa xác nhận của D2-3 (U01–U09) — tên sản phẩm thương mại thật chưa xác nhận.",
                 "D2-3の未確認9成分（U01〜U09）— 実際の販売名が未確認。",
                 _OWNER_PROJECT_DOCTOR_VI, _OWNER_PROJECT_DOCTOR_JA),
    OpenQuestion("UQ04", "A", STATUS_UNVERIFIED, "Open (không chặn triển khai)",
                 "Chữ số 5–7 của mã YJ = 400–699 có phải định nghĩa chính thức cho \"dạng tiêm\" hay không — câu "
                 "hỏi ở mức tài liệu, còn mở nhưng không chặn việc triển khai hiện tại.",
                 "YJコード5〜7桁目＝400〜699が「注射剤」の正式な定義か — 文書レベルの論点で未解決だが、現行実装は"
                 "妨げない。",
                 _OWNER_PROJECT_DOCTOR_VI, _OWNER_PROJECT_DOCTOR_JA),
    OpenQuestion("UQ05", "A", STATUS_UNVERIFIED, "Open",
                 "Tên hiển thị thật trên ORCA của D4-3 (P20–P24) — chưa xác nhận.",
                 "D4-3（P20〜P24）のORCA実際の表示名 — 未確認。",
                 _OWNER_PROJECT_DOCTOR_VI, _OWNER_PROJECT_DOCTOR_JA),
    OpenQuestion("UQ06", "A", STATUS_RESOLVED, "Resolved (Session02)",
                 "Đã xác nhận: `medication_code` là mã theo bảng tính phí (receipt code), không phải mã YJ; không "
                 "có cột riêng cho loại tính phí.",
                 "確認済み：`medication_code` はレセプト（請求）コードであり、YJコードではない。請求区分専用の列"
                 "は存在しない。",
                 _OWNER_PROJECT_DOCTOR_VI, _OWNER_PROJECT_DOCTOR_JA),
    OpenQuestion("UQ07", "A", STATUS_UNVERIFIED, "Open",
                 "Tìm kiếm bệnh danh có tôn trọng khoảng thời gian hay không, và cách xử lý ký tự toàn/nửa độ rộng "
                 "— cần kiểm thử trực tiếp trên công cụ.",
                 "病名検索が期間条件を考慮しているか、全角／半角の扱いはどうか — ツールでの直接検証が必要。",
                 _OWNER_PROJECT_DOCTOR_VI, _OWNER_PROJECT_DOCTOR_JA),
    OpenQuestion("UQ08", "A", STATUS_UNVERIFIED, "Open",
                 "R05 — Ngày 30 được tính bao gồm (0–30) hay không bao gồm (0–29)?",
                 "R05 — 30日目を含める（0〜30日）か含めない（0〜29日）か？",
                 _OWNER_PROJECT_DOCTOR_VI, _OWNER_PROJECT_DOCTOR_JA),
    OpenQuestion("UQ09", "A", STATUS_UNVERIFIED, "Open",
                 "R09 — Trường hợp chỉ truyền dịch (không kháng sinh): đưa vào phân tích chính hay lập bảng "
                 "riêng?",
                 "R09 — 補液のみ（抗菌薬なし）の症例：主解析に含めるか、別集計にするか？",
                 _OWNER_PROJECT_DOCTOR_VI, _OWNER_PROJECT_DOCTOR_JA),
    OpenQuestion("UQ10", "A", STATUS_UNVERIFIED, "Open",
                 "R10 — Đường dùng tiêm bắp/dưới da (IM/SC) có được tính chung với tiêm tĩnh mạch (IV) không?",
                 "R10 — 筋注／皮下注（IM／SC）を静脈注射（IV）と同じ扱いにするか？",
                 _OWNER_PROJECT_DOCTOR_VI, _OWNER_PROJECT_DOCTOR_JA),
    OpenQuestion("UQ11", "A", STATUS_UNVERIFIED, "Open",
                 "R11 — Các phân loại D1 PL/LB: đưa vào phân tích chính hay lập bảng riêng?",
                 "R11 — D1のPL／LB分類：主解析に含めるか、別集計にするか？",
                 _OWNER_PROJECT_DOCTOR_VI, _OWNER_PROJECT_DOCTOR_JA),
    OpenQuestion("UQ12", "A", STATUS_UNVERIFIED, "Open",
                 "Phạm vi bệnh: chỉ viêm phổi, hay gồm cả đợt cấp COPD/viêm phế quản cấp?",
                 "対象疾患の範囲：肺炎のみか、COPD急性増悪／急性気管支炎も含むか？",
                 _OWNER_PROJECT_DOCTOR_VI, _OWNER_PROJECT_DOCTOR_JA),
    OpenQuestion("UQ13", "A", STATUS_UNVERIFIED, "Open (trùng UQ10, góc nhìn thiết kế công cụ)",
                 "Phạm vi \"truyền kháng sinh\" — lấy IV làm chuẩn; có tách riêng IM/SC/đường trung tâm không?",
                 "「抗菌薬点滴」の範囲 — IVを基準とし、IM／SC／中心静脈ルートを別立てにするか？",
                 _OWNER_PROJECT_DOCTOR_VI, _OWNER_PROJECT_DOCTOR_JA),
    OpenQuestion("UQ14", "A", STATUS_RESOLVED, "Resolved (Session02)",
                 "Đã xác nhận: độ chi tiết nguồn dữ liệu/ngày tháng chỉ có `perform_month`, `medical_records` "
                 "không có ngày dùng thuốc thật.",
                 "確認済み：データソースの日付粒度は `perform_month`（月単位）のみ。`medical_records` に実投与日"
                 "は存在しない。",
                 _OWNER_PROJECT_DOCTOR_VI, _OWNER_PROJECT_DOCTOR_JA),
    OpenQuestion("UQ15", "A", STATUS_UNVERIFIED, "Open",
                 "Xử lý \"candidate-event\": định nghĩa `candidate_id`, đặc tả cột CSV — Session 05 đã giải quyết "
                 "phần lớn qua data model, chỉ còn chờ chủ dự án ký xác nhận chính thức để đóng hẳn.",
                 "「候補イベント（candidate-event）」の扱い：`candidate_id` の定義、CSV列仕様 — Session05のデー"
                 "タモデルでほぼ解決済み、正式クローズにはチーム責任者の最終承認待ち。",
                 _OWNER_PROJECT_VI, _OWNER_PROJECT_JA),
    OpenQuestion("UQ16", "A", STATUS_UNVERIFIED, "Open",
                 "Tiêu chí rà soát thủ công cuối cùng: thuộc diện/không thuộc diện/tạm giữ, Day0, ranh giới đợt "
                 "điều trị, biên 30 ngày, cách xử lý mất dấu theo dõi.",
                 "最終的な診療録レビュー基準：対象／対象外／保留、Day 0、エピソード境界、30日境界、追跡不能の扱"
                 "い。",
                 _OWNER_PROJECT_DOCTOR_VI, _OWNER_PROJECT_DOCTOR_JA),
    OpenQuestion("UQ17", "A", STATUS_UNVERIFIED, "Open",
                 "Truy cập/bảo vệ dữ liệu: ai được xem dữ liệu nguồn, quy trình phê duyệt xuất dữ liệu, lưu trữ/"
                 "truy cập/ghi log cho file CSV.",
                 "アクセス・データ保護：元データの閲覧権限者、CSV出力の承認プロセス、保存・アクセス・ログ記録。",
                 _OWNER_PROJECT_VI, _OWNER_PROJECT_JA),
    OpenQuestion("UQ18", "A", STATUS_UNVERIFIED, "Open",
                 "Quy tắc 14 ngày cho \"đợt điều trị mới\" của R04 — cần xác nhận lại trước khi áp dụng chính "
                 "thức.",
                 "R04の「14日ルール」（新規エピソード判定）— 正式運用前に再確認が必要。",
                 _OWNER_PROJECT_DOCTOR_VI, _OWNER_PROJECT_DOCTOR_JA),
    OpenQuestion("UQ19", "A", STATUS_UNVERIFIED, "Open (cơ chế DB đã xong, câu hỏi nghiệp vụ còn mở)",
                 "Định danh xuyên cơ sở: khóa `(clinic_id, patient_id)` đã triển khai (REQ08), nhưng câu hỏi "
                 "nghiệp vụ \"cùng ID nhưng khác người giữa các cơ sở\" vẫn còn mở.",
                 "施設横断の患者識別：`(clinic_id, patient_id)` キーはDB実装済み（REQ08）。ただし「施設間で同一"
                 "IDでも別人」という業務上の論点は未解決。",
                 _OWNER_PROJECT_VI, _OWNER_PROJECT_JA),
    OpenQuestion("UQ20", "A", STATUS_UNVERIFIED, "Open",
                 "Chi tiết quy trình xác nhận mất dấu theo dõi (lost-to-follow-up) của R07.",
                 "R07の追跡不能（lost-to-follow-up）確認プロセスの詳細。",
                 _OWNER_PROJECT_DOCTOR_VI, _OWNER_PROJECT_DOCTOR_JA),
    OpenQuestion("UQ21", "A", STATUS_UNVERIFIED, "Open",
                 "Không tìm thấy bản đầy đủ của Kế hoạch phát triển nghiên cứu (nguồn của R01/R06/R08) trong "
                 "`document/A/` — cần xác nhận có tồn tại bản đầy đủ để đối chiếu hay không.",
                 "`document/A/` に研究開発計画の完全版が見当たらない（R01／R06／R08の出典）— 完全版の有無を確認"
                 "する必要あり。",
                 _OWNER_PROJECT_VI, _OWNER_PROJECT_JA),
    OpenQuestion("UQ22", "A", STATUS_UNVERIFIED, "Open, đang áp dụng quy tắc tạm thời",
                 "Ý nghĩa tiền tố `ZZZ` trong `disease_code` chưa xác nhận; quy tắc tạm thời đang áp dụng: gắn cờ "
                 "`flag_zzz_pending_confirmation=Y`, không tự phân loại (đã triển khai trong code).",
                 "`disease_code` の `ZZZ` 接頭辞の意味が未確認。暫定運用中：`flag_zzz_pending_confirmation=Y` を"
                 "付与し自動分類はしない（実装済み）。",
                 _OWNER_PROJECT_DOCTOR_VI, _OWNER_PROJECT_DOCTOR_JA),
    OpenQuestion("UQ23", "A", STATUS_UNVERIFIED, "Open",
                 "Ý nghĩa `perform_count` trong bảng thô — cần xác nhận bằng văn bản chính thức từ người giữ "
                 "Master Document trước khi dùng trong công bố hoặc UI (REQ10).",
                 "元テーブルの `perform_count` の意味 — 公表・UIでの利用（REQ10）前に、マスタードキュメント管理"
                 "者からの正式な書面確認が必要。",
                 _OWNER_PROJECT_DOCTOR_VI, _OWNER_PROJECT_DOCTOR_JA),

    # ------------------------------------------------------------ B. Logic tìm kiếm D1-D4/Q/QC
    OpenQuestion("DEC-04-01", "B", STATUS_RESOLVED, "Confirmed (ở mức session, chưa ở mức Master Document)",
                 "Đã chốt (tạm, mức session): \"Tập C\" QC1/QC2 là phần mở rộng tạm định (暫定), KHÔNG chính thức "
                 "của bảng 7-1 Master Document.",
                 "確定済み（セッションレベル、Master Document未承認）：QC1／QC2「セットC」は表7-1の暫定・非公式"
                 "拡張として導入。",
                 _OWNER_PROJECT_VI, _OWNER_PROJECT_JA),
    OpenQuestion("DEC-04-02", "B", STATUS_RESOLVED, "Confirmed (ở mức session)",
                 "Đã chốt (mức session): dùng `exclusion_granularity` cấp tháng làm xấp xỉ thực tế gần nhất cho "
                 "loại trừ cấp bản ghi (REQ11).",
                 "確定済み（セッションレベル）：レコード単位の除外に対する実務上の近似として、月単位の "
                 "`exclusion_granularity` を採用（REQ11）。",
                 _OWNER_PROJECT_VI, _OWNER_PROJECT_JA),
    OpenQuestion("OPEN-04-01", "B", STATUS_UNVERIFIED, "Open",
                 "Chuỗi mã tính phí C005-2 của QC2 chưa được xác minh với dữ liệu `medication_name` thật.",
                 "QC2のC005-2請求コード文字列は、実際の `medication_name` データで未検証。",
                 _OWNER_PROJECT_VI, _OWNER_PROJECT_JA),
    OpenQuestion("OPEN-04-02", "B", STATUS_RESOLVED,
                 "Resolved by this integration — xác nhận là KHÔNG thể thỏa mãn",
                 "Đã xác nhận: không thể ánh xạ D4-1 (P01–P11) lên cột DB — `medication_code` không có mức chi "
                 "tiết phụ ở bất kỳ dòng nào, kể cả nhóm 31/32/33. Đây là giới hạn dữ liệu vĩnh viễn, không phải "
                 "lỗi có thể sửa.",
                 "確認済み（本統合で「対応不可能」と確定）：D4-1（P01〜P11）をDB列にマッピングすることは不可能"
                 " — クラス31／32／33を含め、どの行にも `medication_code` のサブコード粒度が存在しない。これは"
                 "恒久的なデータ上の制約であり、修正可能な不具合ではない。",
                 _OWNER_MASTER_DOC_VI, _OWNER_MASTER_DOC_JA),
    OpenQuestion("OPEN-04-03", "B", STATUS_UNVERIFIED, "Open",
                 "Vai trò của Q01: rút về làm fixture hồi quy, hay tiếp tục chạy song song chính thức cùng Q30?",
                 "Q01の位置づけ：回帰テスト用フィクスチャとして退役させるか、Q30と並行して本番運用を続けるか？",
                 _OWNER_PROJECT_VI, _OWNER_PROJECT_JA),

    # ------------------------------------------------------------ C. Mô hình dữ liệu CSV
    OpenQuestion("DEC-05-01", "C", STATUS_PROPOSED, "Proposed, unapproved",
                 "Đề xuất, CHƯA phê duyệt: phạm vi Candidate CSV = hợp của cả 7 ô ma trận, hay chỉ Q30 + báo cáo "
                 "riêng?",
                 "提案中（未承認）：Candidate CSVの範囲＝マトリクス全7セルの和集合か、Q30のみ＋別報告か？",
                 _OWNER_PROJECT_VI, _OWNER_PROJECT_JA),
    OpenQuestion("DEC-05-02", "C", STATUS_RESOLVED, "Confirmed",
                 "Đã chốt: công cụ không tự tạo bất kỳ gợi ý ranh giới đợt điều trị nào (tuân thủ CLAUDE.md).",
                 "確定済み：ツールはエピソード境界の提案を一切自動生成しない（CLAUDE.md準拠）。",
                 _OWNER_PROJECT_VI, _OWNER_PROJECT_JA),
    OpenQuestion("DEC-05-03", "C", STATUS_PROPOSED, "Proposed, blocked on R05",
                 "Đề xuất, đang chờ R05: `observation_window_definition` hỗ trợ rõ cả 2 cách tính 0–30/0–29 theo "
                 "từng dòng — không chặn thiết kế CSV.",
                 "提案中（R05待ち）：`observation_window_definition` で行ごとに0〜30／0〜29の両方の計算方法を明"
                 "示的にサポート — CSV設計自体は妨げない。",
                 _OWNER_PROJECT_VI, _OWNER_PROJECT_JA),
    OpenQuestion("OPEN-05-01", "C", STATUS_UNVERIFIED, "Open",
                 "Rủi ro tái định danh: `candidate_id` gần như định danh được cá nhân ở cơ sở nhỏ (vd "
                 "`clinic_sanjou`, 16 bệnh nhân) — cần bước kiểm soát truy cập/thỏa thuận chia sẻ dữ liệu trước "
                 "khi xuất ra ngoài.",
                 "再識別リスク：小規模施設（例：`clinic_sanjou`、16名）では `candidate_id` が個人をほぼ特定でき"
                 "てしまう — 外部出力前にアクセス制御／データ共有契約（DSA）の手順が必要。",
                 _OWNER_PROJECT_SECURITY_VI, _OWNER_PROJECT_SECURITY_JA),
    OpenQuestion("OPEN-05-02", "C", STATUS_UNVERIFIED, "Open",
                 "Vị trí lưu trữ/truy cập cho CSV Rà soát thủ công + Kết cục (chi tiết lâm sàng nhiều hơn "
                 "Candidate CSV).",
                 "診療録レビューCSV・転帰CSV（Candidate CSVより臨床詳細が多い）の保存・アクセス場所が未定。",
                 _OWNER_PROJECT_SECURITY_VI, _OWNER_PROJECT_SECURITY_JA),
    OpenQuestion("OPEN-05-03", "C", STATUS_UNVERIFIED, "Open",
                 "Chính sách lưu giữ nhiều lượt chạy (run) — chưa có lịch dọn dẹp.",
                 "複数回実行（run）のデータ保持ポリシー — 削除スケジュール未定義。",
                 _OWNER_PROJECT_SECURITY_VI, _OWNER_PROJECT_SECURITY_JA),
    OpenQuestion("INT-00-04", "C", STATUS_UNVERIFIED, "Open, mitigated 2026-11-08",
                 "`clinic_cl222`/`clinic_cl223`/`clinic_cl228` có dữ liệu bệnh nhân thật (229/354/408 người) "
                 "nhưng không có dòng trong `clinic_master` — trước đây bị loại âm thầm khỏi mọi filter/tìm "
                 "kiếm. Đã xác nhận bằng dữ liệu (medical_points, tỉ lệ thuốc uống, cửa sổ crawl) là thuộc "
                 "nhóm HOMIS. Đã thêm placeholder `[UNVERIFIED] clinic_<id>` vào filter "
                 "(`rules/clinic_master_overrides.csv`) để không còn bị bỏ sót, nhưng tên cơ sở thật vẫn "
                 "chưa xác nhận ở bất kỳ đâu trong DB/repo — cần tra từ hệ thống ORCA gốc rồi backfill "
                 "`clinic_master`.",
                 "`clinic_cl222`／`clinic_cl223`／`clinic_cl228` には実患者データ（229／354／408名）がある"
                 "が `clinic_master` に行が無いため、従来は全てのフィルター・検索から静かに除外されていた。"
                 "データ（`medical_points` の有無、内服薬比率、クロール期間）からHOMISグループに属すると確認"
                 "済み。`rules/clinic_master_overrides.csv` にプレースホルダー `[UNVERIFIED] clinic_<id>` を"
                 "追加し、フィルターから漏れないようにしたが、施設の正式名称はDB・リポジトリのどこにも存在せ"
                 "ず未確認のまま — 元のORCAシステムで確認後、`clinic_master` へ反映する必要がある。",
                 _OWNER_PROJECT_VI, _OWNER_PROJECT_JA),

    # ------------------------------------------------------------ D. Migrate v1.3.1 (addendum 15)
    # Nguồn: 15_addendum_v1.3.1_migration_plan_2026-11-11.md Mục 0 ("Đã giải quyết" + "Còn tồn
    # đọng") và Mục 5 ("Decisions required") -- xem SOURCE_FILE_V131. Không trộn với A/B/C (model
    # v1.0 cũ) ở trên.
    OpenQuestion("V131-R1", "D", STATUS_RESOLVED, "Resolved (addendum 15 Mục 0, commit aee43e9/9c49b46)",
                 "Kiến trúc trích xuất candidate đã viết lại hoàn toàn: 1 trục duy nhất (bản ghi tính tiền "
                 "kháng sinh tiêm/truyền, lọc qua D4_注射区分) + group theo tháng liên tục — thay cho 3 trục "
                 "Q10(病名)/Q20(薬剤)/Q30(AND)/D3-matrix cũ. Test thật: 422 candidate trên 3 clinic/~1.1M dòng DB.",
                 "候補抽出のアーキテクチャを全面的に書き直し：D4_注射区分でフィルタした注射用抗菌薬の算定記録"
                 "のみを使う単一軸＋連続月のグルーピングに統一（旧Q10（病名）／Q20（薬剤）／Q30（AND）／D3マ"
                 "トリクスの3軸モデルを廃止）。3施設・実DB約110万行で試行し候補422件を抽出済み。",
                 _OWNER_ENGINEER_VI, _OWNER_ENGINEER_JA),
    OpenQuestion("V131-R2", "D", STATUS_RESOLVED, "Resolved (commit c23c53e)",
                 "D1/D3/D4 dictionary (+D6 mới, DRAFT) đã đồng bộ với 検索ツール辞書v1.3.1.xlsx — D4 đổi hẳn "
                 "từ \"loại thủ thuật tham khảo P01-P24\" sang \"mã tính tiền ORCA .310-.350 → "
                 "candidate_eligible + A13投与経路\". Nội dung bệnh danh/thành phần/điều kiện tìm không đổi.",
                 "D1／D3／D4辞書（＋新規D6、DRAFT）を検索ツール辞書v1.3.1.xlsxに同期済み — D4は旧「参考の手"
                 "技種別P01〜P24」から「ORCA算定コード.310〜.350→candidate_eligible＋A13投与経路」へ完全に変"
                 "更。病名・成分・検索語・判定表の内容自体は変更なし。",
                 _OWNER_ENGINEER_VI, _OWNER_ENGINEER_JA),
    OpenQuestion("V131-R3", "D", STATUS_RESOLVED, "Resolved (commit 3846acd/b1a6b65)",
                 "Schema CSV mới: 1 file 41 cột thống nhất (A01-A17 tool xuất, B01-B22 reviewer nhập, C01-C02 "
                 "QC) + 1 file covariate riêng, thay cho 6 file CSV rời (Candidate/3 Evidence/Manual Review/"
                 "Outcome) cũ.",
                 "新CSVスキーマ：統一41列1ファイル（ツール出力A01〜A17、レビュー入力B01〜B22、QC C01〜C02）"
                 "＋別ファイルのcovariate、旧6分割CSV（候補／エビデンス3種／診療録レビュー／転帰）を置き換え。",
                 _OWNER_ENGINEER_VI, _OWNER_ENGINEER_JA),
    OpenQuestion("V131-R4", "D", STATUS_RESOLVED, "Resolved (commit b1a6b65/4c9035b/74809b8)",
                 "6 trang app/pages/*.py, exports/export_csv.py, review_template.py, qc_checks.py (V01-V09 "
                 "mới) và toàn bộ tests/ đã viết lại theo model mới — 81 test pass (1 skip không liên quan), "
                 "không còn import vỡ.",
                 "app/pages/*.pyの6ページ、exports/export_csv.py、review_template.py、新規qc_checks.py"
                 "（V01〜V09）、tests/一式を新モデルに合わせて書き直し済み — テスト81件成功（無関係なスキッ"
                 "プ1件）、importの破損なし。",
                 _OWNER_ENGINEER_VI, _OWNER_ENGINEER_JA),
    OpenQuestion("V131-R5", "D", STATUS_RESOLVED, "✅ ĐÃ XỬ LÝ (commit b2041e5, 2026-11-11)",
                 "Rủi ro tuân thủ dữ liệu cá nhân: scripts/build_reference.py (đọc patient_name trực tiếp, "
                 "không mode=ro, ghi ra reference/*.csv không nằm trong .gitignore) đã bị xoá. Đã xác nhận "
                 "reference/ chưa từng bị commit.",
                 "個人情報コンプライアンスリスク：scripts/build_reference.py（patient_nameを直接読み取り、"
                 "mode=roなし、.gitignore対象外のreference/*.csvへ出力）を削除済み。reference/ ディレクトリが"
                 "コミットされたことは一度もないことを確認済み。",
                 _OWNER_PROJECT_SECURITY_VI, _OWNER_PROJECT_SECURITY_JA),
    OpenQuestion("V131-R6", "D", STATUS_RESOLVED, "✅ ĐÃ XỬ LÝ (2026-11-11, xác nhận bởi chủ dự án)",
                 "CLAUDE.md §2 (nguồn ưu tiên) đã được chủ dự án xác nhận cập nhật: 手順書v1.3.1.docx là 正本 "
                 "mới, các tài liệu v1.3.1 khác xếp theo vai trò, Master Document v1.0 hạ xuống \"chỉ tham "
                 "khảo lịch sử\".",
                 "CLAUDE.md §2（優先ソース）はチーム責任者の確認を得て更新済み：手順書v1.3.1.docxが新しい正"
                 "本となり、他のv1.3.1文書は役割別に整理、v1.0マスタードキュメントは「歴史的参考のみ」に格下"
                 "げ。",
                 _OWNER_PROJECT_VI, _OWNER_PROJECT_JA),
    OpenQuestion("V131-T1", "D", STATUS_RESOLVED, "Resolved (cập nhật trong phiên này, 2026-11-12)",
                 "Nội dung diễn giải trang \"Giải thích thuật ngữ\" (Tổng quan pipeline, Cách hoạt động, "
                 "banner cảnh báo) mô tả model v1.0 cũ (Tập A/B/C, Q30, D3-certainty) — đã viết lại theo model "
                 "v1.3.1; mục D này thay cho banner cảnh báo \"lỗi thời\" cũ.",
                 "「用語解説」ページの説明内容（パイプライン概要、仕組み、警告バナー）が旧v1.0モデル（集合A/"
                 "B/C、Q30、D3確からしさ）を説明していた点は、今回の更新でv1.3.1モデルに合わせて書き直し済"
                 "み。このD項が旧警告バナーの代わりとなる。",
                 _OWNER_ENGINEER_VI, _OWNER_ENGINEER_JA),
    OpenQuestion("V131-T2", "D", STATUS_UNVERIFIED, "Open",
                 "Chưa tạo addendum riêng cho session 01/02/06/07/09 (deliverables Markdown) như đề xuất ở "
                 "addendum 15 Mục 4 — chỉ phần code (dictionaries/rules/models/services/exports/app/tests) đã "
                 "làm trực tiếp.",
                 "addendum15 Mục4の提案どおり、session01／02／06／07／09用の個別addendum（Markdown "
                 "deliverable）はまだ作成されていない — コード部分（dictionaries/rules/models/services/"
                 "exports/app/tests）のみ直接実装済み。",
                 _OWNER_ENGINEER_VI, _OWNER_ENGINEER_JA),
    OpenQuestion("V131-T3", "D", STATUS_UNVERIFIED, "Open",
                 "Chưa chạy thử streamlit run app/Home.py thật (chỉ py_compile + test logic nền, chưa "
                 "click-through UI).",
                 "streamlit run app/Home.pyの実機動作確認はまだ行っていない（py_compileとロジックテストのみ"
                 "、UIのクリック確認は未実施）。",
                 _OWNER_ENGINEER_VI, _OWNER_ENGINEER_JA),
    OpenQuestion("V131-D1", "D", STATUS_UNVERIFIED, "Open — tài liệu nguồn chưa tồn tại",
                 "Công thức急変率 chính thức (toàn bộ nhập viện vs chỉ ngoài kế hoạch) dùng để ước tính số "
                 "mẫu — tài liệu thứ 5 \"急変率の計算\" chưa tồn tại trong document/A/v1.3.1/.",
                 "サンプルサイズ推定に使う急変率の正式な計算式（入院全体 vs 予定外のみ）— 正式文書「急変率の"
                 "計算」（5番目の公式文書）はdocument/A/v1.3.1/にまだ存在しない。",
                 _OWNER_PROJECT_DOCTOR_VI, _OWNER_PROJECT_DOCTOR_JA),
    OpenQuestion("V131-D2", "D", STATUS_RESOLVED,
                 "✅ Quyết định tạm thời (có thể đổi lại) — 実施方針の概要 §6.2-2, 検索ツールの設計基準と辞書 R11",
                 "Quyết định tạm thời (2026-11-11): KHÔNG đưa 保留 (gồm \"疑い\") vào báo cáo/tổng hợp chính "
                 "— chỉ báo riêng held_back_count. Đã khớp code hiện tại (outcome_rates.py); có thể đổi lại "
                 "nhanh (1 chỗ) nếu quyết định sau này thay đổi, miễn giữ cờ is_suspected tách biệt.",
                 "暫定決定（2026-11-11）：保留（「疑い」を含む）は主報告・主集計に含めない — "
                 "held_back_countとして別掲のみ。現行コード（outcome_rates.py）と一致しており、今後方針を変"
                 "える場合も変更箇所は1か所のみ（is_suspectedフラグを分離した上で）で対応可能。",
                 _OWNER_PROJECT_DOCTOR_VI, _OWNER_PROJECT_DOCTOR_JA),
    OpenQuestion("V131-D3", "D", STATUS_UNVERIFIED, "Open",
                 "Danh sách B03 (lý do 対象外/保留) chính thức — đã có đề xuất (xem tab D3/D4), cần phê duyệt "
                 "là danh sách cuối, gồm cả việc có thêm \"予防投与\" làm lý do riêng hay không.",
                 "B03（対象外／保留の理由）正式リスト — 提案はあるが、最終リストとしての承認が必要。「予防投"
                 "与」を独立した理由として追加するかも未確定。",
                 "Nhóm nghiên cứu", "研究チーム"),
    OpenQuestion("V131-D4", "D", STATUS_UNVERIFIED, "Open",
                 "Định dạng evidence_ref/day0_evidence/outcome_evidence_ref (A17/B05/B22), version病名辞書 "
                 "dùng cho A16, và CSV có BOM hay không — chưa chốt.",
                 "evidence_ref／day0_evidence／outcome_evidence_ref（A17／B05／B22）の形式、A16用の病名辞書"
                 "バージョン、CSVにBOMを付けるか — 未確定。",
                 "Engineer + Nhóm nghiên cứu", "エンジニア＋研究チーム"),
    OpenQuestion("V131-D5", "D", STATUS_UNVERIFIED, "Open",
                 "Quyền sử dụng dữ liệu cá nhân + đường phê duyệt (có cần xét duyệt y đức/IRB hay không) — "
                 "chưa chốt.",
                 "個人データの利用権限と承認フロー（倫理審査／IRBが必要か）— 未確定。",
                 "PI / người phụ trách y đức", "PI／倫理審査担当"),
    OpenQuestion("V131-D6", "D", STATUS_UNVERIFIED, "Open (2/9 tự kiểm tra được qua code/DB)",
                 "9 \"未確認事項\" kỹ thuật trong 検索ツールの設計基準と辞書 §10 — 2/9 đã tự kiểm tra được qua "
                 "đối chiếu DB thật (medication_code = mã receipt, medical_class 31/32/33 khớp 皮下筋肉注射/"
                 "静脈注射/点滴注射), 7 mục còn lại cần bác sĩ/engineer xác nhận.",
                 "検索ツールの設計基準と辞書§10の技術的な「未確認事項」9件のうち、2件は実データベースで確認"
                 "済み（medication_codeはレセプトコード、medical_class 31/32/33が皮下筋肉注射／静脈注射／点"
                 "滴注射と一致）。残り7件は医師・エンジニアによる確認が必要。",
                 _OWNER_PROJECT_DOCTOR_VI, _OWNER_PROJECT_DOCTOR_JA),
    OpenQuestion("V131-D9", "D", STATUS_UNVERIFIED, "Open",
                 "Công cụ HTML cũ document/B/orca-search-standalone.html — tài liệu nói đã nghỉ hưu/lỗi "
                 "thời, cần Engineer xác nhận không còn phụ thuộc nào trong pipeline hiện tại.",
                 "旧HTMLツールdocument/B/orca-search-standalone.html — 文書上は退役・廃止扱いだが、現行パイ"
                 "プラインに依存が残っていないことをエンジニアが確認する必要がある。",
                 _OWNER_ENGINEER_VI, _OWNER_ENGINEER_JA),
    OpenQuestion("V131-D10", "D", STATUS_UNVERIFIED, "⏳ PENDING, chủ động để ngỏ (2026-11-11)",
                 "⏳ Chủ dự án đã xem, chủ động để ngỏ, chưa quyết — không phải bị quên: mỗi cơ sở xác nhận "
                 "đường lấy thông tin nhập viện/tử vong khi bệnh nhân nhập viện/qua đời ở một bệnh viện khác "
                 "(施設外) — ORCA của cơ sở theo dõi không tự động biết; quyết định trực tiếp tỉ lệ \"確認不"
                 "能\" ở B19/転帰.",
                 "⏳ チーム責任者は把握済みで意図的に未決定のまま — 見落としではない：患者が別の医療機関"
                 "（施設外）で入院・死亡した場合の情報入手経路を各施設で確認する必要がある — 追跡中の施設の"
                 "ORCAは自動では分からない。B19／転帰の「確認不能」率を直接左右する。",
                 "Nhóm nghiên cứu + từng cơ sở", "研究チーム＋各施設"),
    OpenQuestion("V131-D11", "D", STATUS_UNVERIFIED, "Open — đã hạ mức độ khẩn (xem addendum 15 §2.9)",
                 "medical_points.medical_day có ngày cấp độ ngày cho 皮下筋肉注射/静脈注射/点滴注射 (31/32/"
                 "33) nhưng CHỈ cho clinic nguồn HOMIS (0 dòng cho 11 clinic NAHT). Code hiện tại chỉ dùng "
                 "làm \"supplementary hint\", không tự động hoá 14-day rule/Day0. Cần báo lại nhóm viết tài "
                 "liệu v1.3.1 để xác nhận có nên tận dụng làm gợi ý hiển thị cho reviewer ở clinic HOMIS hay "
                 "không.",
                 "medical_points.medical_dayには皮下筋肉注射／静脈注射／点滴注射（31/32/33）の日単位の日付"
                 "があるが、HOMIS系施設のみ（NAHT11施設は0行）。現行コードは「補助的ヒント」としてのみ使用"
                 "し、14日ルール／Day0の自動化には使っていない。v1.3.1文書作成チームに報告し、HOMIS施設でレ"
                 "ビュー担当者向けの表示ヒントとして活用すべきか確認が必要。",
                 "Chủ dự án / engineer phía tài liệu", "チーム責任者／文書担当エンジニア"),
]
