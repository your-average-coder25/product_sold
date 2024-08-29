## Table of contents

- [Description](#description)
- [Example](#example)
- [Potential updates](#potential_updates)

## Description

- The purpose of this script is to retrieve products sold between 2 date ranges in lightspeed's backoffice.
- This data can then be used to get exact product usage/costs.
- Lightspeed currently does not offer a way for their users to download the data from the popover from the products sold report.
- The goal was to use selenium and python to scrape the popover data fron the products sold report and output to a csv file. That way it is much easier for us to analyze trends of sales.

## Example

- From the image below products are grouped by their inventory category.
![Example of products report from backoffice](Images/Product_sold_example.png)
- Each category needs to be expanded before the relevant popover can be scraped.
- Each item has the number of times a specific modifier was chosen with that item.
![Example of products popover from backoffice](Images/Popover_Example.png)

## Potential updates
- Currently the output is everything between 2 dates. It could be useful to split the dates into multiple weeks that way the user can get an output of products sold across multiple weeks and can be easily analyzed. The user would no longer have to run the script multiple times to retrieve multiple weeks worth of data.
- The main data extrated is the number of regulars and larges that are ordered for each item. It might be a good idea to parse more of the popover data.