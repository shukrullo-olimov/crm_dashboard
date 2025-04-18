# 📊 CRM Analytics Dashboard

An interactive data analytics dashboard built with **Streamlit**, designed to visualize and analyze CRM data of an online programming school.

---

## 🎯 Project Goal

Visualize CRM data to analyze for improve sales efficiency, identify growth points, and suggest data-driven decisions for an online programming school.

---

## 🧩 Key Features & Implementation

- 📂 File uploader for dynamic CSV input
- 📊 Charts for exploratory data analysis (EDA): bar, line, pie, and dual-axis plots
- 📞 Correlation analysis between calls and deals
- 📈 Monthly payment dynamics & ad spend ROI analysis
- 💬 Analysis of contact sources and consultation reasons
- 🗺️ Interactive deal map by city (pre-generated HTML)
- 💼 Manager-wise deal statistics
- 🔄 Dual-axis graphs, filters, and interactive layout
- 📌 Modular project structure for maintainability

---

## 🚀 Launching the App

### Option 1: Local Deployment

1. Clone the repo:
```bash
git clone https://github.com/shukrullo-olimov/crm_dashboard.git
cd crm_dashboard
```
2. (Optional) Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # on Linux/macOS
venv\Scripts\activate  # on Windows
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Run the dashboard:
```bash
streamlit run main_dashboard.py
```

### Option 2: Live Demo (Streamlit Cloud)

If you want to test it via the **Live Demo**, you'll need to:
- Download all 4 CSV files from the `/demo_data` folder.
- Then upload them one by one into the running dashboard.
- The app will display analytics based on each uploaded dataset.

🔗 [Live Demo on Streamlit Cloud](https://crmdashboard-nzwaqgbqfcuerccqes72gj.streamlit.app/)

---

## 📁 Project Structure

```
crm_dashboard/
│
├── main_dashboard.py              # Main Streamlit app
├── requirements.txt              # Project dependencies
├── assets/                       # HTML and static assets
│   └── deals_map.html
├── demo_data/                    # Preprocessed CSV data
│   ├── Cleaned_Contacts.csv
│   ├── Cleaned_Calls.csv
│   ├── Cleaned_Deals.csv
│   └── Cleaned_Payments.csv
├── modules/                      # Data processing modules
│   ├── process_contacts.py
│   ├── process_calls.py
│   ├── process_deals.py
│   └── process_spend.py
├── doc/                          # Final report and presentation
│   ├── Project_Report_EN.pdf
│   └── Presentation_EN.pdf
└── README.md                     # Project documentation
```

---

## 🔧 Built With

- Streamlit – for interactive UI
- Pandas – for data manipulation
- Plotly – for visualizations
- Folium – for map (pre-generated)
- SciPy – for statistical analysis

---

## 🤝 Author

**Shukrullo Olimov** — This project was developed as part of the final assignment for the **"Data Analyst"** course at IT Career Hub GmbH.

> 📌 Need a clean analytics dashboard for your product? Let's connect!

---

## ⭐️ Support

If you found this project helpful, consider giving it a ⭐ on GitHub!

Feel free to fork, customize, or contribute!

Made with ❤️ using Python, Streamlit, Pandas, Plotly, and CRM data for educational & demo purposes.

