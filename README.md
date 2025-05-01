# eCFR Analyzer

## Overview

The Electronic Code of Federal Regulations (eCFR) Analyzer is a tool for analyzing and visualizing the volume of federal regulations across different government agencies and their inner agencies.

This application provides insights into:
- Total word count and section count for 153 federal agencies
- Detailed metrics for 163 inner agencies
- Comparative analysis of regulatory volume

## Data Source

The data was collected on May 1, 2025 from [CFR-Metrics.com](https://cfr-metrics.com) and represents a snapshot of the Federal Regulations as they existed at that time.

## Key Findings

- The Department of Treasury has the highest word count of any agency (15,120,613 words in 16,768 sections)
- The Internal Revenue Service alone accounts for 13,013,629 words of regulations
- The Department of Agriculture has the second highest word count with 13,566,594 words across 39,902 sections
- The total dataset includes 104,372,225 words and 231,304 sections

## Project Structure

- `/server`: Go backend server with APIs to access eCFR data
- `/ui`: Next.js frontend for visualization
- `agency_metrics.json`: Complete dataset of all agency metrics

## Local Development

### Running the Backend

```bash
cd server
go run server.go
```

The server will start on port 8090.

### Running the Frontend

```bash
cd ui
npm run dev
```

The UI will be available at http://localhost:3000.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
