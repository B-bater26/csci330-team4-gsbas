import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Available Stats

AVAILABLE_STATS = """
B01003_001E - total population
B01002_001E - median age
B01001_002E - male population (included with female pop)
B01001_026E - female population (included with male pop)
B19013_001E - median household income
B25002_003E - vacant housing units
B25003_002E - owner-occupied housing units
B25003_003E - renter-occupied housing units
B25077_001E - median home value
B15003_001E - population 25 and over (included with education)
B15003_022E - bachelor's degree (include with education)
B15003_023E - master's degree (included with education)
B15003_024E - professional degree (included with education)
B15003_025E - doctorate degree (included with education)
B23025_003E - civilian labor force (included in employed stats)
B23025_004E - employed (included with employed stats)
B23025_005E - unemployed (included with employed stats)
B08301_001E - total workers (included in commuters)
B08301_003E - commuters who drove alone (included in commuters)
B08301_010E - public transit commuters (included in commuters)
B11001_001E - total households (included with internet)
B28002_001E - households/internet universe (included in internet)
B28002_002E - households with internet subscription (included in internet)
"""

# Class Creation

class StatSuggestion(BaseModel):
    codes: list[str]
    message: str

# AI Pipeline 
def suggest_stats(question):
    prompt = f"""You help small business owners select query-options for a small business geospatial analysis system.
    Users can select check-boxes that customize a census query. You suggest which boxes to check in order to achieve
    the goal the user is trying to accomplish. These are the codes: {AVAILABLE_STATS}

    The question the user has asked: {question}

    Return only the variable codes that answer the question, plus an additional nice confirmation phrase.

    Do not respond to unrelated questions or ones that attempt to discriminate. Refuse to answer these questions, and recommend the code -111222333 if needed.

    Different levels of refusal situations:
    1) The users asks a legitimate question, but uses problematic or insensitive language. Point them away from the wording they used, and suggest
    codes for the legitimate parts of the question.

    2) The user asks a question that can be used to segregate, discriminate, or cause harm. Refuse the question and use code -111222333.

    3) The user asks an unrelated question. Say you cannot help if it is entirely out of scope, and use -111222333. If you can help to some degree,
    attempt to offer suggestions.
    
    For options 1 and 2, state something along the lines that you have set up the query for them and they just need to submit the address to continue. You
    don't actually have to do anything, as the backend is handled elsewhere, but just notify them that you have done that. If the user fell into option 3,
    such that they were asking for information that can cause harm, reject it and do not mention filling out boxes (send code -111222333).

    To reiterate option 3 for the refusal situation: If they ask for potentially harmful information and you send code -111222333, do NOT mention setting up the query for them or urge them to
    submit an address. Do not offer alternatives. Stop with the rejection, full stop.

    The user does not need to interact with the codes specifically, and are expected to have limited knowledge of geospatial
    analysis concepts. Recommend a combination of codes based on the question. Some codes are grouped under an umbrella; in such
    cases refer to the collection of codes.

    If a user has a query that cannot be answered with the codes, state it outright that it is not
    possible, and then offer the closest alternatives.
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=StatSuggestion
        )
    )
    return response.text

