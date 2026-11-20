# Geospatial Small Business Analysis System
## GIS Made Easy for Small Businesses

## Authors
1. Bailey Baxter - Team Lead | Querying 
Functionality | AI Assistant
2. Caleb Moore - Next-in-Charge | Database | Visualization
3. Nate Miller - UI/UX and Development | Amenities Feature
4. Jack Hardman - Testing and Documentation | Area Comparison | /tests Work
5. Siddharth Linga - Professor

## Table of Contents
[Description](#description)
[Prerequisites & Installation](#prerequisites--installation)
[Folders](#folders)
[Tech Stack](#tech-stack)
[Limitations](#limitations)


## Description
GSBAS is a web dashboard that enables small business owners with limited access and knowledge of geospatial technologies to run analysis queries from their system.
Users can do the following using GSBAS:
- Query any United States address for Census stats
- Compare two areas side-by-side
- Customize, visualize, and save queried locations
- Find nearby amenities in an area
- Chat with an AI assistant to come up with the best query constraints for specific scenarios

GSBAS solves the issue of lacking the technical knowledge and resources for geospatial analysis by making the process digestible and free.

## Prerequisites & Installation
GSBAS requires Python 3.14 and all included files in the repo to run.

1. Clone the repo
2. Create a virtual environment with `python -m venv .venv`
3. Activate the environment on Windows using `.venv\Scripts\Activate.ps1` or for Linux/MacOS use `source .venv/bin/activate`
4. Install requirements using `pip install -r requirements.txt`
5. Set up keys using .env.example. You need a key from Google Gemini for Gemini 3.6 Flash, a Neon Database Key and Secret Key, and Census ACS key. All of these keys are free.
6. Use `python run.py` in the terminal and open `http://127.0.0.1:5000` in a web browser.
7. Create an Account and Log In

## Folders

### app
- Entire project structure
- Includes scripts, templates, code, env, and Flask
### /static
- /css - Web styles for dashboard
- /scripts - Frontend and endpoint calling functions
### /templates
- HTML pages that the user sees
- comparison, history, index, login, register
### __init__.py
- Flask Controller
- Connects code to endpoints
### py files
- Contain functions that run in each Flask endpoint in the backend
- amenities, census_acs, gemini, geocoder, query_data_census
### README.md
- Markdown file containing information about the project and set up
### /docs
- Contains documentation for the project
- PowerPoint
### /examples
- Contains sample .env file
- Needs to be placed in root
### /tests
- Contains testing documentation
### .gitignore
- Specifications for GitHub to ignore uploading some files/folders
### requirements.txt
- Collection of installations to make the project run
### run.py
- Runs the dashboard locally

## Test the Features

### Querying
- Enter a valid address into the text input, select a radius using the slider, and click the `Enter` key
- Wait for the map to display your location, area, census block zones, and statistics
- A successful run shows a change on the map and valid statistical outputs

### Nearby Amenities
- Query a location
- Wait a few moments at the bottom of the screen
- View a list of nearby amenities
- Scroll up to the map and zoom in
- Click on the blue dots to see the title and location of each amenity
- Successful runs display a list and collection of clickable points near the location pin

### Area Comparison
- Go to the Area Comparison page
- Enter two valid addresses
- Submit the addresses
- View the two different area radius circles on the map
- View the side-by-side comparison of the two locations
- A successful run shows two areas on the map and two stacks of stats

### Visualization
- Go to the visualization screen
- Customize the view, colors, symbology, and map style
- A successful run allows for various stylistic changes to the map and symbology

### AI Assistant
- Click the pencil icon on the home screen
- Type a question in the input box
- For example `Is this a good spot for a cafe?`
- Wait for a response
- The system outputs a response, selects query constraints for you, and suggests inserting an address to view the data
- A successful run correctly outputs the Gemini response and automatically selects query constraints for the user
- Note: Discriminatory responses are rejected and problematic responses are flagged

You can view more testing information in /tests or in PowerPoint in /docs

## Tech Stack
- Python
- Flask
- JavaScript
- Census ACS
- TIGERweb
- Census Geocoder
- Turf.js
- Leaflet.js
- Gemini
- PostgreSQL
- OpenStreetMap

## Limitations
### Limitations
- There are tight key limits due to the free plan being selected for each API. The AI assistant in particular may experience downtime due to hitting a key limit.
- Styling across screens may be inconsistent
- Area Comparison, AI functionality, and Customization are all on different pages
- Data is not cached, so there may be delays or overloaded calls

### Unfinished Features
- Error handling may not always reach the user visually
- There is no "Forgot Password" button for the Log In

### Troubleshooting 
- Retry the query or AI question if it doesn't work the first time
- Ensure you have a secret key and link to the neon database if the log in does not work
- Use dev tools to see internal errors