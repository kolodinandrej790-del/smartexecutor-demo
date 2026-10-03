# contracts.py — Контракты данных для всех модулей SmartExecutor
# Роль: единый язык модулей. Только структуры, без логики.
# Версия 1.0.
#
# Каждый модуль принимает и возвращает данные по этим контрактам.
# Диспетчер валидирует структуру ответа (K-004).

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


# ========== 1. InfoSense ==========
@dataclass
class Event:
    """Событие из внешнего мира (новость, анонс, макро)."""
    ts: int
    source: str                          # "okx_announcements", "coindesk", "cmc"
    source_type: str                     # "primary" | "secondary"
    type: str                            # listing / delisting / regulation / hack / macro / whale / geopolitics / statement / manipulation
    asset: Optional[str]                 # "ETH" | None (для всего рынка)
    impact: int                          # -3..+3
    confidence: str                      # "HIGH" | "MEDIUM" | "LOW"
    headline: str
    url: str = ""
    market_reaction: Optional[Dict[str, Any]] = None   # {price_change_5m, volume_spike, ...}
    raw: Dict[str, Any] = field(default_factory=dict)


# ========== 2. LevelBuilder ==========
@dataclass
class PreparedData:
    """Структурные данные для стратегий."""
    asset: str
    price: float
    level: float
    wick_above_level: float
    wick_below_level: float
    volume_current: float
    volume_average: float
    volume_above_level: float
    atr: float
    timestamp: int
    session: str = ""                    # asia / europe / us


# ========== 3. TraderSense ==========
@dataclass
class Sense:
    """Интерпретация рынка."""
    volatility_level: str                # neutral / trending / volatile / storm
    false_breakout: bool
    volume_weak: bool
    stop_hunt_likely: bool
    message: str = ""


# ========== 4. TrendAnalyzer ==========
@dataclass
class Trend:
    """Тренд и рыночная фаза."""
    direction: str                       # up / down / flat
    strength: float                      # 0..1
    phase: str                           # accumulation / impulse / correction
    session: str                         # asia / europe / us


# ========== 5. Signal ==========
@dataclass
class Signal:
    """Сигнал от стратегии."""
    asset: str
    direction: str                       # BUY / SELL
    entry: float
    stop_loss: float
    take_profit: float
    reason_code: str
    reason_text: str
    strategy: str = "unknown"
    profile: str = ""                    # какой профиль (K-020)


# ========== 6. ContextGate ==========
@dataclass
class GateVerdict:
    """Решение ContextGate."""
    verdict: str                         # PASS / BLOCK
    reason: str
    confidence: str                      # HIGH / MEDIUM / LOW
    recommended_profile: Optional[str] = None  # K-023


# ========== 7. Methodist / Архивариус ==========
@dataclass
class ConfidenceRecord:
    """Запись о confidence от Methodist."""
    ts: int
    asset: str
    confidence: str                      # HIGH / MEDIUM / LOW
    modules_compared: List[str] = field(default_factory=list)
    agreements: List[str] = field(default_factory=list)
    disagreements: List[str] = field(default_factory=list)
    summary: str = ""
    linked_trade_id: Optional[int] = None


# ========== 8. Ядро → Диспетчер ==========
@dataclass
class Intent:
    """Намерение ядра — что делать."""
    name: str                            # evaluate_market / check_signal / execute_trade / ...
    params: Dict[str, Any] = field(default_factory=dict)


# ========== 9. Explanation (K-026) ==========
@dataclass
class Explanation:
    """Объяснение решения агента."""
    trade_id: Optional[int]
    ts: int
    asset: str
    action: str                          # BUY / SELL / BLOCKED / ARBITRAGE
    profile: str
    reason_code: str
    reason_text: str
    explanation: str
    confidence: str
    confidence_reason: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    modules_involved: List[str] = field(default_factory=list)
    decision_chain: List[str] = field(default_factory=list)


# ========== 10. Профиль (K-020) ==========
@dataclass
class ProfileConfig:
    """Конфиг профиля торговли."""
    name: str                            # spot_long / futures_short / ...
    description: str
    modules: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    limits: Dict[str, Any] = field(default_factory=dict)