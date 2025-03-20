import streamlit as st
import pandas as pd
import plotly.express as px

# Title
st.title("Northwind Traders Dashboard")

# Load CSV files
orders = pd.read_csv("orders.csv")
orderDetails = pd.read_csv("order-details.csv")
products = pd.read_csv("products.csv")
customers = pd.read_csv("customers.csv")
shippers = pd.read_csv("shippers.csv")
employees = pd.read_csv("employees.csv")

# Ensure orderID and productID are int64, dropping rows with NaN
orders["orderID"] = pd.to_numeric(orders["orderID"], errors='coerce')
orders = orders.dropna(subset=["orderID"])
orders["orderID"] = orders["orderID"].astype('int64')

orderDetails["orderID"] = pd.to_numeric(orderDetails["orderID"], errors='coerce')
orderDetails = orderDetails.dropna(subset=["orderID"])
orderDetails["orderID"] = orderDetails["orderID"].astype('int64')

products["productID"] = pd.to_numeric(products["productID"], errors='coerce')
products = products.dropna(subset=["productID"])
products["productID"] = products["productID"].astype('int64')

# Ensure shipperID and employeeID are int64
shippers["shipperID"] = pd.to_numeric(shippers["shipperID"], errors='coerce').astype('int64')
employees["employeeID"] = pd.to_numeric(employees["employeeID"], errors='coerce').astype('int64')

# Merge orders with shippers to get company names
orders = pd.merge(orders, shippers[["shipperID", "companyName"]], left_on="shipVia", right_on="shipperID", how="left")
orders = orders.drop(columns=["shipVia", "shipperID"])  # Replace shipVia with companyName

# Merge orders and orderDetails for sales data, then add employee names
salesData = pd.merge(orders, orderDetails, on="orderID")
salesData = pd.merge(salesData, employees[["employeeID", "firstName", "lastName"]], on="employeeID", how="left")
salesData["employeeName"] = salesData["firstName"] + " " + salesData["lastName"]
salesData["totalSales"] = salesData["unitPrice"] * salesData["quantity"] * (1 - salesData["discount"])

# Convert orderDate to datetime
salesData["orderDate"] = pd.to_datetime(salesData["orderDate"], errors='coerce')

# Visualization 1: Sales Over Time
st.subheader("Total Sales Over Time")
salesOverTime = salesData.groupby("orderDate")["totalSales"].sum().reset_index()
fig1 = px.line(salesOverTime, x="orderDate", y="totalSales", title="Sales Trend")
st.plotly_chart(fig1)

# Visualization 2: Top 10 Products by Sales
st.subheader("Top 10 Products by Sales")
productSales = pd.merge(orderDetails, products, on="productID")
productSales["totalSales"] = productSales["unitPrice_x"] * productSales["quantity"] * (1 - productSales["discount"])
topProducts = productSales.groupby("productName")["totalSales"].sum().reset_index().sort_values(by="totalSales", ascending=False).head(10)
fig2 = px.bar(topProducts, x="productName", y="totalSales", title="Top Products by Sales")
st.plotly_chart(fig2)

# Visualization 3: Customers by Country
st.subheader("Customer Distribution by Country")
customerDist = customers["country"].value_counts().reset_index()
customerDist.columns = ["country", "customerCount"]
fig3 = px.pie(customerDist, names="country", values="customerCount", title="Customers by Country")
st.plotly_chart(fig3)

# Visualization 4: Most Ordered Products by Customer Country
st.subheader("Most Ordered Products by Customer Country")
orderCustomer = pd.merge(orders, customers, on="customerID")
orderCustomerProduct = pd.merge(orderCustomer, orderDetails, on="orderID")
orderCustomerProduct = pd.merge(orderCustomerProduct, products, on="productID")
productByCountry = orderCustomerProduct.groupby(["country", "productName"])["orderID"].count().reset_index()
productByCountry.columns = ["country", "productName", "orderCount"]
topProductByCountry = productByCountry.groupby("country").apply(lambda x: x.nlargest(5, "orderCount")).reset_index(drop=True)
fig4 = px.bar(topProductByCountry, x="country", y="orderCount", color="productName", 
              title="Top 5 Most Ordered Products by Country", barmode="group")
st.plotly_chart(fig4)

# Visualization 5: Sales by Employee (using employee names)
st.subheader("Sales by Employee")
salesByEmployee = salesData.groupby("employeeName")["totalSales"].sum().reset_index()
fig5 = px.bar(salesByEmployee, x="employeeName", y="totalSales", title="Total Sales by Employee",
              text=salesByEmployee["totalSales"].round(2).astype(str))
fig5.update_traces(textposition='auto')
st.plotly_chart(fig5)

# Visualization 6: Order Count by Shipping Company (using companyName)
st.subheader("Order Distribution by Shipping Company")
shipMethodDist = orders["companyName"].value_counts().reset_index()
shipMethodDist.columns = ["companyName", "orderCount"]
fig6 = px.pie(shipMethodDist, names="companyName", values="orderCount", title="Orders by Shipping Company")
st.plotly_chart(fig6)

# Sidebar with filters
st.sidebar.header("Filters")
selectedYear = st.sidebar.slider("Select Year", 1996, 1998, 1997)  # Adjust years based on your data
filteredSales = salesData[salesData["orderDate"].dt.year == selectedYear]
st.subheader(f"Sales in {selectedYear}")
fig7 = px.line(filteredSales.groupby("orderDate")["totalSales"].sum().reset_index(), x="orderDate", y="totalSales")
st.plotly_chart(fig7)

# Run the dashboard
if __name__ == "__main__":
    st.sidebar.write("Dashboard running on Streamlit")