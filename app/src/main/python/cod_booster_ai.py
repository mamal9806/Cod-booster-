"""
COD AI ENGINE - deterministic, explainable Android gaming optimization planner.
Python standard-library only. It never changes device settings itself.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
import math
import time

ENGINE_VERSION = "1.0.0"

@dataclass
class Finding:
    key: str
    severity: str
    title: str
    detail: str
    confidence: float

@dataclass
class Recommendation:
    id: str
    category: str
    title: str
    reason: str
    steps: List[str]
    impact: str
    risk: str
    requires_user_action: bool = True
    android_auto_apply: bool = False
    confidence: float = 0.0

@dataclass
class Analysis:
    engine_version: str
    device_class: str
    performance_score: int
    network_score: Optional[int]
    thermal_score: Optional[int]
    findings: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    tests: List[Dict[str, Any]]
    limitations: List[str]

def _num(data: Dict[str, Any], key: str, default=None):
    value = data.get(key, default)
    try:
        if value is None: return None
        value = float(value)
        return value if math.isfinite(value) else None
    except (TypeError, ValueError):
        return None

def _clamp(v, lo=0, hi=100):
    return max(lo, min(hi, int(round(v))))

def _test(name, status, detail, value=None):
    result = {"name": name, "status": status, "detail": detail}
    if value is not None: result["value"] = value
    return result

def analyze_device(metrics: Dict[str, Any], game_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    metrics keys (all optional):
      ram_total_mb, ram_available_mb, battery_temp_c, thermal_status,
      cpu_cores, cpu_load_percent, gpu_name, android_sdk, battery_level,
      network_type, ping_ms, jitter_ms, packet_loss_percent,
      game_fps_avg, game_fps_min, game_frame_time_ms, storage_free_gb,
      is_charging, refresh_rate_hz
    game_profile keys:
      target_fps, graphics_preference ("fps"|"balanced"|"quality")
    """
    m = dict(metrics or {})
    p = dict(game_profile or {})
    findings: List[Finding] = []
    recs: List[Recommendation] = []
    tests: List[Dict[str, Any]] = []

    ram_total = _num(m, "ram_total_mb")
    ram_free = _num(m, "ram_available_mb")
    ram_pct = (ram_free / ram_total * 100) if ram_total and ram_free is not None and ram_total > 0 else None

    if ram_pct is not None:
        status = "pass" if ram_pct >= 25 else "warn" if ram_pct >= 12 else "fail"
        tests.append(_test("memory_headroom", status, "Available memory compared with total RAM.", round(ram_pct, 1)))
        if ram_pct < 18:
            findings.append(Finding("low_ram_headroom", "high" if ram_pct < 10 else "medium",
                "حافظه آزاد کم است", f"حدود {ram_pct:.1f}% رم آزاد گزارش شده؛ احتمال بارگذاری مجدد برنامه‌ها و مکث وجود دارد.", 0.88))
            recs.append(Recommendation("memory_cleanup", "memory", "کاهش بار برنامه‌های پس‌زمینه",
                "حافظه آزاد گزارش‌شده پایین است؛ بستن دستی برنامه‌های غیرضروری می‌تواند فضای بیشتری فراهم کند.",
                ["دانلودها و برنامه‌های سنگین پس‌زمینه را متوقف کن.", "برنامه‌های غیرضروری را از صفحه برنامه‌های اخیر ببند.", "بازی را دوباره اجرا کن."],
                "ممکن است مکث ناشی از فشار حافظه کمتر شود.", "low", True, False, 0.84))

    temp = _num(m, "battery_temp_c")
    thermal = str(m.get("thermal_status", "")).lower()
    thermal_score = None
    if temp is not None:
        thermal_score = _clamp(100 - max(0, temp - 30) * 5)
        status = "pass" if temp < 38 else "warn" if temp < 43 else "fail"
        tests.append(_test("battery_temperature", status, "Battery temperature proxy; not CPU/GPU junction temperature.", round(temp, 1)))
        if temp >= 40:
            findings.append(Finding("high_battery_temp", "high" if temp >= 44 else "medium",
                "دمای باتری بالاست", f"دمای باتری {temp:.1f}°C است. دمای باتری نماینده دقیق دمای CPU/GPU نیست.", 0.9))
            recs.append(Recommendation("thermal_relief", "thermal", "کاهش فشار حرارتی",
                "گرما می‌تواند باعث محدودشدن خودکار توان و افت فریم شود.",
                ["اگر گوشی داغ است بازی را موقتاً متوقف کن.", "هنگام بازی قاب ضخیم را جدا کن و گوشی را از نور مستقیم دور نگه دار.", "برای خنک‌شدن از یخچال یا سرمای ناگهانی استفاده نکن."],
                "کاهش احتمال افت عملکرد ناشی از گرما.", "low", True, False, 0.9))
    if thermal in ("severe", "critical", "emergency"):
        findings.append(Finding("android_thermal_throttle", "high", "اندروید وضعیت حرارتی شدید گزارش کرده",
            f"thermal_status={thermal}", 0.97))
        recs.append(Recommendation("thermal_pause", "thermal", "توقف بازی تا خنک‌شدن دستگاه",
            "سیستم‌عامل وضعیت حرارتی شدید گزارش کرده است.",
            ["بازی را ببند و اجازه بده دستگاه خنک شود.", "پس از عادی‌شدن وضعیت حرارتی دوباره بازی کن."],
            "کاهش خطر افت عملکرد و داغ‌شدن بیش از حد.", "low", True, False, 0.97))

    ping = _num(m, "ping_ms")
    jitter = _num(m, "jitter_ms")
    loss = _num(m, "packet_loss_percent")
    network_score = None
    if ping is not None or jitter is not None or loss is not None:
        score = 100.0
        if ping is not None: score -= max(0, ping - 35) * 0.65
        if jitter is not None: score -= max(0, jitter - 8) * 1.8
        if loss is not None: score -= loss * 5.0
        network_score = _clamp(score)
        tests.append(_test("network_quality", "pass" if network_score >= 80 else "warn" if network_score >= 55 else "fail",
            "Heuristic network quality estimate; use in-game server ping for authoritative gameplay latency.", network_score))
        if (ping is not None and ping > 90) or (jitter is not None and jitter > 25) or (loss is not None and loss > 2):
            findings.append(Finding("unstable_network", "high" if (loss or 0) > 5 else "medium",
                "اتصال شبکه ناپایدار یا کند است",
                f"ping={ping}, jitter={jitter}, packet_loss={loss}. این مقادیر فقط در صورت اندازه‌گیری معتبر قابل اتکا هستند.", 0.78))
            recs.append(Recommendation("network_stability", "network", "بهبود پایداری اینترنت",
                "پینگ بالا، نوسان یا از دست‌رفتن بسته می‌تواند باعث تأخیر و تلپورت شود.",
                ["در نقطه‌ای با آنتن‌دهی قوی‌تر بازی کن.", "دانلود، آپلود و هات‌اسپات‌های غیرضروری را متوقف کن.", "اگر VPN روشن است، یک بار بدون آن و با رعایت شرایط شبکه آزمایش کن.", "با چند مسابقه، پینگ داخل بازی را مقایسه کن."],
                "ممکن است نوسان اتصال کمتر شود؛ کاهش پینگ تضمین‌شده نیست.", "low", True, False, 0.78))

    fps = _num(m, "game_fps_avg")
    min_fps = _num(m, "game_fps_min")
    frame_ms = _num(m, "game_frame_time_ms")
    target_fps = _num(p, "target_fps", 60) or 60
    preference = str(p.get("graphics_preference", "fps")).lower()
    if fps is not None:
        status = "pass" if fps >= target_fps * .92 else "warn" if fps >= target_fps * .70 else "fail"
        tests.append(_test("game_fps", status, "Requires a trusted in-game or external FPS measurement.", round(fps, 1)))
        if fps < target_fps * .9 or (min_fps is not None and min_fps < target_fps * .65):
            findings.append(Finding("fps_below_target", "high" if fps < target_fps * .65 else "medium",
                "نرخ فریم پایین‌تر از هدف است", f"میانگین FPS={fps}; حداقل FPS={min_fps}; هدف={target_fps}.", 0.86))
            steps = ["Graphics Quality را یک پله پایین‌تر بیاور.", "Frame Rate را روی بالاترین گزینه‌ای بگذار که در چند مسابقه پایدار می‌ماند.", "سایه‌ها و افکت‌های سنگین را در صورت وجود کاهش بده.", "پس از هر تغییر، در یک نقشه و شرایط مشابه دوباره FPS را اندازه بگیر."]
            recs.append(Recommendation("fps_profile", "graphics", "پروفایل اولویت FPS",
                "اندازه‌گیری FPS نشان می‌دهد بازی به هدف تعیین‌شده نمی‌رسد.",
                steps, "کاهش بار گرافیکی ممکن است پایداری فریم را بهتر کند.", "low", True, False, 0.86))
    if frame_ms is not None:
        tests.append(_test("frame_pacing", "pass" if frame_ms <= 20 else "warn" if frame_ms <= 33.4 else "fail",
            "Frame time consistency indicator, if measured by a trusted source.", round(frame_ms, 1)))

    charging = m.get("is_charging")
    if charging is True and temp is not None and temp >= 38:
        recs.append(Recommendation("avoid_charging_hot", "thermal", "از بازی هنگام شارژ در زمان داغی پرهیز کن",
            "دستگاه هم‌زمان در حال شارژ و نسبتاً گرم است.",
            ["شارژر را جدا کن، اگر برایت ایمن و ممکن است.", "اجازه بده گوشی خنک شود."],
            "ممکن است تولید گرمای اضافی کمتر شود.", "low", True, False, 0.87))

    # Score reflects available evidence; missing metrics are not silently treated as good.
    components = []
    if ram_pct is not None: components.append(min(100, ram_pct * 2.5))
    if thermal_score is not None: components.append(thermal_score)
    if fps is not None: components.append(min(100, fps / max(target_fps, 1) * 100))
    performance_score = _clamp(sum(components) / len(components)) if components else 0

    ram = ram_total or 0
    device_class = "unknown"
    if ram >= 7000: device_class = "high"
    elif ram >= 4000: device_class = "mid"
    elif ram > 0: device_class = "entry"

    if not tests:
        tests.append(_test("diagnostic_coverage", "limited", "اطلاعات کافی برای امتیازدهی وجود ندارد؛ داده‌های دستگاه بیشتری لازم است."))

    limitations = [
        "این موتور یک تحلیل‌گر قاعده‌محور و قابل‌توضیح است، نه یک مدل زبانی یا مدل یادگیری عمیق آموزش‌دیده.",
        "اپ اندرویدی بدون روت نمی‌تواند آزادانه پردازش برنامه‌های دیگر را ببندد یا فرکانس CPU/GPU را تحمیل کند.",
        "اعمال تنظیمات داخل COD Mobile فقط با اقدام کاربر در خود بازی انجام می‌شود؛ فایل‌های بازی دستکاری نمی‌شوند.",
        "پینگ سرویس آزمایشی اینترنت معادل پینگ سرور مسابقه COD نیست.",
        "دمای باتری با دمای مستقیم CPU/GPU تفاوت دارد.",
        "برای یادگیری واقعی، باید اندازه‌گیری‌های معتبر قبل و بعد از هر تغییر ذخیره شوند."
    ]
    result = Analysis(
        ENGINE_VERSION, device_class, performance_score, network_score, thermal_score,
        [asdict(x) for x in findings],
        [asdict(x) for x in recs],
        tests, limitations
    )
    return asdict(result)

def self_test() -> Dict[str, Any]:
    """Fast built-in smoke tests; safe to run on-device."""
    cases = [
        ("low_ram", {"ram_total_mb": 6000, "ram_available_mb": 400}, {"target_fps": 60}),
        ("hot_device", {"battery_temp_c": 45, "thermal_status": "severe"}, {}),
        ("bad_network", {"ping_ms": 150, "jitter_ms": 40, "packet_loss_percent": 7}, {}),
        ("low_fps", {"game_fps_avg": 30, "game_fps_min": 15}, {"target_fps": 60}),
        ("empty_input", {}, {}),
    ]
    checks = []
    for name, metrics, profile in cases:
        try:
            out = analyze_device(metrics, profile)
            assert "recommendations" in out and "tests" in out
            assert 0 <= out["performance_score"] <= 100
            checks.append({"name": name, "passed": True})
        except Exception as exc:
            checks.append({"name": name, "passed": False, "error": str(exc)})
    return {"engine_version": ENGINE_VERSION, "passed": sum(x["passed"] for x in checks),
            "total": len(checks), "ok": all(x["passed"] for x in checks), "checks": checks}

if __name__ == "__main__":
    print(self_test())
