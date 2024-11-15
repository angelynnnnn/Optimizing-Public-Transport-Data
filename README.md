# Optimizing-Public-Transport-Data

# 1. Repository Structure
Below is an overview of the repository structure and what each folder/file contains

```├── env/
├── _pycache_/
├── .env.example               # Example environment variable file for configuration
├── .gitignore                 # Specifies files to ignore in version control
├── Dockerfile                 # Docker setup for project containerization
├── README.md                  # Project overview and setup instructions
├── requirements.txt           # List of dependencies for the project
│
├── data/
│   ├── bus_stop_coords.csv        # Coordinates of bus stops used in analysis
│   ├── clean_data.csv             # Processed and cleaned survey data
│   ├── cleaned_routes.csv         # Routes data after cleaning
│   ├── future_predicted_data.csv  # Future data predictions for usage patterns
│   ├── grouped_data.csv           # Grouped data by certain categories
│   ├── synthetic_data.csv         # Generated synthetic data to supplement the small dataset
│   └── form_responses.csv         # Raw survey responses from users
│
├── notebooks/
│   ├── Multivariate.ipynb         # Notebook for multivariate demand forecasting
│   ├── NLP_Analysis_Results.csv   # Results from NLP analysis
│   ├── data_cleaning.ipynb        # Notebook detailing the data cleaning steps
│   ├── data_generation.ipynb      # Synthetic data generation process
│   ├── multivariate2.ipynb        # Secondary multivariate analysis notebook
│   ├── optimization.ipynb         # Optimization analysis for bus operations
│   ├── route_visualization.ipynb  # Visualizes optimized routes for the shuttle service
│   ├── testsyntheise.ipynb        # Testing synthetic data generation
│   ├── travel_patterns.ipynb      # Analysis of user travel patterns on campus
│   └── user_segmentation.ipynb    # Segmentation analysis for different user groups
│
├── scripts/
│   ├── clean_functions.py         # Functions used for cleaning raw data
│   ├── config.py                  # Configuration settings for the project
│   ├── custom_constraints.py      # Custom constraints used in model optimization
│   ├── main.py                    # Main script that runs the data pipeline
│   ├── simulation.py              # Simulations for predicting shuttle demand
│   ├── utils.py                   # Utility functions for data processing
│   └── test.py                    # Placeholder or testing script for code functions
│
├── models/
│   ├── grp_A_User_Satisfaction_Model.ipynb  # Model for analyzing user satisfaction
│   └── future_predicted_data.csv            # Model-generated predictions for future data
│
└── visualizations/
    └── route_visualization.ipynb            # Notebook for route and clustering visualizations

```
# 2. Real Data Collection

We designed a survey aimed at gathering insights on the satisfaction and user experience with the NUS campus shuttle service. The survey included multiple-choice questions (MCQ), multi-response questions (MRQ), and open-ended questions, allowing participants to share detailed feedback. The survey was conducted via an online Google Forms questionnaire, distributed primarily through university email lists and student groups.

More Information about Data Collection can be found [here](https://github.com/angelynnnnn/Optimizing-Public-Transport-Data/wiki/Data-Understanding)

# 3. Synthetic Data Generation

To overcome the limitations of the small and skewed dataset, we generated synthetic data to expand our sample size and create a more representative dataset. Using the Gaussian Copula-based synthesizer, we modeled the distribution of the original responses, generating approximately 60,000 synthetic records that align with the patterns in the real data.

More Information about Synthetic Data Generation can be found [here](https://github.com/angelynnnnn/Optimizing-Public-Transport-Data/wiki/Data-Understanding)

# 4. Data Dictionary 

### Dataset : clean_data.csv

| Column Name                     | Data Type | Description                                                     |
|---------------------------------|-----------|-----------------------------------------------------------------|
| `role`                          | object    | The role of the respondent (e.g., Undergraduate student, Staff).|
| `frequency_of_travel`           | object    | How often the respondent uses the shuttle service.              |
| `primary_purpose`               | object    | The primary purpose of using the shuttle.                       |
| `travel_days`                   | object    | Days of the week the respondent travels on the shuttle.         |
| `travel_hours`                  | object    | The hours of the day during which the respondent travels.       |
| `ISB_Service_trip_1`            | object    | Name of the shuttle service used for the first recorded trip.   |
| `bus_stop_board_trip_1`         | object    | Boarding bus stop for the first trip.                           |
| `bus_stop_alight_trip_1`        | object    | Alighting bus stop for the first trip.                          |
| `day_of_the_week_trip_1`        | object    | Day of the week for the first trip.                             |
| `time_start_trip_1`             | time      | Start time of the first trip.                                   |
| `travel_duration_trip_1`        | object    | Estimated travel duration for the first trip.                   |
| `frequency_trip_1`               | object    | User satisfaction rating with the frequency of service on the first recorded trip.                             |
| `punctuality_trip_1`             | object    | User satisfaction rating with the punctuality of service on the first recorded trip.                           |
| `cleanliness_trip_1`             | object    | User satisfaction rating with the cleanliness on the first recorded trip.                                      |
| `safety_trip_1`                  | object    | User satisfaction rating with safety on the first recorded trip.                                               |
| `coverage_trip_1`                | object    | User satisfaction rating with route coverage on the first recorded trip.                                       |
| `crowdedness_trip_1`             | object    | User satisfaction rating with crowdedness on the first recorded trip.                                          |
| `ISB_Service_trip_2`             | object    | Code of the shuttle service used for the second recorded trip.                                                 |
| `bus_stop_board_trip_2`          | object    | Boarding bus stop for the second recorded trip.                                                                |
| `bus_stop_alight_trip_2`         | object    | Alighting bus stop for the second recorded trip.                                                               |
| `day_of_the_week_trip_2`         | object    | Day of the week for the second recorded trip.                                                                  |
| `time_start_trip_2`              | time      | Start time of the second recorded trip.                                                                        |
| `travel_duration_trip_2`         | object    | Estimated duration of the second recorded trip.                                                                |
| `frequency_trip_2`               | object    | User satisfaction rating with the frequency of service on the second recorded trip.                            |
| `punctuality_trip_2`             | object    | User satisfaction rating with the punctuality of service on the second recorded trip.                          |
| `cleanliness_trip_2`             | object    | User satisfaction rating with the cleanliness on the second recorded trip.                                     |
| `safety_trip_2`                  | object    | User satisfaction rating with safety on the second recorded trip.                                              |
| `coverage_trip_2`                | object    | User satisfaction rating with route coverage on the second recorded trip.                                      |
| `crowdedness_trip_2`             | object    | User satisfaction rating with crowdedness on the second recorded trip.                                         |
| `usage_influence_convenience`    | object    | Influence of convenience on usage of the shuttle service.                                                      |
| `usage_influence_cost`           | object    | Influence of cost on usage of the shuttle service.                                                             |
| `usage_influence_lack_of_options`| object    | Influence of lack of transport options on shuttle service usage.                                               |
| `usage_influence_availability_of_parking` | object | Influence of parking availability on shuttle service usage.                                                    |
| `usage_influence_environmental`  | object    | Influence of environmental concerns on shuttle service usage.                                                  |
| `prioritize_frequency`           | object    | Rank of importance given to shuttle service frequency.                                                         |
| `prioritize_punctuality`         | object    | Rank of importance given to shuttle service punctuality.                                                       |
| `prioritize_cleanliness`         | object    | Rank of importance given to shuttle cleanliness.                                                               |
| `prioritize_safety`              | object    | Rank of importance given to shuttle safety.                                                                    |
| `prioritize_bus_route_coverage`  | object    | Rank of importance given to bus route coverage.                                                                |
| `prioritize_crowdedness`         | object    | Rank of importance given to crowdedness on the shuttle.                                                        |
| `top_3_frustrations`             | object    | The respondent's top three frustrations with the shuttle service.                                              |
| `not_able_to_get_on`             | object    | Frequency of not being able to board due to crowdedness.                                                       |
| `additional_features_frequency`  | object    | Preferred improvements in frequency of shuttle service.                                                        |
| `additional_features_seats`      | object    | Preferred improvements in seating availability.                                                                |
| `additional_features_cleanliness`| object    | Preferred improvements in cleanliness.                                                                         |
| `additional_features_comfortable`| object    | Preferred improvements in comfort.                                                                             |
| `additional_features_route_coverage` | object | Preferred improvements in route coverage.                                                                      |
| `additional_features_updates`    | object    | Preferred improvements in service updates.                                                                     |
| `issues_with_quality_of_info`    | object    | Issues identified with the quality of information provided.                                                    |
| `special_events`                 | object    | Whether there are special events impacting shuttle use.                                                        |
| `seasonal_changes`               | object    | Whether seasonal changes impact shuttle service usage.                                                         |
| `seasonal_changes_specific`      | object    | Specific details about how seasonal changes impact shuttle service usage.                                      |
| `further_comments`               | object    | Any additional feedback provided by the respondent.       |

### Dataset : bus_stops_coords.csv


| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| Bus Stop    | object    | Name of the bus stop location. |
| Latitude    | float     | Latitude coordinate of the bus stop. |
| Longitude   | float     | Longitude coordinate of the bus stop. |

### Dataset : cleaned_routes.csv

| Column Name        | Data Type | Description                                                                                      |
|--------------------|-----------|--------------------------------------------------------------------------------------------------|
| `ISB_Service`      | object    | Name of the shuttle service used for the trip.                                                   |
| `bus_stop_board `  | object    | Boarding bus stop for the trip.                                                                  |
| `bus_stop_alight ` | object    | Alighting bus stop for the trip.                                                                 |
| `day_of_the_week`  | object    | Day of the week when the trip occurred.                                                          |
| `time_start`       | time      | Start time of the trip.                                                                          |
| `travel_duration`  | object    | Estimated travel duration for the trip.                                                          |
| `frequency`        | object    | Satisfaction rating for frequency of the shuttle service.                                        |
| `punctuality`      | object    | Satisfaction rating for punctuality of the shuttle service.                                      |
| `cleanliness`      | object    | Satisfaction rating for cleanliness of the shuttle service.                                      |
| `safety`           | object    | Satisfaction rating for safety of the shuttle service.                                           |
| `coverage`         | object    | Satisfaction rating for route coverage of the shuttle service.                                   |
| `crowdedness`      | int       | Satisfaction rating for crowdedness on the trip.                                                 |

### Dataset : NLP_Analysis_Results.csv

| Column Name       | Data Type | Description                                                                                                      |
|-------------------|-----------|------------------------------------------------------------------------------------------------------------------|
| `Original Text`     | object    | The original feedback text provided by the respondent.                                                           |
| `Processed Text`    | object    | The processed version of the text, with keywords extracted for analysis.                                         |
| `Topic`             | int       | The topic assigned to the text based on topic modeling.                                                          |
| `Cluster`           | int       | The cluster assigned to the text based on clustering analysis.                                                   |

### Dataset : future_predicted_data.csv

| Column Name        | Data Type | Description                                                        |
|--------------------|-----------|--------------------------------------------------------------------|
| `ISB_Service`      | object    | Name of the shuttle service used for the trip.                     |
| `bus_stop_board`   | object    | Boarding bus stop for the trip.                                    |
| `day_of_the_week`  | object    | Day of the week when the trip occurred.                            | 
| `is_weekend`       | int       | Binary variable for weekend                                        |
| `is_peak`          | int       | Binary variable for peak timing                                    |
| `hour`             | int       | Integer for hour                                                   |
| `minute`           | int       | Integer for minute                                                 |
| `time_start`       | object    | Start time of the trip.                                            |
| `predicted_count`  | float     | Predicted count of passengers arriving at bus stop by minute       |


# Setting up the environment and running the code 

### Requirements :
- Python 3.8 +
- Docker
- Dependencies listed in 'requirements.txt'

## Group Tasks

### [Subgroup A Analysis](https://github.com/angelynnnnn/Optimizing-Public-Transport-Data/wiki/Analytical-Findings-Group-A) 
Qn 1 : Run [QN1A](grp_A_User_Satisfaction_Model.ipynb) and [Q1A Evaluation](https://github.com/angelynnnnn/Optimizing-Public-Transport-Data/wiki/Modeling-&-Evaluation-Q1A) 

Qn 2 : Run [QN2A](user_segmentation.ipynb) and [Q2A Evaluation](https://github.com/angelynnnnn/Optimizing-Public-Transport-Data/wiki/Modeling-&-Evaluation-Q2A) 

Qm 3 : Run [QN3A](travel_patterns.ipynb) and [Q3A Evaluation](https://github.com/angelynnnnn/Optimizing-Public-Transport-Data/wiki/Modeling-&-Evaluation-Q3A) 

Optional Q 1: Run [QN1AO](Optional-Subtask%201%20(Group%20A).ipynb) and [Q1A Evaluation](https://github.com/angelynnnnn/Optimizing-Public-Transport-Data/wiki/Modeling-&-Evaluation-Q1-Optional) 



### [Subgroup B Analysis](https://github.com/angelynnnnn/Optimizing-Public-Transport-Data/wiki/Analytical-Findings-Group-B) 

Qn 1 : Run [QN1B](demand_forecasting.ipynb) and [Q1B Evaluation](https://github.com/angelynnnnn/Optimizing-Public-Transport-Data/wiki/Modeling-&-Evaluation-Q1B) 

Qn 2 : Run [QN3B](simulation.py) and [Q2B Evaluation](https://github.com/angelynnnnn/Optimizing-Public-Transport-Data/wiki/Modeling-&-Evaluation-Q2B) 

Qn 3 : Run [QN3B](simulation.py) and [Q3B Evaluation](https://github.com/angelynnnnn/Optimizing-Public-Transport-Data/wiki/Modeling-&-Evaluation-Q3B) 

# Running Streamlit
To run the Streamlit app, you will need your own Mapbox API key.

1. **Get an API Key**
* Go to [Mapbox](https://www.mapbox.com) and create an account (if you don't have one).
* Generate an API key from your account settings.
2. **Set up the Environment**
* Copy the provided `.env.example` file to `.env`:

  ```bash
  cp .env.example .env
  ```
* Replace `your_api_key_here` in the `.env` file with your actual API key:

  ```plaintext
  MAPBOX_API = your_actual_api_key
  ```
3. **Install Dependencies** and **Run the Application**
  ```bash
  pip install -r requirements.txt
  python main.py 
  ```
