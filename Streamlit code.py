import streamlit as st
import mysql.connector
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Set Seaborn style and color palette
sns.set_style("whitegrid")
sns.set_palette("pastel")

# Establish MySQL connection
connection = mysql.connector.connect(
    host='cpsc5075.c6glisumrpc8.us-east-1.rds.amazonaws.com', 
    user='admin', 
    password='password*', 
    database='urbancollective'
)

cursor = connection.cursor()

# Define queries and parameters
queries = {
    "1": {
        "description": "Products with above-average ratings and a minimum number of reviews defined by the user",
        "query": """
            SELECT 
                p.ProductID,
                p.Product_Description,
                AVG(pr.ProductReview_Value) AS Avg_ProductReview_Value,
                COUNT(pr.ProductReview_Value) AS Total_Reviews
            FROM 
                product p
            LEFT JOIN 
                productreview pr ON p.ProductID = pr.ProductID
            GROUP BY 
                p.ProductID, p.Product_Description
            HAVING 
                AVG(pr.ProductReview_Value) > (SELECT AVG(ProductReview_Value) FROM productreview) AND
                COUNT(pr.ProductReview_Value) > %s
            ORDER BY 
                Avg_ProductReview_Value DESC;
        """,
        "parameters": ["Minimum_Reviews"]
    },
    "2": {
        "description": "Customer Lifetime Value (CLV) for top 10 highest-spending customers with at least a number of orders defined by the user",
        "query": """
            SELECT 
                c.CustomerID,
                c.Customer_FName,
                c.Customer_Email,
                SUM(od.OrderDetail_Value) AS Total_Spent,
                COUNT(DISTINCT o.OrderID) AS Total_Orders,
                SUM(od.OrderDetail_Value) / COUNT(DISTINCT o.OrderID) AS Average_Order_Value
            FROM 
                customer c
            JOIN 
                `orders` o ON c.CustomerID = o.CustomerID
            JOIN 
                orderdetail od ON o.OrderID = od.OrderID
            GROUP BY 
                c.CustomerID
            HAVING 
                Total_Orders >= %s
            ORDER BY 
                Total_Spent DESC
            LIMIT 
                10;
        """,
        "parameters": ["Minimum_Orders"]
    },
    "3": {
        "description": "Top 10 performing stores where total orders are higher or equal to a number defined by the user",
        "query": """
            SELECT   
                s.StoreID,  
                s.Store_Description,  
                s.Store_Category,  
                SUM(od.OrderDetail_Value) AS Total_Spent,  
                COUNT(DISTINCT o.OrderID) AS Total_Orders,  
                SUM(od.OrderDetail_Value) / COUNT(DISTINCT o.OrderID) AS Average_Order_Value  
            FROM   
                store s  
            JOIN   
                orderdetail od ON od.StoreID = s.StoreID  
            JOIN   
                orders o  ON o.OrderID = od.OrderID  
            GROUP BY   
                s.StoreID  
            HAVING   
                Total_Orders >= %s  
            ORDER BY   
                Total_Spent DESC  
            LIMIT   
                10;
        """,
        "parameters": ["Minimum_Orders"]
    },
    "4": {
        "description": "Top 10 payment ID/types where the average order value is more than a defined value",
        "query": """
            SELECT   
                p.PaymentID,  
                p.Payment_Description,  
                SUM(od.OrderDetail_Value) AS Total_Spent,  
                COUNT(DISTINCT o.OrderID) AS Total_Orders,  
                SUM(od.OrderDetail_Value) / COUNT(DISTINCT o.OrderID) AS Average_Order_Value  
            FROM   
                payment p  
            JOIN   
                orders o ON o.PaymentID = p.PaymentID  
            JOIN   
                orderdetail od ON od.OrderID = o.OrderID  
            GROUP BY   
                p.PaymentID  
            HAVING   
                Average_Order_Value >= %s  
            ORDER BY   
                Total_Spent DESC  
            LIMIT   
                10;
        """,
        "parameters": ["Minimum_Average_Order_Value"]
    },
    "5": {
        "description": "Top Zip Codes by Total Sales Value and Number of Orders, limited by a number defined by the user",
        "query": """
            WITH RankedZipcodes AS (
                SELECT    
                    a.Address_Zipcode,   
                    COUNT(DISTINCT o.OrderID) AS Total_Orders,   
                    SUM(o.Order_Value) AS Total_Sales_Value,   
                    AVG(o.Order_Value) AS Average_Order_Value,
                    ROW_NUMBER() OVER (ORDER BY SUM(o.Order_Value) DESC) AS rn
                FROM    
                    address a   
                JOIN    
                    orders o ON a.OrderID = o.OrderID   
                GROUP BY    
                    a.Address_Zipcode   
            )
            SELECT 
                Address_Zipcode,
                Total_Orders,
                Total_Sales_Value,
                Average_Order_Value
            FROM 
                RankedZipcodes
            WHERE 
                rn <= %s;
        """,
        "parameters": ["Limit_Zipcodes"]
    }
}

# Function to execute a selected query
def run_query(query_key, parameter_values=None):
    query_data = queries.get(query_key)

    if query_data:
        query = query_data["query"]
        parameters = query_data.get("parameters", [])

        # Execute the query with parameters if they exist
        if parameters and parameter_values:
            try:
                cursor.execute(query, parameter_values)
            except mysql.connector.Error as err:
                return f"Error executing the query: {err}"

        # Execute the query without parameters
        else:
            try:
                cursor.execute(query)
            except mysql.connector.Error as err:
                return f"Error executing the query: {err}"

        # Fetch and return results as a DataFrame
        results = cursor.fetchall()
        headers = [x[0] for x in cursor.description]
        df = pd.DataFrame(results, columns=headers)
        return df

# Fetch matching customer IDs
def fetch_matching_customer_ids(prefix):
    cursor.execute("SELECT CustomerID FROM customer WHERE CustomerID LIKE %s LIMIT 10", (prefix + '%',))
    return [str(row[0]) for row in cursor.fetchall()]

# Fetch matching order IDs
def fetch_matching_order_ids(prefix):
    cursor.execute("SELECT OrderID FROM `orders` WHERE OrderID LIKE %s LIMIT 10", (prefix + '%',))
    return [str(row[0]) for row in cursor.fetchall()]

# Function to create a dashboard
def create_dashboard():
    # Total Customers
    cursor.execute("SELECT COUNT(*) FROM customer")
    total_customers = cursor.fetchone()[0]

    # Total Orders
    cursor.execute("SELECT COUNT(*) FROM `orders`")
    total_orders = cursor.fetchone()[0]

    # Total Revenue
    cursor.execute("SELECT SUM(OrderDetail_Value) FROM orderdetail")
    total_revenue = cursor.fetchone()[0]

    # Average Order Value
    cursor.execute("SELECT AVG(OrderDetail_Value) FROM orderdetail")
    avg_order_value = cursor.fetchone()[0]

    st.subheader("Dashboard Overview")
    col1, col2 = st.columns(2)
    col1.metric("Total Customers", total_customers)
    col2.metric("Total Orders", total_orders)
    col1.metric("Total Revenue", f"${total_revenue:,.2f}")
    col2.metric("Average Order Value", f"${avg_order_value:,.2f}")

    # Revenue by Month
    cursor.execute("""
        SELECT 
            DATE_FORMAT(Order_Date, '%Y-%m') AS Month,
            SUM(od.OrderDetail_Value) AS Revenue
        FROM `orders` o
        JOIN orderdetail od ON o.OrderID = od.OrderID
        GROUP BY Month
        ORDER BY Month
    """)
    revenue_by_month = cursor.fetchall()
    df_revenue_by_month = pd.DataFrame(revenue_by_month, columns=["Month", "Revenue"])

    
    if revenue_by_month:
        df_revenue_by_month = pd.DataFrame(revenue_by_month, columns=["Month", "Revenue"])

        st.subheader("Monthly Revenue")
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df_revenue_by_month, x="Month", y="Revenue", marker='o', linewidth=2)
        plt.title("Monthly Revenue")
        plt.xlabel("Month")
        plt.ylabel("Revenue")
        plt.xticks(rotation=45)
        st.pyplot(plt)
    else:
        st.warning("No data available for monthly revenue.")

    # Top 5 Products by Revenue
    cursor.execute("""
        SELECT 
            p.Product_Description,
            SUM(od.OrderDetail_Value) AS Total_Revenue
        FROM orderdetail od
        JOIN product p ON p.ProductID = od.ProductID
        GROUP BY p.Product_Description
        ORDER BY Total_Revenue DESC
        LIMIT 5
    """)
    top_products = cursor.fetchall()
    df_top_products = pd.DataFrame(top_products, columns=["Product", "Total_Revenue"])

    if top_products:
        df_top_products = pd.DataFrame(top_products, columns=["Product", "Total_Revenue"])

        st.subheader("Top 5 Products by Revenue")
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df_top_products, x="Product", y="Total_Revenue")
        plt.title("Top 5 Products by Revenue")
        plt.xlabel("Product")
        plt.ylabel("Total Revenue")
        plt.xticks(rotation=45, ha='right')
        st.pyplot(plt)
    else:
        st.warning("No data available for top 5 products by revenue.")

# Main Streamlit app
def main():
    st.title("Urban Collective Reporting System")

    # Description of the tool
    st.sidebar.write("""
    Welcome to the Urban Collective Reporting System. This tool allows you to:
    - **Search** for specific customer or order information.
    - **Generate reports** based on predefined queries.
    - **View dashboards** to get an overview of key metrics and visualizations.
    """)

    # Sidebar menu options
    st.sidebar.title("Menu")
    option = st.sidebar.selectbox("Choose an option", ["Search", "Reporting Tool", "Dashboard"])

    if option == "Search":

        st.subheader("Search for Specific Customer or Order ID")

        search_type = st.radio("Search by:", ("Customer ID", "Order ID"))
        search_prefix = st.text_input(f"Start typing {search_type}:")

        if search_type == "Customer ID" and search_prefix:
            customer_ids = fetch_matching_customer_ids(search_prefix)
            search_value = st.selectbox("Select Customer ID:", customer_ids)

        elif search_type == "Order ID" and search_prefix:
            order_ids = fetch_matching_order_ids(search_prefix)
            search_value = st.selectbox("Select Order ID:", order_ids)

        if st.button("Search"):
            if search_type == "Customer ID":
                # Fetch customer info
                cursor.execute("SELECT * FROM customer WHERE CustomerID = %s", (search_value,))
                customer_result = cursor.fetchall()
                customer_headers = [x[0] for x in cursor.description]
                customer_df = pd.DataFrame(customer_result, columns=customer_headers)

                # Fetch order info related to the customer
                cursor.execute("SELECT * FROM `orders` WHERE CustomerID = %s", (search_value,))
                order_result = cursor.fetchall()
                order_headers = [x[0] for x in cursor.description]
                order_df = pd.DataFrame(order_result, columns=order_headers)

                if not order_df.empty:
                    # Fetch order detail info related to the orders
                    order_ids = tuple(order_df['OrderID'])
                    order_ids_placeholder = ', '.join(['%s'] * len(order_ids))
                    cursor.execute(f"""
                        SELECT 
                            od.OrderID,
                            p.Product_Description,
                            od.OrderDetail_Size,
                            od.OrderDetail_Color,
                            od.OrderDetail_Value
                        FROM orderdetail od
                        INNER JOIN product p ON p.ProductID = od.ProductID
                        WHERE od.OrderID IN ({order_ids_placeholder})
                    """, order_ids)
                    order_detail_result = cursor.fetchall()
                    order_detail_headers = [x[0] for x in cursor.description]
                    order_detail_df = pd.DataFrame(order_detail_result, columns=order_detail_headers)

                    st.subheader("Customer Information")
                    st.write(customer_df)

                    st.subheader("Orders by Customer")
                    st.write(order_df)

                    st.subheader("Order Details")
                    st.write(order_detail_df)
                else:
                    st.write("No orders found for this customer.")

            elif search_type == "Order ID":
                # Fetch order info
                cursor.execute("SELECT * FROM `orders` WHERE OrderID = %s", (search_value,))
                order_result = cursor.fetchall()
                order_headers = [x[0] for x in cursor.description]
                order_df = pd.DataFrame(order_result, columns=order_headers)

                # Fetch order detail info related to the order
                cursor.execute("""
                    SELECT 
                        od.OrderID,
                        p.Product_Description,
                        od.OrderDetail_Size,
                        od.OrderDetail_Color,
                        od.OrderDetail_Value
                    FROM orderdetail od
                    INNER JOIN product p ON p.ProductID = od.ProductID
                    WHERE od.OrderID = %s
                """, (search_value,))
                order_detail_result = cursor.fetchall()
                order_detail_headers = [x[0] for x in cursor.description]
                order_detail_df = pd.DataFrame(order_detail_result, columns=order_detail_headers)

                # Fetch customer info related to the order
                cursor.execute("SELECT * FROM customer WHERE CustomerID = %s", (order_df.iloc[0]['CustomerID'],))
                customer_result = cursor.fetchall()
                customer_headers = [x[0] for x in cursor.description]
                customer_df = pd.DataFrame(customer_result, columns=customer_headers)

                st.subheader("Order Information")
                st.write(order_df)

                st.subheader("Order Details")
                st.write(order_detail_df)

                st.subheader("Customer Information")
                st.write(customer_df)

    elif option == "Reporting Tool":
        st.subheader("Reporting Tool")

        # Display all query descriptions
        for key, query_data in queries.items():
            st.write(f"{key}: {query_data['description']}")

        # Get user input for the selected query
        query_choice = st.text_input("Enter the query number:")

        # Check if the entered value is a valid query number
        if query_choice in queries:
            query_data = queries[query_choice]
            parameters = query_data.get("parameters", [])

            # Display selected query name and description
            st.write(f"Name: {query_choice}")
            st.write(f"Description: {query_data['description']}")

            # Get parameter values if parameters exist
            parameter_values = []
            for param in parameters:
                value = st.text_input(f"Enter value for {param.replace('_', ' ')}:")
                parameter_values.append(value)

            # Execute query on button click
            if st.button("Run Query"):
                results_df = run_query(query_choice, parameter_values)

                # Display results
                if not results_df.empty:
                    st.subheader("Query Results:")
                    st.write(results_df)

                    # Add button to export to CSV
                    csv_file = results_df.to_csv(index=False)
                    st.download_button(
                        label="Export to CSV",
                        data=csv_file,
                        file_name="query_results.csv",
                        mime="text/csv"
                    )
        else:
            st.warning("Please enter a valid query number.")

    elif option == "Dashboard":
        create_dashboard()

if __name__ == "__main__":
    main()
