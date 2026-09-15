# 🧠 Mental Health in Tech — Survey Analysis & Dashboard

App Link: https://mental-health-project-vfhy7pofondgcdosmmsjmu.streamlit.app/

An end-to-end data analysis project on the **2014 OSMI Mental Health in Tech Survey**, exploring how mental health is perceived, supported, and disclosed in tech workplaces — and what actually drives employees to seek treatment.

The project has two parts:
1. **Exploratory Data Analysis** (Jupyter Notebook) — data cleaning, 15 visualizations, and business insights.
2. **Interactive Dashboard** (Streamlit app) — a filterable, multi-tab web app for exploring the same data live.

---

## 📊 Dataset

- **Source:** [Open Sourcing Mental Illness (OSMI)](https://osmihelp.org/) 2014 Mental Health in Tech Survey
- **File:** `survey.csv`
- **Size:** 1,259 responses × 27 columns
- **Covers:** demographics (age, gender, country), employer characteristics (company size, remote work), mental health support infrastructure (benefits, care options, anonymity, leave policy), and personal attitudes toward disclosing mental health issues at work.

Full column descriptions are in `Mental_Health_in_Tech_Survey.pdf`.

---

## 🔑 Key Findings

| Finding | Detail |
|---|---|
| **Treatment is common** | ~50.6% of respondents have sought mental health treatment. |
| **Family history is the strongest predictor** | 74% of those with a family history of mental illness sought treatment, vs. only 35% of those without. |
| **Awareness beats availability** | Employees who *know* their care options seek treatment at 69%, vs. 41% for "No" and just 39% for "Not sure" — not knowing what's available is worse than having no benefits at all. |
| **Supervisor trust gap** | Employees are more comfortable discussing mental health with coworkers than with direct supervisors. |
| **Leave policy is unclear** | A large share of respondents don't know how easy it would be to take mental-health leave. |
| **Age & remote work are not strong differentiators** | Treatment-seeking rates are similar across age groups and remote vs. in-office workers. |

---

## 📁 Project Structure

```
├── Mental_Health_Tech_Survey_EDA.ipynb   # Full EDA notebook (cleaning + 15 charts + insights)
├── Mental_Health_in_Tech_Survey.pdf      # Column/question reference for the dataset
├── survey.csv                            # Raw survey data
├── app.py                                # Interactive Streamlit dashboard
├── requirements.txt                      # Python dependencies
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/mental-health-tech-survey.git
cd mental-health-tech-survey
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3a. Run the EDA notebook
```bash
jupyter notebook Mental_Health_Tech_Survey_EDA.ipynb
```

### 3b. Run the interactive dashboard
```bash
streamlit run app.py
```
Then open the local URL Streamlit prints (usually `http://localhost:8501`). `survey.csv` should sit in the same folder as `app.py`, or you can upload it from the sidebar.

---

## 🖥️ Dashboard Features

- **Sidebar filters:** country, gender, age range, company size, treatment status
- **KPI cards:** live respondent count, treatment rate, family history rate, benefits rate, care-options awareness
- **Overview tab:** treatment split, age distribution, top countries, company size
- **Demographics tab:** gender breakdown, age group vs. treatment, age-by-treatment box plot
- **Workplace Support tab:** interactive comparison of any support factor (benefits, care options, wellness program, seek help, anonymity, remote work) against treatment-seeking, plus leave-ease breakdown
- **Attitudes tab:** willingness to discuss mental health with coworkers/supervisors, fear of consequences, observed consequences
- **Correlations tab:** heatmap of encoded key variables
- **Raw Data tab:** browsable, filtered dataset with CSV export

---

## 🛠️ Tech Stack

- **Analysis:** Python, Pandas, NumPy
- **EDA Visualizations:** Matplotlib, Seaborn
- **Dashboard:** Streamlit, Plotly

---

## 💡 Business Recommendations

1. **Communicate benefits and care options clearly and repeatedly** — awareness has a bigger effect on treatment-seeking than benefits alone.
2. **Train managers** to handle mental health disclosures supportively, closing the coworker–supervisor trust gap.
3. **Publish a clear, easy-to-find mental health leave policy** to remove uncertainty and friction.
4. Apply support programs **broadly across the workforce** rather than narrowly by age or work-location, while proactively reaching employees with a family history of mental illness.

---

## 📄 License

This project is released under the [MIT License](LICENSE). The underlying survey data is provided by OSMI under their own terms — see [osmihelp.org](https://osmihelp.org/) for details.

---

## 🙌 Acknowledgements

- Dataset: [Open Sourcing Mental Illness (OSMI)](https://osmihelp.org/)
- Built as part of an EDA capstone project.
