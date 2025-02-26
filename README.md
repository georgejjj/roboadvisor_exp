# Robo-Advisor Experimental Platform (智能投顾实验平台)

This is a Robo-Advisor experimental platform built with Streamlit that allows users to experience the entire process of robo-advising, from risk assessment to asset allocation and return simulation.

## Features

1. **Risk Assessment Questionnaire**: Evaluates the user's risk tolerance and investment preferences
2. **Asset Risk-Return Display**: Visualizes the risk and return characteristics of different asset classes
3. **User Initial Allocation**: Users can allocate assets based on their understanding
4. **Robo-Advisor Recommendation**: Provides personalized asset allocation suggestions based on the user's risk assessment
5. **Plan Modification**: Users can modify the recommended allocation plan
6. **Return Simulation Comparison**: Uses Monte Carlo simulation to compare potential returns of different allocation plans

## Installation and Running Locally

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation Steps

1. Clone or download this repository

2. Install required dependencies
   ```
   pip install -r requirements.txt
   ```

3. Run the app
   ```
   streamlit run app.py
   ```

4. Open in your browser (typically opens automatically)
   ```
   Local URL: http://localhost:8501
   ```

## Deployment on Streamlit Share

This application is optimized for deployment on Streamlit Share. All charts and text elements have been configured to use English for better compatibility with cloud deployment environments.

To deploy this application on Streamlit Share:
1. Fork this repository to your GitHub account
2. Go to [Streamlit Share](https://share.streamlit.io/) and sign in
3. Create a new app and connect it to your forked repository
4. Set the main file path to `app.py`
5. Deploy!

## Usage Flow

1. Start screen → Click "Start Experiment"
2. Fill out personal information and risk tolerance questionnaire → Submit
3. View asset information, input initial allocation plan → Submit
4. View and compare robo-advisor recommendation → Click "Modify Allocation Plan"
5. Adjust your allocation based on recommendations → Click "Confirm and Proceed to Return Simulation"
6. View simulated returns comparison of different allocation plans

## Data Note

Asset data and recommended allocations in this application are simulated for educational and demonstration purposes only. For actual investing, please consult professional financial advisors.

## Important Notice

This application is intended solely as an educational tool and experimental platform. It does not constitute investment advice. Investment involves risks, decisions should be made cautiously. 