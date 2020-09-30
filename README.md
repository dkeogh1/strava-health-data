# Strava Health Analysis

## EDA

See [strava_eda.ipynb]() for a dive into my running and cycling pace data. At the end of the notebook there is a clustering analysis based on elevation, pace, and distance data for running.

## ML

See [strava_pace_predictions.ipynb]() contains predictions for pace based on elevation and distance data from strava, and sleep score and resting heart beat data from strava. We evaluated RandomForrestRegressors, a multi-output meta estimator on a RandomForrestRegressor, and we use a RandomizedSearchCV iterator and were able to generate accuarcy of ~94% on n=175.