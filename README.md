

# Scottish Births Analytics Dashboard 👶

A comprehensive data analytics dashboard for exploring birth statistics in Scotland. This interactive Streamlit application provides insights into birth trends by region, month, age group, and includes forecasting capabilities using Facebook Prophet.

## Features

- **Interactive Data Visualization**: Explore birth data through dynamic charts and graphs
- **Regional Analysis**: Compare birth statistics across different Scottish regions
- **Temporal Trends**: Analyze patterns by month and over time
- **Age Group Insights**: Examine birth rates across different maternal age groups
- **Forecasting**: Predict future birth trends using advanced time series modeling
- **Responsive Design**: Clean, modern interface optimized for data exploration

## Dataset

The dashboard analyzes Scottish birth data including:
- Regional birth statistics
- Monthly birth patterns
- Maternal age group distributions
- Time series data for trend analysis

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Setup

1. **Clone or download the repository**
   ```bash
   git clone https://github.com/mabdullahferoz/ITSOLERA-Scotland-Birth-Project.git
   cd "ITSOLERA-Scotland-Birth-Project"
   ```

2. **Install required packages**
   
   Option 1 - Install from requirements.txt (recommended):
   ```bash
   pip install -r requirements.txt
   ```
   
   Option 2 - Install packages individually:
   ```bash
   pip install streamlit plotly seaborn matplotlib pandas openpyxl nbformat
   ```

## Usage

1. **Navigate to the project directory**
   ```bash
   cd "path/to/your/project/folder"
   ```

2. **Run the dashboard**
   ```bash
   streamlit run app.py
   ```

3. **Access the dashboard**
   - The application will automatically open in your default web browser
   - If it doesn't open automatically, navigate to `http://localhost:8501`

## Project Structure

```
├── app.py                      # Main Streamlit dashboard application
├── birth_dashboard.ipynb       # Jupyter notebook for data exploration
├── Models_on_birth_data.ipynb  # Machine learning models and analysis
├── births_plots.pkl           # Serialized plot objects
├── monthly region data.xlsx    # Source data file
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

## Dependencies

- **streamlit**: Web application framework
- **plotly**: Interactive plotting library
- **seaborn**: Statistical data visualization
- **matplotlib**: Core plotting library
- **pandas**: Data manipulation and analysis
- **openpyxl**: Excel file handling
- **nbformat**: Jupyter notebook format support

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is part of the ITSOLERA analytics portfolio.

## Contact

For questions or support, please contact the development team at ITSOLERA.

---

*Built with ❤️ using Streamlit and modern data science tools*
