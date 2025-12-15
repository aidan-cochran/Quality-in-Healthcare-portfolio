# Quality-in-Healthcare-Portfolio

## Introduction
The purpose of this project is to apply techniques learned in ISE 371 - Quality and Process Improvement in Healthcare. To accomplish this, I have broken this project up into 2 sub-projects, with the purpose to best incorporate 5 relevent topics covered in class. Each project is meant to technically apply these topics and act as deliverables, but a formal report does exist explaining related theory. Additionally, my focus throughout the semester has specifically related to Vaccine Manufacturing and how to think about the topics touched on in class in this context. Therefore, both projects align closely with Vaccine Manufacturing, although the simulated data used in Project 2 is general manufacturing data. 

Each project is contained within a .ipynb file, with the exception of the Measuring and Reporting of Quality Data, which takes advantage of the Streamlit python library which is incombatable with that file type. 

#### Project 1 - Capacity Planning (Demand Forecasting)
- Capacity Planning and Scheduling
- AI and it's Impact on Healthcare

In this project, I used a dataset that tracked [influenza in the city of Chicago](https://catalog.data.gov/dataset/influenza-surveillance-weekly), and applied various forecasting methods to predict influenza infections. Accurate forecasting is essental for not only vaccine manufacturers, but hospitals, pharmacies, schools, and insurers. Forecasting methods demonstrated within the Capacity Planning and Scheduling section are Seaonal Naive Forecasting and Seasonal Autoregressive Integrated Moving Average. I then applied XGBoost Regression as a forecasting method, which typically produces highly accurate predictions due to its ability to handle high dimentional data. 

#### Project 2 - Statistical Process Control
- Statistical Process Control
- Measuring and Reporting of Quality Data
- Change Management

This project is used demonstrate relevent SPC charts, display them on an updating, real-time web based dashboard, and record these changes to evaluate potential company impact caused by continuous improvement initiatives. The data used in this project is simulated over a time period of six months representing data commonly collected on any manufacturing line, including a vaccine manufacturer. Quality, Downtime, Throughput and Cycle Time are among the features simulated. Demonstrated SPC charts include a P-Chart for Total Defects, an I-MR chart for Cycle Time, I-MR chart for Downtime, OEE and OEE parameters (Quality, Performance, Availability). I then used these charts to create a web-based dashboard, which allows for easy visibility on relevent Key Performance Indicators. Additionally, the charts and metrics update continuously on the simulation of new data. Finally, these data points are saved for future analysis and to support Change Management. 
