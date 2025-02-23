# Data Analysis Project

This repository demonstrates a full data analysis workflow with the following components:
- **Data ingestion and cleaning**
- **Exploratory data analysis (EDA)**
- **Model building** (regression, classification, clustering)
- **Integration with Metabase** for visualization

---


### Highlights

1. **`data/`**  
   - `raw/` contains original data files.  
   - `cleaned/` holds processed data after cleaning and transformations.

2. **`orm_models/`**  
   - Defines Python classes mapping to database tables.  
   - `base.py` usually contains the Base class or shared logic (if using SQLAlchemy).

3. **`notebooks/`**  
   - Separated into subfolders by analysis stage (e.g., exploratory, modeling).  
   - `templates/` stores starter notebooks and repeated patterns.

4. **`scripts/`**  
   - Utility scripts for data cleaning, database interactions, and Metabase integration.

5. **Docker Compose**  
   - `docker-compose-analysis.yml` provides a containerized environment for running analysis.  
   - `docker-compose-metabase.yml` spins up Metabase for dashboards.

---

## Environment Setup

1. **Install Python dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
   (Or adapt if you use Poetry/Pipenv.)

2. **Configure your environment**:
    - Update any parameters in `config/config.yaml`.
    - (Optional) Create a `.env` file if needed for secret credentials.

3. **Run Docker containers**:
    ```bash
    # Analysis environment
    docker-compose -f docker-compose-analysis.yml up -d
    
    # Metabase environment
    docker-compose -f docker-compose-metabase.yml up -d
    ```
   This will set up a local environment to run analyses and serve Metabase dashboards.

---

## Usage

1. **Data Cleaning**:  
   - Run `scripts/data_cleaning.py` to transform raw data into the cleaned format.
3. **Modeling**:  
   - Explore different models in `notebooks/modeling/`, organized by model type (regression, classification, clustering, etc.).
4. **ORM Models**:  
   - Check `orm_models/` for database schema definitions if you want to load data into a relational database.

---

## License

This project is provided under the [MIT License](LICENSE) (or any license of your choice).  