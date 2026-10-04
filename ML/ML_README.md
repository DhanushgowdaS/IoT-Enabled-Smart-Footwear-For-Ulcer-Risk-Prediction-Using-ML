# ML Workflow

## Purpose

Estimate diabetic foot-ulcer risk indication by measuring deviation from learned healthy footwear sensor patterns.

## Training Data

- Person A: healthy reference
- Person B: healthy reference
- RAW records used for training
- AVG10 records excluded because they are derived averages

## Model

**Isolation Forest** is trained as an unsupervised anomaly detector on the combined healthy reference data.

### Input Features

- FSR1
- FSR2
- FSR3
- FSR4
- Temperature
- FSR average
- FSR max/min
- FSR standard deviation
- Four FSR distribution ratios

## Output

The model produces:

1. Anomaly score
2. Healthy-pattern mismatch percentage
3. Ulcer-risk indication

### Mismatch Calculation

```text
Mismatch = clip((AnomalyScore - q95) / (q99 - q95) × 100, 0, 100)
```

The mismatch percentage is a healthy-pattern deviation index. It is **not** a probability of ulcer.

## Risk Bands

| Mismatch | Indication |
|---:|---|
| 0% | Safe |
| 0–33.33% | Low Risk |
| 33.33–66.67% | Medium Risk |
| 66.67–100% | High Risk |

These bands are project-specific and must not be described as clinically validated thresholds.

## Next Step

Validate the model first, then integrate the same feature calculation and mismatch formula into FastAPI and the rolling 5-minute dashboard assessment.
