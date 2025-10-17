# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "fastapi[standard]",
#   "uvicorn",
# ]
# /// end script



from fastapi import FastAPI

def validate_secret(secret: str) -> bool:
    # Dummy validation logic
    return secret == "ljao(23$*dfs#1023-49($HC9203*&(23"


app = FastAPI()

# POST endpoint to handle `JSON request round 1` that takes in 
# email, secret, task, round, nonce, brief, checks(array), evaluation_url,
# attatchments(array with object with fields, name and url)
@app.post("/initiate_task")
def initTask(data: dict):
    #validate data
    if not validate_secret(data.get("secret", "")):
        return {"error": "Invalid secret"}
    else:
        #Process the task initiation
        # depending on the round call the respective function
        if data.get("round") == 1:
            round1()
        elif data.get("round") == 2:
            round2()
        else:
            return {"error": "Invalid round"}
        
    return {"message": "Task initiated successfully", "data": data}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(main, host='0.0.0.0', port=8000)
    
