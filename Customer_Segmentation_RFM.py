##### 1.Business Understanding #####

#An e-commerce company wants to segment its customers and determine marketing strategies according to these segments.
#So, we will define the behavior of customers and create groups according to clusters in these behaviors.

##### 2.Data Understanding #####

import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

df_ = pd.read_excel("3.HAFTA/Ders Öncesi Notlar/online_retail_II.xlsx", sheet_name="Year 2010-2011")
df = df_.copy()

# descriptive statistics for the data set

df.describe().T
# We have observed that the minimum takes negative values as a result of the output.
# Therefore, we can understand that something is wrong with the Quantity and Price.

df.head(5)

# How many of each product are there?
df["Description"].value_counts().head()

#Which is the most ordered product?
df.groupby("Description").agg({"Quantity": "sum"}).head()

#How much money was earned from each country?
df.groupby("Country").agg({"TotalPrice": "sum"}).sort_values("TotalPrice", ascending=False).head()


##### 3.Data Preparation #####

#checking missing values and dropping if we have
df.isnull().sum()
df.dropna(inplace=True)


#Containing "C" means refundees,so we'll consider those that don't contain C.
df = df[~df["Invoice"].str.contains("C", na=False)]

# After excluding C's we are not expecting negative values.
df = df[(df['Quantity'] > 0)]  #Burda iadeler cıktıgı için daha negatif değer kalmasını beklemiyoruz zaten.
df = df[(df['Price'] > 0)]


##### 4.Calculating RFM Metrics #####


df["InvoiceDate"].max()

today_date = dt.datetime(2011, 12, 11)


rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     'Invoice': lambda Invoice: Invoice.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})

rfm.head()

rfm.columns = ['recency', 'frequency', 'monetary']
rfm = rfm[rfm["monetary"] > 0]

##### 5.Generating RFM Scores #####

# Recency
# 1 is the closest date and 5 is the furthest date.
# The most important situation for us is the most recent date, 1, so it has a higher importance than 5.
rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])


# Frequency
# 1 represents the lowest frequency and 5 the highest frequency.
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

# Monetary
# 1 represents the least amount of money and 5 represents the most money.
rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])


rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str))

rfm.head()


##### Defining RFM segments #####

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}
#Merged scores has changed according to seg_map
rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
rfm.head()


rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

rfm[rfm["segment"] == "new_customers"].index

rfm[rfm["segment"] == "need_attention"].head()