# Project Atlas

Project Atlas is a smart agriculture monitoring system designed to help farmers detect crop stress before visible damage occurs. The system collects soil moisture, temperature, humidity, and light-level data from sensors installed across different sections of a field.

## Data Processing

Sensor readings are transmitted to an ESP32 gateway, which forwards the data to the backend. The backend cleans the incoming readings and stores historical measurements. A machine learning model analyzes changes in soil moisture and temperature to identify patterns associated with crop stress.

## Irrigation

When the system detects a sustained decrease in soil moisture, it compares the reading against the crop's configured moisture threshold. If the value remains below the threshold for a specified period, the irrigation controller is activated.

The system does not immediately activate irrigation for a single low reading because temporary sensor fluctuations can produce false alerts.

## Weather Integration

Project Atlas can also use weather forecasts to improve irrigation decisions. If rainfall is expected soon, irrigation can be delayed even when soil moisture is below its normal threshold.

## Alerts

If the system detects a combination of unusually high temperature, low soil moisture, and abnormal sensor readings, it generates a crop-stress alert. Farmers can view these alerts through the monitoring dashboard.

## Goal

The primary goal of Project Atlas is to reduce unnecessary water consumption while maintaining healthy crop conditions through data-driven irrigation decisions.