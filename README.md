# Skill 1.2B-1: Funnel Stage Definition & Conversion Analysis

## Overview

This skill analyzes user conversion through key stages of the product journey. It identifies where users drop off and which stages are bottlenecks.

## Stages Defined

| Stage | Description | Criteria |
|-------|-------------|----------|
| Registered | User created account | Has signup record |
| First Use | User sent at least one message | First message sent |
| First Value (HVA) | User completed a high-value action | Code execution / file upload / 5+ turns |
| Repeat Usage | User came back within 7 days | 2+ active days in first week |
| Sustained Usage | User used for 3+ consecutive weeks | Weekly active for 3 weeks |

## What is HVA (High-Value Action)?

HVA represents deep engagement that indicates real product value:

- **Code execution**: User runs AI-generated code successfully
- **File analysis**: User uploads and analyzes files (CSV, PDF, etc.)
- **Deep conversation**: Single session with 5+ turns
- **Long-form writing**: 500+ words using Canvas
- **Export/Share**: User copies or exports AI output

## Quick Start

```bash
# Install dependencies
pip install pandas numpy jinja2

# Run analysis (auto-generates sample data if not exists)
python3 funnel_analysis.py

# Open the report
open output/report.html
