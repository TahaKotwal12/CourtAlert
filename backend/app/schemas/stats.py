from datetime import date
from typing import List
from pydantic import BaseModel


class OverviewStats(BaseModel):
    total_cases:      int
    active_cases:     int
    alerts_sent_30d:  int
    delivery_rate:    float   # 0.0 – 1.0
    upcoming_7d:      int     # hearings in next 7 days


class UpcomingHearing(BaseModel):
    case_id:      str
    case_title:   str
    cnr_number:   str
    hearing_date: date
    days_until:   int
    court_name:   str | None


class ChannelStats(BaseModel):
    sent:      int
    delivered: int
    failed:    int
    rate:      float


class DeliveryRateStats(BaseModel):
    whatsapp: ChannelStats
    sms:      ChannelStats
    telegram: ChannelStats
