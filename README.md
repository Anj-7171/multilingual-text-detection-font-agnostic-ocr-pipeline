# Multilingual Text Detection with Font-Aware OCR Evaluation

A multilingual OCR pipeline for detecting text regions in images, identifying the text script, applying script-specific recognition models, and evaluating recognition performance across different languages and font styles.

The project uses **PaddleOCR/PaddleX** and a synthetically generated dataset containing English, Hindi, and Tamil text rendered using multiple fonts.

---

## 📌 Overview

Optical Character Recognition (OCR) performance can vary significantly depending on:

- Language and writing script
- Font style
- Text rendering
- Recognition model configuration
- Image characteristics

This project explores a lightweight multilingual OCR pipeline designed to investigate these factors systematically.

The pipeline consists of:

```text
Input Image
     │
     ▼
Text Detection
     │
     ▼
Text Region Cropping
     │
     ▼
Script Identification
     │
     ▼
Script-Specific OCR
     │
     ▼
Recognized Text
     │
     ▼
Evaluation
     │
     ├── Character Error Rate (CER)
     ├── Word Error Rate (WER)
     └── Recognition Confidence
