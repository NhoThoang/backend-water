from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DashboardStat(BaseModel):
    title: str
    value: str
    change: str
    trend: str # "up" or "down"
    icon_type: str # To help frontend pick icon
    color: str

class RecentActivity(BaseModel):
    id: int
    description: str
    time_ago: str
    type: str

class BillOverview(BaseModel):
    total_unpaid: float
    unpaid_count: int
    total_collected: float

class DashboardAnomaly(BaseModel):
    id: int
    customer_name: str
    month: str
    consumption: float
    time_ago: str

class ConsumptionStat(BaseModel):
    month: str
    consumption: float

class DashboardSummary(BaseModel):
    stats: List[DashboardStat]
    recent_activities: List[RecentActivity]
    bill_overview: BillOverview
    anomalies: List[DashboardAnomaly]
    consumption_history: List[ConsumptionStat]

class RevenueStat(BaseModel):
    month: str
    total_billed: float
    total_collected: float
