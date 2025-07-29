from pydantic import BaseModel, Field
from typing import List, Optional

class NutritionInfo(BaseModel):
    foods: List[str] = Field(..., description="List of foods identified in the meal")
    total_calories: Optional[int] = Field(None, description="Estimated total calories")
    recommendations: Optional[List[str]] = Field(None, description="Nutritional recommendations")

class WorkoutPlan(BaseModel):
    exercises: List[str] = Field(..., description="List of recommended exercises")
    duration: str = Field(..., description="Recommended workout duration")
    intensity: str = Field(..., description="Recommended intensity level")

class BMIResult(BaseModel):
    bmi: Optional[float] = Field(None, description="Calculated BMI value")
    category: Optional[str] = Field(None, description="BMI category")
    advice: Optional[str] = Field(None, description="Health advice based on BMI")

class SleepRecommendation(BaseModel):
    bedtime: Optional[str] = Field(None, description="Recommended bedtime")
    tips: Optional[List[str]] = Field(None, description="Sleep hygiene tips")

