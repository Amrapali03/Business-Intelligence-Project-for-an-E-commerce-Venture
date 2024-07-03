# Business-Intelligence-Project with Interactive Website and Dashboard
## Retail Venture Name: Urban Collective

![image](https://github.com/Amrapali03/Interactive-End-to-end-Retail-Business-Intelligence-Project/assets/114306627/e28e5565-8692-4e92-a005-3b61b9b14250)

This document provides an overview of Urban Collective's business intelligence (BI) project, focusing on their retail operations and data management strategies.
Business Plan and Background
Urban Collective is a growing apparel retailer with 89 stores in Columbia and annual sales exceeding $2 million.
The company faces challenges in sustaining growth and customer retention.
Current marketing efforts are costly, and there is limited repeat patronage.

## BI Justification
Challenges: Data is scattered across various local databases, CRM systems, and spreadsheets.
Solution: Implement a centralized data warehouse to integrate these sources and provide comprehensive business insights.
Goals: Increase customer retention and repeat purchases by at least 30%, reduce marketing costs by 30%, and increase revenue by 20%.

## BI Architecture
Components: The BI architecture includes the System of Record (Operational Database), the System of Integration (ETL Process), and the System of Analytics (Data Warehouse/Data Mart).
Data Management: MySQL is used for the operational database. Data is ingested from multiple sources, cleaned, transformed, and loaded into the data warehouse using ETL tools.
Tools: Tableau and Power BI are planned for data visualization and reporting.

## ER Diagram and Data Population
An entity-relationship (ER) model is created to manage customer, order, and product data.
Data is populated into the database from CSV files, cleansed, and transformed using CloverDX, then moved to an AWS cloud database.

## CloverDX Pipeline
Process: Data is moved from the operational database to the analytical database (UrbanCollective) in AWS.
Data Cleaning: Invalid values are filtered out, data is standardized, and incorrect records are corrected or removed.
Execution: Instructions are provided for running the CloverDX pipeline to ensure data is correctly migrated and transformed.


## Analytical Queries
Product Ratings:

Retrieves products with above-average ratings and more than 5 reviews.
Helps in promoting highly rated products to build customer trust and encourage purchases.
Customer Lifetime Value (CLV):

Calculates CLV for the top 10 highest-spending customers with at least 2 orders.
Focuses on retaining high-value customers to improve profitability.
Top Performing Stores:

Identifies stores with order values higher than or equal to 50.
Provides insights into which stores are driving the most revenue.
Top Payment Methods:

Identifies payment methods associated with higher spending.
Helps optimize payment processing options and improve customer satisfaction.

## Python and Streamlit
To create an interactive solution, we leverage Python and Streamlit, a powerful framework for building data applications. 
The connection to our RDS database is established using the mysql.connector library, enabling secure and efficient data retrieval.
Streamlit facilitates the creation of a dynamic web interface that allows users to execute predefined queries, visualize results, and interact with the data. 
The functionality is built around key modules such as pandas for data manipulation, seaborn and matplotlib for data visualization, and Streamlit's own components for user input and output. 
Website Link: https://urbancollective-report.streamlit.app/ ( This has been created on top of AWS database, with time as a student I might loose access to AWS hence below screenshots are provided)

The homepage looks like this:
![image](https://github.com/Amrapali03/Urban-Collective-s-business-intelligence-Project/assets/114306627/0dd08700-c10e-47bd-9701-c54ecc597bc3)

Below is how this webpage helps to interact with data and get the details:
![image](https://github.com/Amrapali03/Urban-Collective-s-business-intelligence-Project/assets/114306627/cdbeeca8-dc40-43e0-beb2-df4bc2a06b88)
![image](https://github.com/Amrapali03/Urban-Collective-s-business-intelligence-Project/assets/114306627/9bd75a59-8828-484b-ac9c-ee5d0efa2d8c)



## Tableau Dashboard
Link: https://public.tableau.com/app/profile/amrapali.samanta4121/viz/UrbanCollective2024Dashboard_17168737322560/Dashboard1?publish=yes

![image](https://github.com/Amrapali03/Urban-Collective-s-business-intelligence-Project/assets/114306627/3f3703fe-d7bb-459a-883b-445c4dbcd08a)
