# Copyright © 2025 Neothan
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class HealthData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    date: datetime = Field(default_factory=datetime.utcnow)
    steps: int = Field(default=0)
    heart_rate: int = Field(default=0)
    sleep_hours: float = Field(default=0.0)
    calories: int = Field(default=0)
    distance: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class HealthStats(SQLModel):
    total_steps: int
    avg_heart_rate: float
    avg_sleep_hours: float
    activity_level: str
    health_score: int
    weekly_goal_progress: int 