#run karnay kay liye terminal mei (fastapi dev main.py)

from fastapi import FastAPI, HTTPException
import json
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional

app = FastAPI()

class Patients(BaseModel):
    id: Annotated[str, Field(..., description="Id of the patuent", examples=["P001"])]
    name: Annotated[str, Field(..., description="name of the patient")]
    city:Annotated[str, Field(..., description="city where the patient is living")]
    age:Annotated[int, Field(..., gt=0, lt=120,description="age of the patient")]
    gender:Annotated[Literal["male", "female", "other"], Field(...,description="gender of the patient")]
    height:Annotated[float, Field(..., gt=0,description="height of the patient in meter")]
    weight:Annotated[float, Field(..., gt=0,description="weight of the patient in kg")]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi=round(self.weight/(self.height)**2,2)
        return bmi

    @computed_field
    @property
    def verdict(self)-> str:
        if self.bmi < 18.5:
            return "underweight"
        elif self.bmi <30:
            return "normal"
        else:
            return "obseed"
        
class PatientUpdate(BaseModel):
    id: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None)]
    gender: Annotated[Optional[Literal['male', 'female']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]


def LoadData():
    with open('patients.json', 'r') as f:
        data = json.load(f)
    return data

def save(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f)


@app.get("/")
def read_root():
    return {"message": "Wah! Aapki pehli FastAPI successfully chal rahi hai!"}



@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "query": q}


@app.post('/create')
def createPatient(patient: Patients):
    data = LoadData() 
    if patient.id in data:
        raise HTTPException(status_code=400, detail="patient exist karta hai")

    data[patient.id]= patient.model_dump(exclude=['id'])

    save(data)
    return JSONResponse(status_code=201, content={'message':'patient created successfully'})



@app.put('/edit/{patient_id}')
def Update(patient_id: str, patientUpdate: PatientUpdate):
    data = LoadData()

    if patient_id not in data:
        raise HTTPException(status_code=400, detail="not found haiiii")

    existingPatient = data[patient_id]

    updateInfo = patientUpdate.model_dump(exclude_unset=True)

    for key, value in updateInfo.items():
        existingPatient[key] = value

    existingPatient['id'] = patient_id
    patient_pydantic_object= Patients(**existingPatient)
    patient_pydantic_object = patient_pydantic_object.model_dump(exclude='id')

    data[patient_id] = existingPatient

    save(data)

    return JSONResponse(status_code=201, content={'message':"patient update successfully"})

@app.delete('/delete/{patient_id}')
def delete(patient_id: str):
    data = LoadData()

    if patient_id not in data:
            raise HTTPException(status_code=400, detail="not found haiiii")


    del data[patient_id]

    save(data)

    return JSONResponse(status_code=201, content={'message':"patient delete successfully"})
    
