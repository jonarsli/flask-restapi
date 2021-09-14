## Introduction
You can use response decorator to generate response schema to spec document. If you need multiple response specification documents, you can use multiple response decorators to achieve.

!!! Note
    Flask-RESTAPI default return to json. If it detects that the return type is dictionary or Pydantic BaseModel, it will be automatically converted to json

## Step
1. Create spec and inherit BaseModel
2. Use response decorator
3. Initialize response instance