# Multilingual Text Detection with Font-Aware OCR

A multilingual OCR pipeline for detecting text in visual media, identifying the text script, applying script-specific recognition models, and quantitatively evaluating OCR performance across different languages and fonts.

The project focuses on **English, Hindi, and Tamil** and uses a synthetic dataset generated with multiple fonts to study OCR robustness.

---

## Project Overview

Optical Character Recognition (OCR) performance can vary significantly depending on the:

- Language
- Writing script
- Font style
- Image characteristics
- Recognition model
- Text complexity

This project implements an experimental multilingual OCR pipeline that combines:

1. Text detection
2. Text region extraction
3. Script identification
4. Script-aware OCR recognition
5. Quantitative evaluation
6. Font-level robustness analysis
7. Result visualization

### Pipeline

```text
                  Input Image
                       │
                       ▼
              ┌─────────────────┐
              │  Text Detection │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Region Cropping │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │Script Identification│
              └────────┬────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
      English        Hindi        Tamil
          │            │            │
          ▼            ▼            ▼
     EN OCR Model  HI OCR Model  TA OCR Model
          │            │            │
          └────────────┼────────────┘
                       ▼
                Recognized Text
                       │
                       ▼
              ┌─────────────────┐
              │    Evaluation   │
              └────────┬────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
         CER          WER       Confidence
```

---

# Project Objectives

The project was developed with the following objectives:

- Build a multilingual OCR pipeline.
- Detect text regions from images.
- Identify the script of the detected text.
- Route text to an appropriate recognition model.
- Study OCR performance across different fonts.
- Quantitatively evaluate recognition accuracy.
- Compare generic OCR against script-aware OCR.
- Identify strengths and limitations of the recognition pipeline.

---

# Dataset

A synthetic dataset was generated to provide controlled ground-truth data for evaluation.

Each image contains a known text string rendered using a specific font.

The dataset currently contains:

| Script | Fonts | Images |
|---|---:|---:|
| English | 5 | 20 |
| Hindi | 4 | 20 |
| Tamil | 1 | 20 |
| **Total** | **10** | **60** |

The dataset is balanced by **number of images per script**, with 20 samples for each language.

However, the number of fonts differs because of available script-compatible fonts.

---

## Fonts Used

### English

- Arial
- Calibri
- Comic
- Impact
- Times

### Hindi

- Aparaj
- Kokila
- Mangal
- Utsaah

### Tamil

- Latha

---

# Synthetic Dataset Generation

The dataset is generated programmatically using **Pillow**.

Each generated image contains:

- A predefined ground-truth text string
- A selected script
- A selected font
- Fixed image dimensions
- Centered text
- White background
- Black text

The generated dataset is organized as:

```text
data/
└── dataset/
    ├── english/
    │   ├── arial/
    │   ├── calibri/
    │   ├── comic/
    │   ├── impact/
    │   └── times/
    │
    ├── hindi/
    │   ├── aparaj/
    │   ├── kokila/
    │   ├── mangal/
    │   └── utsaah/
    │
    ├── tamil/
    │   └── latha/
    │
    └── metadata.json
```

The metadata file stores:

- Image ID
- Image path
- Script
- Font
- Font file
- Ground-truth text

Example:

```json
{
    "id": 0,
    "image": "data/dataset/english/arial/english_arial_00.png",
    "script": "english",
    "font": "arial",
    "font_file": "fonts/english/arial.ttf",
    "text": "Hello World OCR Test"
}
```

---

# OCR Pipeline

## 1. Text Detection

PaddleOCR is used to detect text regions in an input image.

```text
Input Image
     │
     ▼
PaddleOCR Detector
     │
     ▼
Text Bounding Boxes
```

The detected bounding boxes identify the locations of text within the image.

---

## 2. Text Region Cropping

The detected bounding boxes are used to extract individual text regions.

```text
Detected Image
      │
      ├── Text Region 1
      ├── Text Region 2
      └── Text Region 3
```

This isolates text before recognition.

---

## 3. Script Identification

The pipeline identifies the script associated with the detected text.

Currently supported:

```text
English
Hindi / Devanagari
Tamil
```

The detected script determines which recognition model is used.

---

## 4. Script-Aware OCR

Instead of using one generic recognition configuration for every language, script-specific PaddleOCR recognition models are used.

Conceptually:

```text
                 Text Crop
                    │
                    ▼
          Script Identification
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       English    Hindi     Tamil
          │         │         │
          ▼         ▼         ▼
       EN OCR     HI OCR     TA OCR
          │         │         │
          └─────────┼─────────┘
                    ▼
             Recognized Text
```

The models used in the script-aware experiment include:

```text
en_PP-OCRv5_mobile_rec
devanagari_PP-OCRv5_mobile_rec
ta_PP-OCRv5_mobile_rec
```

---

# Quantitative Evaluation

The OCR output is compared against the known ground-truth text.

The following metrics are calculated:

- Character Error Rate (CER)
- Word Error Rate (WER)
- Recognition Confidence

---

## Character Error Rate

CER measures the number of character-level errors.

```text
CER = Edit Distance / Number of Reference Characters
```

Lower is better.

```text
CER = 0.0  → Perfect recognition
CER ≈ 1.0  → Very high recognition error
```

---

## Word Error Rate

WER measures errors at the word level.

```text
WER = Word-level Edit Distance / Number of Reference Words
```

Lower is better.

---

## Recognition Confidence

PaddleOCR also returns a recognition confidence score.

Higher confidence generally indicates that the model is more confident in its prediction.

Confidence is reported together with CER and WER to provide additional context when analyzing recognition quality.

---

# Experimental Results

The final evaluation was performed on:

```text
60 samples
3 scripts
10 fonts
```

---

## Overall Results

| Metric | Result |
|---|---:|
| Samples evaluated | 60 |
| Average CER | **0.610** |
| Average WER | **0.682** |
| Average confidence | **0.810** |

---

# Per-Script Results

| Script | Samples | CER | WER | Confidence |
|---|---:|---:|---:|---:|
| English | 20 | 0.821 | 0.988 | 0.821 |
| Hindi | 20 | 0.998 | 1.000 | 0.651 |
| Tamil | 20 | **0.013** | **0.058** | **0.956** |

### Interpretation

The results show substantial variation between scripts.

Tamil achieved the strongest recognition performance in the current experiment:

```text
CER        = 0.013
WER        = 0.058
Confidence = 0.956
```

English recognition remained challenging, particularly for some font styles.

Hindi recognition produced very high error rates, indicating that additional work is required for the current Hindi recognition configuration.

---

# CER by Script

The visualization makes the difference in recognition performance between the three scripts immediately visible.

---

# Generic OCR vs Script-Aware OCR

A baseline experiment was performed using a generic OCR recognition configuration.

The script-aware configuration was then evaluated using script-specific recognition models.

| Configuration | Average CER |
|---|---:|
| Generic OCR | 0.914 |
| Script-Aware OCR | **0.610** |

### Relative CER Reduction

```text
Generic OCR
CER = 0.914

        ↓

Script-Aware OCR
CER = 0.610

        ↓

Relative CER Reduction
= 33.26%
```

The script-aware configuration produced a:

## **33.26% relative reduction in CER**

on the current evaluation dataset.

> **Important:** This is an experimental comparison between two recognition configurations. The improvement should not be interpreted as being caused solely by script identification, since the recognition models/configuration also differ.

---

# Baseline vs Script-Aware Visualization

This visualization compares the average CER obtained using the generic OCR configuration against the script-aware configuration.

---

#  Font Robustness Analysis

The evaluation also analyzes recognition performance at the font level.

This allows the project to investigate whether recognition performance remains stable when the same script is rendered using different fonts.

---

## English Font Results

| Font | Samples | CER | WER | Confidence |
|---|---:|---:|---:|---:|
| Arial | 4 | 0.872 | 1.000 | 0.772 |
| Calibri | 4 | 0.864 | 1.000 | 0.898 |
| Comic | 4 | **0.628** | 0.938 | 0.660 |
| Impact | 4 | 0.877 | 1.000 | 0.896 |
| Times | 4 | 0.862 | 1.000 | 0.880 |

The Comic font produced the lowest CER among the evaluated English fonts.

---

## Hindi Font Results

| Font | Samples | CER | WER | Confidence |
|---|---:|---:|---:|---:|
| Aparaj | 5 | 1.000* | 1.000 | 0.668 |
| Kokila | 5 | 0.992 | 1.000 | 0.658 |
| Mangal | 5 | 0.984 | 1.000 | 0.634 |
| Utsaah | 5 | 1.000 | 1.000 | 0.645 |

Hindi recognition remained difficult across all tested fonts.

---

## Tamil Font Results

| Font | Samples | CER | WER | Confidence |
|---|---:|---:|---:|---:|
| Latha | 20 | **0.013** | **0.058** | **0.956** |

Tamil currently contains only one available font in the dataset, so conclusions about Tamil font robustness are limited.

---

# Best and Worst Performing Fonts

Based on the current experiment:

### Best Performing Font

```text
Script     : Tamil
Font       : Latha
CER        : 0.013
WER        : 0.058
Confidence : 0.956
```

### Worst Performing Font

```text
Script     : Hindi
Font       : Aparaj
CER        : ~1.000
WER        : 1.000
Confidence : 0.668
```

These results demonstrate the importance of considering both **script and font characteristics** when evaluating OCR systems.

---

# Sample Evaluation Output

The detailed evaluation is stored in:

```text
data/results/ocr_evaluation.csv
```

Each row contains:

```text
id
script
font
image
ground_truth
prediction
recognition_confidence
cer
wer
```

Example:

```text
id,script,font,image,ground_truth,prediction,recognition_confidence,cer,wer

0,english,arial,
data\dataset\english\arial\english_arial_00.png,
Hello World OCR Test,
cYanmaelaGenaYelow,
0.6458,
0.9500,
1.0000
```

This allows individual OCR predictions to be inspected rather than relying only on aggregate metrics.

---

# Project Structure

```text
ocr-pipeline/
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── detect_only.py
│   ├── crop_regions.py
│   ├── make_test_image.py
│   ├── script_identifier.py
│   ├── ocr_pipeline.py
│   ├── evaluate_ocr.py
│   ├── plot_results.py
│   └── plot_comparison.py
│
├── data/
│   ├── dataset/
│   │   ├── english/
│   │   ├── hindi/
│   │   ├── tamil/
│   │   └── metadata.json
│   │
│   └── results/
│       ├── crops/
│       ├── analysis/
│       │   ├── per_script_summary.csv
│       │   ├── per_font_summary.csv
│       │   ├── cer_by_script.png
│       │   └── baseline_vs_script_aware.png
│       │
│       └── ocr_evaluation.csv
│
├── fonts/
│   ├── english/
│   ├── hindi/
│   └── tamil/
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core implementation |
| PaddleOCR | Text detection and recognition |
| PaddleX | OCR model management |
| PaddlePaddle | Deep learning backend |
| Pillow | Synthetic image generation |
| Matplotlib | Result visualization |
| CSV | Evaluation result storage |
| JSON | Dataset metadata |

---

# Installation

## 1. Clone the repository

```bash
git clone <repository-url>
cd ocr-pipeline
```

## 2. Create a virtual environment

```bash
python -m venv venv
```

### Windows

```powershell
venv\Scripts\Activate.ps1
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

# Running the Pipeline

## Step 1 — Generate the Dataset

```bash
python src/make_test_image.py
```

This generates the synthetic multilingual dataset and creates:

```text
data/dataset/metadata.json
```

---

## Step 2 — Run Text Detection

```bash
python src/detect_only.py
```

This runs the text detector and stores the detected bounding boxes/results.

---

## Step 3 — Crop Detected Regions

```bash
python src/crop_regions.py
```

The detected text regions are cropped for recognition.

---

## Step 4 — Run OCR

```bash
python src/ocr_pipeline.py
```

This performs OCR recognition using the configured recognition models.

---

## Step 5 — Evaluate OCR

```bash
python src/evaluate_ocr.py
```

This calculates:

```text
CER
WER
Recognition Confidence
```

and saves the detailed evaluation results to:

```text
data/results/ocr_evaluation.csv
```

---

## Step 6 — Generate Analysis

The evaluation results can then be summarized by script and font.

The generated files are:

```text
data/results/analysis/per_script_summary.csv
data/results/analysis/per_font_summary.csv
```

---

## Step 7 — Generate CER Visualization

```bash
python src/plot_results.py
```

Output:

```text
data/results/analysis/cer_by_script.png
```

---

## Step 8 — Generate Baseline Comparison

```bash
python src/plot_comparison.py
```

Output:

```text
data/results/analysis/baseline_vs_script_aware.png
```

---

# 🔮 Future Improvements

Potential future extensions include:

### Dataset

- Increase the number of images
- Add more fonts
- Add more font styles
- Add real-world images
- Add image augmentation
- Add noise and blur
- Add rotation and perspective distortion

### OCR

- Improve Hindi recognition
- Fine-tune recognition models
- Evaluate additional PaddleOCR models
- Add confidence-based model selection
- Improve preprocessing

### Multilingual Support

Potential additional scripts include:

- Malayalam
- Telugu
- Kannada
- Bengali
- Gujarati
- Marathi
- Punjabi

### Evaluation

Future experiments could also include:

- Detection precision
- Detection recall
- F1-score
- Script classification accuracy
- Font classification accuracy
- Per-character confusion analysis

---

# Key Findings

The current experiment produced several useful observations.

### Finding 1 — OCR performance varies significantly across scripts

The three scripts produced very different recognition results.

```text
Tamil   → CER 0.013
English → CER 0.821
Hindi   → CER 0.998
```

This demonstrates that multilingual OCR performance cannot be assumed to be uniform across scripts.

---

### Finding 2 — Font style affects recognition

English recognition performance varied across fonts:

```text
Comic  → CER 0.628
Arial  → CER 0.872
Calibri → CER 0.864
Impact → CER 0.877
Times  → CER 0.862
```

This supports the project's focus on font-aware OCR evaluation.

---

### Finding 3 — Script-aware recognition improved the overall experiment

The generic configuration produced:

```text
CER = 0.914
```

while the script-aware configuration produced:

```text
CER = 0.610
```

giving a:

```text
33.26% relative CER reduction
```

on the current dataset.

---

### Finding 4 — Confidence alone is not sufficient

Some predictions can have relatively high confidence despite having a high CER.

For example, a model may confidently produce an incorrect string.

Therefore, evaluation should combine:

```text
Recognition Confidence
+
CER
+
WER
```

rather than relying on confidence alone.

---

# Summary

This project implements a multilingual OCR evaluation pipeline using PaddleOCR, with a focus on script-aware recognition and font robustness.

A synthetic dataset containing **60 images across English, Hindi, and Tamil** was generated using **10 fonts**. The pipeline performs text detection, region extraction, script identification, and script-specific OCR recognition.

Recognition performance is quantitatively evaluated using **Character Error Rate (CER), Word Error Rate (WER), and recognition confidence**.

The experiments achieved an overall **CER of 0.610** with the script-aware configuration compared with **0.914** for the generic baseline, representing a **33.26% relative reduction in CER** on the evaluation dataset.

The analysis also revealed substantial differences in OCR performance across scripts and fonts, with Tamil achieving a CER of **0.013**, while Hindi remained a challenging case with a CER close to **1.0**.

---

# Project Outputs

The main generated artifacts are:

```text
data/
├── dataset/
│   └── metadata.json
│
└── results/
    ├── ocr_evaluation.csv
    │
    └── analysis/
        ├── per_script_summary.csv
        ├── per_font_summary.csv
        ├── cer_by_script.png
        └── baseline_vs_script_aware.png
```

These outputs provide:

- Raw OCR predictions
- Ground-truth comparison
- Script-level metrics
- Font-level metrics
- Visual performance comparisons

---

## Project Highlights

```text
60
Synthetic OCR Samples

3
Languages / Scripts

10
Fonts

3
Evaluation Metrics

33.26%
Relative CER Reduction
```

---
