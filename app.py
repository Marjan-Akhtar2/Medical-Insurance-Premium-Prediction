from fastapi import FastAPI, HTTPException
import json
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import pandas as pd
import pickle

with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

app = FastAPI()
tier_1_cities = ["Mumbai", "Delhi", "Bangalore"]

class UserInput(BaseModel):
    age: Annotated[int, Field(..., gt=0, lt=120, description="Age of the user")]
    weight: Annotated[float, Field(..., gt=0, description="weight of the user")]
    height: Annotated[float, Field(..., gt=0, lt=2.5, description="height of the user")]
    income_lpa: Annotated[float, Field(..., gt=0, description="annual salary of the user")]
    smoker: Annotated[bool, Field(...,description="Is user a smoker")]
    city: Annotated[str, Field(...,description="city of the user")]
    occupation: Annotated[Literal['unemployed', 'retired', 'business_owner', 'private_job',
       'student', 'government_job'], Field(..., description="occupation of the user")]


    @computed_field
    @property
    def bmi(self)-> float:
        return self.weight/(self.height**2)

    @computed_field
    @property
    def lifestyle_risk(self)->str:
        if self.smoker and self.bmi > 30:
            return "high"
        elif self.smoker or self.bmi > 27:
            return "medium"
    
        else:
            return "low"

    @computed_field
    @property
    def age_group(self)-> str:
        if self.age < 20:
            return "young"
        elif self.age < 45:
            return "audult"
        elif self.age < 60:
            return "MiddleAge"
        return "old"

    @computed_field
    @property
    def city_tier(self)->int:
        if self.city in tier_1_cities:
            return 1
        else:
            return 2

@app.post('/predict')
def predict_premium(data: UserInput):
    input_df = pd.DataFrame([{
        'bmi':data.bmi,
        'age_group': data.age_group,
        'lifestyle_risk':data.lifestyle_risk,
        'city_tier': data.city_tier,
        'income_lpa': data.income_lpa,
        'occupation': data.occupation
    }])

    prediction = model.predict(input_df)[0]

    return JSONResponse(status_code=200, content={'prediction is ': prediction})