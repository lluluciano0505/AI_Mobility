# AI_Mobility

An urban grid-based mobility flow forecasting project built on aggregated YJMob100K data. The project uses DuckDB + PyTorch to train a linear baseline and an LSTM sequence model for next-step (30-minute ahead) flow prediction, followed by spatial error visualization.

## Project Objective

- Task: Predict next-step flow for each grid cell using recent flow history and POI context features.
- Focus:
	- Whether temporal modeling clearly outperforms a non-temporal baseline.
	- Where prediction errors concentrate in space.

## Data and Features

- Source table: flow_poi in mobility.duckdb (aggregated from discretized YJMob100K trajectories and POI context).
- Spatiotemporal granularity:
	- Space: 500m x 500m grid cells.
	- Time: 30-minute slots.
- Input features:
	- Current flow: flow
	- All poi_* columns (about 85 dimensions)
	- Cyclical time encodings: tod_sin, tod_cos, dow_sin, dow_cos
- Prediction target: flow_next (next-slot flow for the same cell).

## Pipeline

1. Feature Table Construction
- Build flow_feat in DuckDB:
	- Fill missing POI values with 0.
	- Create global time_index.
	- Add cyclical time encodings.
	- Generate flow_next using a window LEAD per (x, y).

2. Temporal Train-Test Split
- Split by the 80th percentile of time_index:
	- Training: flow_feat_train
	- Testing: flow_feat_test
- Compute normalization statistics (mean/std) on training data only to avoid leakage.

3. Sequence Construction
- SEQ_LEN = 8: each sample uses the last 8 slots (4 hours).
- STRIDE = 4: sliding window shift of 2 hours.
- BATCH_SIZE = 1024.

4. Models
- Linear baseline (LinearSeqModel): flatten [L, F] into one vector and apply a single fully connected regression layer.
- LSTM model (FlowLSTM): 2-layer LSTM with hidden_dim = 64; prediction is made from the last hidden state through a linear head.

5. Training and Evaluation
- Optimizer: Adam (lr=1e-3)
- Loss: MSE
- Epochs: 8
- Evaluate test MSE after each epoch and save checkpoints.

## Key Results

- LSTM significantly outperforms the linear baseline (test error is lower by more than two orders of magnitude).
- Stable final LSTM performance is approximately:
	- Train MSE ≈ 3.79
	- Test MSE ≈ 4.15
- Spatial plots show:
	- The model reproduces the overall flow structure well.
	- Errors are concentrated in high-flow and high-volatility areas.

## Visualization

- Single time slice (Day 64, selected t):
	- True next-step flow
	- Predicted next-step flow
	- Absolute error
- Multi-slice panel (multiple t values on the same day):
	- Row 1: True, Row 2: Pred, Row 3: |Pred - True|
	- Shared color scales are used for consistent comparison across time.

## Repository Structure

- ai_mobility_flow_prediction.ipynb: main experiment notebook.
- model222_ipyn_files/: notebook export assets.
- image/: figures used by notebook/report.
- _site/: Quarto-rendered static site.
- _quarto.yml: Quarto configuration.
- scripts/clear_nb_outputs.py: script to clear notebook outputs.

## How to Run

1. Prepare Data
- Place mobility.duckdb in an accessible location in your runtime environment.
- The current notebook uses a Colab + Google Drive path by default.

2. Install Dependencies
- Python packages: duckdb, pandas, numpy, torch, matplotlib.

3. Run the Notebook
- Open ai_mobility_flow_prediction.ipynb and run cells in order:
	- Data preparation and feature construction
	- Temporal split and normalization
	- Sequence generation
	- Linear baseline training
	- LSTM training and evaluation
	- Spatial visualization

## Conclusion

This project verifies that temporal modeling is critical for urban flow forecasting. Even a relatively small LSTM (2 layers, hidden size 64) substantially outperforms a non-temporal linear baseline. Future improvements can target high-volatility regions with attention mechanisms or explicit spatial graph modeling.
