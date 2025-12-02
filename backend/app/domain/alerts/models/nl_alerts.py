# alerts/nl_alerts.py

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional, Literal

from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool


from typing import Literal, TypedDict

Intent = Literal["create_alert", "list_alerts", "modify_alert", "info_question", "other"]

class IntentResult(TypedDict):
    intent: Intent



class AlertType(str, Enum):
    PRICE_THRESHOLD = "price_threshold"
    METRIC_THRESHOLD = "metric_threshold"  # can include iv, iv_rank, etc.
    EVENT = "event"
    PERCENT_CHANGE = "percent_change"
    OPTION_PREMIUM_CHANGE = "option_premium_change"   # NEW
    IV_PERCENT_CHANGE = "iv_percent_change"            # OPTIONAL NEW



class AlertStatus(str, Enum):
    ACTIVE = "active"
    TRIGGERED = "triggered"
    CANCELED = "canceled"


class Alert(BaseModel):
    """
    Internal representation of an alert.
    This is what you’ll eventually store in Mongo.
    """
    id: Optional[str] = None   # Mongo _id (stringified)
    user_id: str

    type: AlertType
    ticker: str

    # For threshold alerts
    metric: Optional[str] = None      # "price", "pe", etc.
    operator: Optional[
        Literal["<", "<=", ">", ">=", "=="]
    ] = None
    threshold: Optional[float] = None

    # For event-based alerts (earnings, etc.)
    event_type: Optional[str] = None  # "earnings"
    event_offset_days: Optional[int] = None  # e.g. 1 = 1 day before

    # Meta
    status: AlertStatus = AlertStatus.ACTIVE
    fire_once: bool = True

    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_checked_at: Optional[datetime] = None
    last_fired_at: Optional[datetime] = None

    # Notification config (can tweak later)
    channel: Literal["email", "web", "sms", "push"] = "email"
    channel_target: Optional[str] = None   # email addr, phone, etc.

    type: AlertType
    ticker: str

    # option-specific fields
    underlying: Optional[str] = None
    option_type: Optional[Literal["call", "put"]] = None
    strike: Optional[float] = None
    expiration: Optional[date] = None

    # premium / iv stuff
    percent_change: Optional[float] = None
    baseline_price: Optional[float] = None
    iv_baseline: Optional[float] = None
    change_direction: Optional[Literal["up", "down", "either"]] = None


# -----------------------
# Tool argument schemas
# -----------------------

class PriceAlertArgs(BaseModel):
    """Arguments for creating a price threshold alert."""
    ticker: str
    operator: Literal["<", "<=", ">", ">=", "=="]
    target: float


class MetricAlertArgs(BaseModel):
    """Arguments for creating a metric-based alert (e.g. P/E)."""
    ticker: str
    metric: str  # e.g. "pe", "p/e ratio", "price to earnings"
    operator: Literal["<", "<=", ">", ">=", "=="]
    target: float


class EventAlertArgs(BaseModel):
    """Arguments for creating an event-based alert (e.g. earnings)."""
    ticker: str
    event_type: Literal["earnings"]  # you can expand this later
    offset_days: int  # e.g. 1 = 1 day before

class PercentChangeAlertArgs(BaseModel):
    ticker: str
    percent: float
    direction: Literal["up", "down", "either"]
    period: Literal["intraday", "from_creation", "1d", "1w"]  # you can start with fewer

# -----------------------
# LangChain tools
# -----------------------

@tool(args_schema=PriceAlertArgs)
def create_price_alert(ticker: str, operator: str, target: float) -> str:
    """
    Create a price threshold alert for a given stock ticker.

    Use when user says things like:
    - "Notify me when AAPL goes above 250"
    - "Alert me if TSLA drops below 170"
    """
    # NOTE: The LLM just uses this to structure arguments.
    # The function body itself isn't executed by the LLM;
    # we handle tool calls manually in Python.
    return "price_alert_args_collected"


@tool(args_schema=MetricAlertArgs)
def create_metric_alert(ticker: str, metric: str, operator: str, target: float) -> str:
    """
    Create a metric-based alert for a given stock ticker.

    Use when user says things like:
    - "Notify me when NVDA's P/E is below 30"
    - "Alert me if MSFT PE ratio goes above 40"
    """
    return "metric_alert_args_collected"


@tool(args_schema=EventAlertArgs)
def create_event_alert(ticker: str, event_type: str, offset_days: int) -> str:
    """
    Create an event-based alert (e.g. earnings).

    Use when user says things like:
    - "Notify me the day before AAPL earnings"
    - "Remind me on the morning of AMD earnings"
    """
    return "event_alert_args_collected"


@tool(args_schema=PercentChangeAlertArgs)
def create_percent_change_alert(ticker: str, percent: float, direction: str, period: str):
    """
    Create an alert based on percent price movement.

    Use for things like:
    - "Alert me if AAPL drops 5% today"
    - "Notify me when TSLA goes up 10% from here"
    - "Tell me if NVDA rises 3% this week"
    """
    return "percent_change_args_collected"



# -----------------------
# PUBLIC ENTRYPOINT
# -----------------------

# -----------------------
# STUBS / HELPERS TO FILL IN LATER
# -----------------------

def normalize_metric_name(metric_raw: str) -> str:
    """
    Map user/LLM metric names to a canonical internal name.

    Examples:
        "P/E", "pe", "PE ratio", "price to earnings" -> "pe"
        "rsi" -> "rsi"
        "price" -> "price"
    """
    # TODO: implement more robust normalization
    m = metric_raw.strip().lower()
    if m in {"pe", "p/e", "p/e ratio", "price to earnings", "pe ratio"}:
        return "pe"
    if m in {"price", "stock price"}:
        return "price"
    # fallback: just return lowered string
    return m


async def save_alert(alert: Alert) -> str:
    """
    TODO: Implement MongoDB save here.

    Should:
        - insert the alert into the 'alerts' collection
        - return the string ID
    """
    # Example (pseudo-code):
    # doc = alert.model_dump(exclude={"id"})
    # result = await mongo_db.alerts.insert_one(doc)
    # return str(result.inserted_id)
    raise NotImplementedError("save_alert() not implemented yet.")


async def list_alerts_for_user(user_id: str) -> list[Alert]:
    """
    TODO: Implement a query to list alerts for a user.
    """
    raise NotImplementedError("list_alerts_for_user() not implemented yet.")


async def delete_alert(alert_id: str, user_id: str) -> None:
    """
    TODO: Implement deletion / soft-delete for alerts.
    """
    raise NotImplementedError("delete_alert() not implemented yet.")
