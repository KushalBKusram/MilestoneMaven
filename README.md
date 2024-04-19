# Milestone Maven

A dashboard to track your Todoist projects using Streamlit containers.

![Dashbaord](assets/screenshot.png)

## Setup
1. Generate `API_KEY` from Todoist Developer Section and paste it in `docker-compose.yaml`.
2. Pick a label that will be used to track tasks, for e.g. #tracked and enter the same label in `docker-compose.yaml`. Ensure there are only 6 tasks being tracked at any time, this is by design. 
3. `docker compose up` would start the service.
