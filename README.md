**Dota 2 match victory predictor**

![Model Accuracy](https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/bkhor/dota-predictor/main/metrics.json&query=$.accuracy&label=accuracy&suffix=%25&color=blue)

This is a project where I attempt to implement ML models from scratch, with the minimal use of any frameworks. I avoid using existing ML frameworks for now - scikit-learn, JAX, PyTorch, and TensorFlow to learn the mathematical foudnation of every step of model training.
Currently, the only dependency that this project has is NumPy.

To run:
1. Add Steam Web API key into .env in project folder
   
   `STEAM_API_KEY=1234567890ABCDEF`

Updates:

*August 24*: Migrated from storing data in JSON format, to sqlite3 for deduplication, easy to resume collection, query without loading into memory. Also, migrated from OpenDota API, directly to Steam Web API - no daily cap. I just looked at how [OpenDota API](https://github.com/odota/core) does it, and implemented it similarly. 

*August 21-23rd*: Fetching match data using OpenDota API and utilizing logistic regression to train the model, based on picks and match outcome. 

*Issues*: 
1. Training only based on picks and match outcomes, especially public matches, is unreliable and almost random.
2. Weights are being recalculated on every run
3. OpenDota API has daily limits, need to use Steam Web API directly instead.

*Next Steps*: 
1. Migrate to Steam Web API
2. Implement new feature - hero winrate.


