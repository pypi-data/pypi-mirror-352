import time
import uuid
import numpy as np
from datetime import datetime
from dateutil import parser
import requests
import json
import base64
import os
import re

subscriptionUrl = "https://app.llumo.ai/api/workspace/record-extra-usage"
getStreamdataUrl = "https://app.llumo.ai/api/data-stream/all"
createPlayUrl = "https://app.llumo.ai/api/New-Eval-API/create-new-eval-playground"
deletePlayUrl = "https://app.llumo.ai/api/New-Eval-API/new-upload-flow/delete-columnlist-in-playground"
uploadColList = (
    "https://app.llumo.ai/api/New-Eval-API/new-upload-flow/uploadColumnListInPlayground"
)
uploadRowList = (
    "https://app.llumo.ai/api/New-Eval-API/new-upload-flow/uploadRowsInDBPlayground"
)
createInsightUrl = "https://app.llumo.ai/api/New-Eval-API/insights-api/generate-playground-insights"
getPlaygroundInsightsUrl="https://app.llumo.ai/api/New-Eval-API/insights-api/get-all-playground-insights"


def getProcessID():
    return f"{int(time.time() * 1000)}{uuid.uuid4()}"


def getInputPopulatedPrompt(promptTemplate, tempObj):
    for key, value in tempObj.items():
        promptTemplate = promptTemplate.replace(f"{{{{{key}}}}}", value)
    return promptTemplate


def costColumnMapping(costResults, allProcess):
    # this dict will store cost column data for each row
    cost_cols = {}

    compressed_prompt = []
    compressed_prompt_output = []
    cost = []
    cost_saving = []

    for record in allProcess:
        cost_cols[record] = []
        for item in costResults:
            if list(item.keys())[0].split("-")[0] == record.split("-")[0]:
                cost_cols[record].append(list(item.values())[0])

    for ky, val in cost_cols.items():
        try:
            compressed_prompt.append(val[0])
        except IndexError:
            compressed_prompt.append("error occured")

        try:
            compressed_prompt_output.append(val[1])
        except IndexError:
            compressed_prompt_output.append("error occured")

        try:
            cost.append(val[2])
        except IndexError:
            cost.append("error occured")

        try:
            cost_saving.append(val[3])
        except IndexError:
            cost_saving.append("error occured")

    return compressed_prompt, compressed_prompt_output, cost, cost_saving


def checkUserHits(
    workspaceID,
    hasSubscribed,
    trialEndDate,
    subscriptionEndDate,
    remainingHits,
    datasetLength,
):
    # Get the current date (only the date part)
    current_date = datetime.now().date()

    # Parse trialEndDate if provided
    if trialEndDate is not None:
        try:
            trialEndDate = parser.parse(trialEndDate).date()
        except Exception:
            return {"success": False, "message": "Invalid trialEndDate format"}

    # Parse subscriptionEndDate if provided
    if subscriptionEndDate is not None:
        try:
            subscriptionEndDate = parser.parse(subscriptionEndDate).date()
        except Exception:
            return {"success": False, "message": "Invalid subscriptionEndDate format"}

    # If user is on a free trial
    if not hasSubscribed and trialEndDate is not None:
        if current_date > trialEndDate:
            return {"success": False, "message": "Trial expired. Access denied"}

        if remainingHits < datasetLength or remainingHits <= 0:
            return {"success": False, "message": "Trial Hits Exhausted"}

    else:
        if subscriptionEndDate and current_date > subscriptionEndDate:
            return {"success": False, "message": "Subscription expired. Access denied."}


        
        if remainingHits <= 0 or remainingHits < datasetLength:
            if workspaceID:
                workspaceID=str(workspaceID)
                headers = {
                    "Authorization": f"Bearer {base64.b64encode(workspaceID.encode()).decode()}",
                    "Content-Type": "application/json",
                }
                reqBody = {"unitsToSet": 1}
                responseBody = requests.post(
                    url=subscriptionUrl, json=reqBody, headers=headers
                )
                response = json.loads(responseBody.text)

                proceed = response.get("execution", "")
                print(proceed)

                if proceed:
                    return {"success": True, "message": "Hits added and access granted."}
            else:
                return {"success": False, "message": "Workspace ID is required for subscription."}
    return {"success": True, "message": "Access granted."}


def getStreamId(workspaceID: str, token, dataStreamName):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    reqBody = {"workspaceID": workspaceID}
    response = requests.post(url=getStreamdataUrl, json=reqBody, headers=headers)

    if response.status_code == 200:
        responseJson = response.json()
        data = responseJson.get("data", [])

        # Find stream by name
        matchedStream = next(
            (stream for stream in data if stream.get("name") == dataStreamName), None
        )

        if matchedStream:

            return matchedStream.get("dataStreamID")

        else:
            print(f"No stream found with name: {dataStreamName}")
            return None
    else:
        print("Error:", response.status_code, response.text)
        return None


def createEvalPlayground(email: str, workspaceID: str):
    url = createPlayUrl
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "email": email,
        "workspaceID": workspaceID,
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        try:
            responseJson = response.json()
            # print(responseJson)
            return responseJson.get("data", {}).get("playgroundID", None)

        except Exception as e:
            print("Failed to parse JSON:", e)
            return None
    else:
        print("Error:", response.status_code, response.text)
        return None


def deleteColumnListInPlayground(workspaceID: str, playgroundID: str):
    url = deletePlayUrl
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "workspaceID": workspaceID,
        "playgroundID": playgroundID,
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        try:

            return response.json()
        except Exception as e:
            print("⚠️ Failed to parse JSON:", e)
            return None
    else:
        print("❌ Error:", response.status_code, response.text)
        return None


def createColumn(workspaceID, dataframe, playgroundID, promptText=None,queryColName=None,outputColName= "output",dataStreamName=None,definationMapping=None):
    if len(dataframe) > 100:
        dataframe = dataframe.head(100)
        print("⚠️ Dataframe truncated to 100 rows for upload.")

    coltemplate = {
        "workspaceID": workspaceID,
        "playgroundID": playgroundID,
        "columnListToUpload": [],
    }
    allEvals = ['Response Completeness', 'Response Bias', 'Response Harmfulness', 'Input Toxicity', 'Input Harmfulness', 'Context Utilization', 'Relevance Retention', 'Semantic Cohesion', 'Final Task Alignment', 'Tool Reliability', 'Response Correctness', 'Response Toxicity', 'Input Bias', 'Input Relevancy', 'Redundancy Reduction', 'Response Sentiment', 'Tool Selection Accuracy', 'Stepwise Progression', 'Hallucination', 'Faithfulness', 'Answer Relevancy', 'Context Precision', 'Answer Similarity', 'Harmfulness', 'Maliciousness', 'Coherence', 'Answer Correctness', 'Context Recall', 'Context Entity Recall', 'Conciseness', 'customEvalColumn', 'Groundedness', 'Memory Utilization', 'Input Relevancy (Multi-turn)']



    # Create a mapping of column names to unique column IDs
    columnIDMapping = {}

    # Iterate over each column in the dataframe
    for indx, col in enumerate(dataframe.columns):
        # Generate a unique column ID using uuid
        columnID = str(uuid.uuid4().hex[:8]) 

        columnIDMapping[col] = columnID

        
        if col.startswith('output'):
            # For output columns, create the prompt template with promptText
            if promptText:
                # Extract variables from promptText and set them as dependencies
                dependencies = []

                # Find variables inside {{variable}}
                variables = re.findall(r'{{(.*?)}}', promptText)

                # Loop through each variable and check if it exists as a column name
                for var in variables:
                    varName = var.strip() 
                    if varName in columnIDMapping:  # Check if the variable is a column name
                        dependencies.append(columnIDMapping[varName])  # Add its columnID

                # Now update the template for the output column
                
                template={
                    "provider": "OPENAI",
                    "model": "GPT_4o",
                    "promptText": promptText,
                    "modelOptions": {
                        "temperature": 0,
                        "frequencyPenalty": 0,
                        "presencePenalty": 0,
                        "maxToken": 8192
                    },
                    "toolConfig": "none",
                    "concurrency": "",
                    "outputType": "STRING",
                    "isPromptSelected": True,
                    "isSmartPromptSelected": False,
                    "dependency": dependencies,  # Use the dependencies extracted from promptText
                    "columnID": columnID,  # Use the generated column ID
                    "label": col,
                    "type": "PROMPT",
                    "order": indx,
                }
                
        elif col.startswith('Data '):
            if queryColName and dataStreamName:
                dependencies = []
                dependencies.append(columnIDMapping[queryColName])
                template = {
                    "variableType": "STRING",
                    "dependency": dependencies,
                    "dataStreamName": dataStreamName,
                    "query": columnIDMapping[queryColName],
                    "columnID": columnID,  # Use the generated column ID
                    "label": "Data stream",
                    "type": "DATA_STREAM",
                    "order": indx}

        elif col in allEvals:

            dependencies = []
            variables = re.findall(r'{{(.*?)}}', promptText)

                # Loop through each variable and check if it exists as a column name
            for var in variables:
                varName = var.strip() 
                if varName in columnIDMapping:  # Check if the variable is a column name
                    dependencies.append(columnIDMapping[varName])
                    
            dependencies.append(columnIDMapping[outputColName])  # Add the output column ID
            longDef = definationMapping.get(col, {}).get(col, "")
            shortDef ="You have run this from SDK"
            enum =  col.upper().replace(" ","_")

            template = {
      "analytics": [
        col.lower().replace(" ","_")
      ],
      "evaluationMetric": "ALL",
      "evaluationModel": "GEMINI_PRO",
      "selectPrompt": columnIDMapping[outputColName],
      "scoreCondition": "GREATER_THAN",
      "scoreValue": "50",
      "scoreResult": "PASS",
      "llmKpi": col,
      "setRules": True,
      "type": "EVAL",
      "evalType": "LLM",
      "similarityMetric": None,
      "embeddingModel": None,
      "groundTruth": None,
      "dataStream": None,
      "context": None,
      "dependency": [columnIDMapping[outputColName]],
      "hallucinationFields": {
        "query": None,
        "context": None,
        "output": None
      },
      "definition": longDef,
      "analyticsENUM": enum,
      "prompt": shortDef,
      "analyticsName": col,
      "columnID": str(uuid.uuid4().hex[:8]),
      "label": col,
      "order": indx
    }

           

            
        else:
            
            template = {
                "label": col,  # Label is the column name
                "type": "VARIABLE",  # Default type for non-output columns
                "variableType": "STRING",
                "order": indx,
                "columnID": columnID,  # Use the generated column ID
            }

        # Append the template to the column list
        coltemplate["columnListToUpload"].append(template)

    # Prepare the row template structure
    rowTemplate = {
        "workspaceID": workspaceID,
        "playgroundID": playgroundID,
        "dataToUploadList": [],
        "columnList": coltemplate["columnListToUpload"],
    }

    # Populate dataToUploadList with rows from the dataframe
    for indx, row in dataframe.iterrows():
        row_dict = {}

        # For each column, we need to map the column ID to the corresponding value in the row
        for col in dataframe.columns:
            columnID = columnIDMapping[col]  # Get the columnID from the mapping
            row_dict[columnID] = row[col]  # Map the columnID to the value in the row

        # Add the row index (if necessary)
        row_dict["pIndex"] = indx
        rowTemplate["dataToUploadList"].append(row_dict)

    # Return the column template, row template, and the column ID mapping
    return coltemplate, rowTemplate

def uploadColumnListInPlayground(payload):
    url = uploadColList
    headers = {
        "Content-Type": "application/json",
    }
    payload = payload

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        try:

            return response.json()
        except Exception as e:
            print("⚠️ Failed to parse JSON:", e)
            return None
    else:
        print("❌ Error:", response.status_code, response.text)
        return None


def uploadRowsInDBPlayground(payload):
    url = uploadRowList
    headers = {
        "Content-Type": "application/json",
    }

    payload = payload

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        try:

            return response.json()
        except Exception as e:
            print("⚠️ Failed to parse JSON:", e)
            return None
    else:
        print("❌ Error:", response.status_code, response.text)
        return None


def createPlayground(email, workspaceID, df, promptText=None,queryColName=None,dataStreamName=None,definationMapping=None,outputColName="output"):
    
    playgroundId = str(createEvalPlayground(email=email, workspaceID=workspaceID))
    payload1, payload2 = createColumn(
        workspaceID=workspaceID, dataframe=df, playgroundID=playgroundId, promptText=promptText,queryColName=queryColName,dataStreamName=dataStreamName,definationMapping=definationMapping,outputColName=outputColName
    )
    deleteExistingRows = deleteColumnListInPlayground(
        workspaceID=workspaceID, playgroundID=playgroundId
    )
    colListUpload = uploadColumnListInPlayground(payload=payload1)
    rowListUpload = uploadRowsInDBPlayground(payload=payload2)

    if rowListUpload:
        return True



def getPlaygroundInsights(workspaceID: str, activePlayground: str):
    headers = {
        
        "Content-Type": "application/json",
    }

    # Initial request to generate playground insights
    payload = {
        "activePlayground": activePlayground,
        "workspaceID": workspaceID,
    }

    urlGenerate = createInsightUrl
    
    responseGenerate = requests.post(urlGenerate, json=payload, headers=headers)

    if responseGenerate.status_code == 200:
        responseJson = responseGenerate.json()
        
        insightStatus = responseJson.get("data", {}).get("insight", False)

        if insightStatus:
            # If insight is true, request to get all playground insights
            urlGetAll = getPlaygroundInsightsUrl
            
            responseGetAll = requests.post(urlGetAll, json=payload, headers=headers)

            if responseGetAll.status_code == 200:
                responseAllJson = responseGetAll.json()
                
                data = responseAllJson.get("data", {}).get("data", [])
                
                # Extract insight and solution
                insights = []
                for item in data:
                    insight = item.get("insight", "")
                    solution = item.get("solution", "")
                    insights.append({"insight": insight, "solution": solution})

                return insights
            else:
                print(f"Error fetching all insights: {responseGetAll.status_code} - {responseGetAll.text}")
                return None
        else:
            print("No insight generated.")
            return None
    else:
        print(f"Error generating insight: {responseGenerate.status_code} - {responseGenerate.text}")
        return None

