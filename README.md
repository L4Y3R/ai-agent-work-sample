# Air Quality Data Analysis Assistant

An AI-powered assistant that analyzes air quality datasets from multiple rooms, generating Python code dynamically to answer user queries with timezone-aware, cleanly formatted results. Built with FastAPI, OpenAI GPT, and Pandas.

---

## Features

- Load and normalize air quality data from `.ndjson` files.
- Dynamic Python code generation using OpenAI's GPT-4o-mini model.
- Robust handling of timezone-aware timestamps and pandas best practices.
- Clear, human-readable output with proper formatting and rounding.
- Supports light mode and dark mode UI themes.
- Responsive design for seamless experience on mobile devices.
- Loading screen to indicate data fetching and processing status.

---

## Demo Screenshots

### Loading Screen  
![Loading Screen](./screenshots/loading.png)

### Light Mode  
![Light Mode](./screenshots/lightmode.png)

### Dark Mode  
![Dark Mode](./screenshots/darkmode.png)

### Mobile Responsiveness  
![Mobile Responsive](./screenshots/mobile.png)

---

## Getting Started

### Prerequisites

- Python 3.9+
- An OpenAI API key (set as environment variable `OPENAI_API_KEY`)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
