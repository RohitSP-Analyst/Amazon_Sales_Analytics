# Amazon_Sales_Analytics

# Business Intelligence & Sales Analytics Platform

## Overview

An end-to-end Business Intelligence project that collects real product data from Amazon, stores and analyzes it in MySQL, and delivers actionable business insights through an interactive Power BI dashboard.

The project demonstrates the complete analytics lifecycle: **Data Collection → Data Engineering → SQL Analysis → Business Reporting**.

---

## Dataset

The dataset was built using real product information scraped from Amazon across multiple categories, including:

* Technology (Computers, Audio, Wearables)
* Furniture (Chairs, Tables)
* Home & Kitchen (Appliances)
* Apparel (Footwear, Bags)

### Product Attributes Collected

* ASIN
* Product Title
* Brand
* Category & Sub-Category
* Price & MRP
* Discount %
* Ratings & Reviews
* Prime Eligibility
* Bought Last Month Demand Signal
* Scrape Timestamp

Additionally, a **5,000-row transactional sales dataset** was generated using the scraped product catalog to support business analysis and dashboard reporting.

---

## Tools & Technologies

* **Python** (Scrapy, Selenium, Pandas)
* **SQLAlchemy**
* **MySQL**
* **Power BI**
* **DAX**

---

## Project Workflow

### 1. Data Collection

* Built a Scrapy-based web scraping framework for Amazon products.
* Implemented custom middleware for User-Agent rotation and anti-block handling.
* Used Selenium as a fallback for JavaScript-rendered pages.
* Exported cleaned product data to CSV format.

### 2. Data Storage & SQL Analysis

* Loaded cleaned data into MySQL using SQLAlchemy.
* Generated transactional sales data for business reporting.
* Performed advanced SQL analysis using:

  * CTEs
  * Window Functions (RANK, LAG, Running Totals)
  * Customer Segmentation
  * Profitability Analysis
  * Revenue Trend Analysis

### 3. Business Intelligence Dashboard

* Built a star-schema data model in Power BI.
* Created DAX measures for:

  * Total Sales
  * Total Profit
  * Profit Margin %
  * Year-over-Year Growth
  * Customer Segmentation
  * Loss-Making Orders

---

## Dashboard Highlights

### Executive Summary

* Total Sales
* Total Profit
* Profit Margin %
* Order Volume
* Sales vs Profit Trend
* Geographic Sales Distribution
* Customer Segment Analysis

### Profitability Analysis

* Profit by City
* Profit by Category
* Decomposition Tree Analysis
* Category & Sub-Category Performance

---

## Key Results

* **Technology** generated the highest revenue, contributing nearly 80% of total sales.
* **Computers** emerged as the top-performing sub-category.
* Discounts above **20%** consistently reduced profitability across categories.
* **Seattle, Austin, and New York** were the most profitable cities.
* Corporate customers showed higher average order values despite similar revenue contribution across segments.
* Wearables and Audio products displayed stronger demand signals compared to Furniture products.

---

## Skills Demonstrated

* Web Scraping & Data Extraction
* Data Cleaning & ETL Pipelines
* SQL Analytics & Window Functions
* Database Design & Data Modeling
* Power BI Dashboard Development
* DAX & Time Intelligence
* Business Performance Analysis
* Data-Driven Decision Making

---

## Project Outcome

This project showcases an end-to-end Business Intelligence workflow, transforming raw web data into decision-ready insights through modern data engineering, SQL analytics, and Power BI reporting.
