# Financial Data Analytics in Python

**Eric Bühler**<br>
223 102 897<br>
eric.buehler@student.uni-halle.de<br>



# Case Study: Student Housing in Aachen

### Literature Review

To get an initial overview of the usual indicators of rent, I conducted some research on financial literature, namely **Estimating the value of Urban Green Space: A hedonic pricing analysis of the housing market in Cologne, Germany** by Kolbe and Wüstemann and **Hedonic pricing analysis of the influence of urban green spaces on residential prices: the case of Leipzig, Germany** by Liebelt, Bartke, & Schwarz.

Both papers showed that so-called *Urban Green Spaces* have a positive effect on housing prices, i.e., the more parks in the vicinity, the more expensive the apartment will be. This is, in my opinion, good grounds for investigating this effect on WG-Gesucht: Is there a correlation between urban green spaces per postal codes and rent per $m^2$? This was done to rectify the direct collinearity between size and price (since bigger rooms are usually more expensive by default).

Consulting the hints for a successful listing provided by WG-Gesucht themselves, they recommend writing a friendly text. I, therefore, plan to investigate the effect the sentiment of the written parts of the listing has on the listing duration. For a listing to be "effective" in this case, it should be taken down, i.e., "sold" as quickly as possible. We are, therefore, looking for a negative correlation between sentiment and listing duration.

Additionally, I intend to investigate the popularity of fraternities since Aachen has a surprisingly high number of them. In my experience, such fraternities are usually not looked upon kindly, such that I hypothesize that being a fraternity has a positive correlation with listing duration.

## Data Extraction

### Flat Data

To extract useful data from WG-Gesucht, I used the URL of a simple search query for shared apartments in Aachen to extract the links for the single listing of the search results pages. This step happens in the `get_wg_links` function in the [scraper.py](./scraper.py) file.

After the links are extracted, `get_anzeigen_html` extracts the HTML of the listings with the help of the ScraperAPI to bypass the anti-scraping measures of wg-gesucht.de. Since this process takes a significant amount of time, these HTML files are preserved in the [html_pages.json](./data_analysis/html_pages.json) for later analysis.

The final data-preprocessing step happens in the `get_anzeigen_from_html` function, where the desired data is extracted from the respective HTML locators and saved in the [anzeigen.csv](./data_analysis/anzeigen.csv) file.

I decided to use the first 20 pages for my analysis, amounting to 243 observations. While most of the data points are fairly self-explanatory, I will go into more detail on two more sophisticated data points:

**Sentiment:** To calculate one single numeric value for the sentiment of a listing, I extracted the strings from all possible free text fields and used `nltk.sentiment` to extract a vibe for all of them. In a second step, these single sentiments are further processed into a single sentiment score where $-1$ represents a negative sentiment, $0$ a neutral one, and $1$ a positive one. This will later allow easy application of the sentiments in the regression.

**Fraternities:** To determine this boolean variable, I very simply check whether the texts contain any synonyms of fraternity. It should be noted, however, that some obvious fraternities do not identify themselves as such. To alleviate this effect, I conducted a small search for such cases and concluded that these cases can be ignored. See **Analysis of Verbindung and Verbindung möglich variables** in [data_analysis_and_regression.ipynb](./data_analysis/data_analysis_and_regression.ipynb): Fraternities usually have low rent and a lot of flatmates, so I marked such listings and then compared these listings to ones that identify themselves as fraternities. Since this overlap was fairly low, I only used the "Verbindung" variable.

### UGS Data

To utilize Google Earth Engine for greenery data analysis, I used the API of [Rhein Kreis Neuss](https://opendata.rhein-kreis-neuss.de/pages/home/) to extract usable location data for every postal code, which they kindly provide for all of Germany.

To assess UGS, I used a function that calculates the [Normalized Difference Vegetation Index](https://de.wikipedia.org/wiki/Normalized_Difference_Vegetation_Index) of polygons by subtracting the B8 and B4 bands of the COPERNICUS/S2 satellite.

By inputting the postal code data as polygons into the NDVI function, I calculated the average NDVI of the year 2020 for every postal code in Aachen. See [urban_green_spaces.ipynb](./google_earth_engine/urban_green_spaces.ipynb) for more details on this process.

## Data Analysis and Interpretation

### Rent

For the analysis of the explanatory variables for rent, I decided to use the rent per square meter (i.e., divide rent by size), since an investigation of the effect the size of a room has on its rent is very much obsolete. As such, the explanatory variables we are left with are the number of people in the shared apartment and the postal code. First off, we find that an increase in the number of flatmates leads to a decrease in the rent per $m^2$, and only two districts have a positive effect on the rent: 52072 and 52074. These two districts also both have a fairly high NDVI.

### Duration

For this analysis, I decided to keep the rent as it is since people looking for a room in a WG usually will care more about the whole rent than the rent per $m^2$. This does, however, leave the problem of collinearity: Like mentioned above, size and rent are positively correlated ($r=0.31$), so including both variables in our regression will leave us with unstable estimation results. I, therefore, omitted size from this regression, which left the independent variables of flatmates, rent, sentiment, postal code, and connection.

Since online_since is measured in hours since the point in time when the listing was uploaded, a positive effect in this regression means a longer duration. First and foremost, cheaper flats tend to be online shorter and, interestingly, rooms with more flatmates tend to be rented out quicker. Additionally, wg-gesucht.de themselves stand corrected: sentiment is negatively correlated with online_since, meaning that the friendlier the texts in the listings are, the quicker the room will be rented out.

We can also detect that the increase in rent of 52072 and 52074 does not make these districts necessarily less desired since they still have a negative effect on online_since. Interestingly, fraternities do not seem to be less popular since the verbindung_True variable also has a negative effect on online_since. It is also striking that districts with very little green space are not necessarily online for longer.

### NDVI

To get a clearer picture of the numerical, direct effect the NDVI has on the duration and rent, I calculated two additional regressions where I used the NDVI as an explanatory variable instead of the postal code. Here we can see that UGS do make apartments more expensive and that apartments that are online for longer have a higher NDVI. It should be very much noted, however, that the calculation of the NDVI is based on postal codes.

## Automation

In this context, collecting data from wg-gesucht.de over one year will likely leave us with more robust information, since the data we got from one single scraping process is a comparatively small amount. Additionally, information about the listing duration extracted at a single point in time is only questionably applicable. One reason for this is that rented-out apartments do not necessarily get taken down from the site since there is also a function to mark rooms as "rented out".

To realize this, a data model could be used via Django with the page deployed on PythonAnywhere so that the `scraper.py` file will be executed (for example) hourly. With some alterations to the code (deleting listings that are scraped two times, some method to calculate the time the listing is online), this data could then be added to a database. The root page could, for example, be the search results page from which the data is scraped.

Since we would in this case scrape and keep private data about apartments people without informing them, this process comes with some ethical caveats, however. The `robots.txt` file of wg-gesucht.de also does not necessarily spell out openness to its data getting used. In the process of working on this case study, I also had to use ways to circumvent their anti-data-scraping measures. However, the users do voluntarily provide wg-gesucht.de with this data.

## Shortcomings of this Study

Like already mentioned in the section above, one major flaw of this research is the data on listing duration. Additionally, the amount of data is a little thin. In my opinion, wg-gesucht does also not really provide a good database for research of apartment prices. The prime customer base of wg-gesucht is students looking for shared flats, where the price will usually be at the lower end. For this task, similar studies for sites like [ImmoScout24](https://www.immobilienscout24.de) would probably allow for more robust insights.

Another shortcoming of this case in particular is the application of the NDVI I conducted: While it did work considerably well for this case, the pipeline from the satellite images to applicable economical insight severely lacks polish; in major cities postal codes also do not perfectly represent the vicinity of an apartment. Consider an apartment that has a big green space across the street, the street in question however also acts as the border of two postal codes; cases like this are not considered in this study.

## Conclusion and Outlook

While I would personally not consult wg-gesucht.de to assess the price of an apartment I want to rent out, I do think this study provided a number of interesting insights: I was able to at least partly recreate the findings about UGS of the two papers. One especially interesting conclusion is the effect the sentiment has on the listing duration.

In my opinion, this study is a good proof of concept for investigations like this: With little alteration, a large amount of data could also be attained for additional cities and additional sites like ImmoScout. The pipeline from postal code data to Google Earth Engine calculations could also be improved and expanded upon.
