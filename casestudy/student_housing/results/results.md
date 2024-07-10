# Financial Data Analytics in Python

**Eric Bühler**<br>
223 102 897<br>
eric.buehler@student.uni-halle.de<br>



## Case study: Student Housing in Aachen
### Literature review ###
To get an initial overview over the usual indicators of rent aswell, I conducted some research of financial literature, namely **Estimating the value of Urban Green Space: A hedonic pricing analysis of the housing market in Cologne, Germany**. by Kolbe and Wüstemann and **Hedonic pricing analysis of the influence of urban green spaces onto residential prices: the case of Leipzig, Germany** by Liebelt, Bartke & Schwarz

Both of the papers were able to show that so called *Urban Green Spaces* have a positive effect on the housing prices, i.e. the more pars in the vicinity, the more expensive the apartement will be. This is, in my opinion, good grounds for an investigation into this effect on WG-Gesucht: Is there a correlation between urban green spaces per postal codes and rent per $m^2$? This was done to rectify the direct colinearity between grosse and price (since bigger rooms are usually more expensive by default).

Consulting the hints for a succesfull listing provided by WG-Gesucht themselves, they recommend writing a friendly text. I therefore plan to investigate the effect the sentiment of the written parts of the listing have on the listing duration. For a listing to be "effective" in this case, it should be taken down, i.e. "sold" as quickly as possible. We are therefore looking for a negative correlation between sentiment and listing duration.

Additionally, I intend to investigate the popularity of fraternities, since Aachen has a surprisingly high amount of them. In my experience, such fraternities are usually not looked upon kindly, such that I hypothesize that being a fraternity has a positive correlation with listing duration.

## Data Extraction
### Flat Data
To extract usefull data from WG-gesucht, I used the URL of a simple search query for shared apartements in Aachen, to extract the links for the single listing of the search results pages. This step happens in the get_wg_links function in [scraper.py](/workspaces/fdap-2024-Big-Eric-Blip/casestudy/student_housing/scraper.py) file.

After the links are extracted, get_anzeigen_html extracts the html of the listings with the help of the ScraperAPI to bypass the anti-scraping measures of wg-gesucht.de. Since this process takes a big amount of time, these HTML files are preserved in the [html_pages.json](/workspaces/fdap-2024-Big-Eric-Blip/casestudy/student_housing/data_analysis/html_pages.json) for later analysis.

The final data-preprocessing step happens in the get_anzeigen_from_html function, where the desired data is extracted from the respective HTML locators and saves the data in the [anzeigen.csv](/workspaces/fdap-2024-Big-Eric-Blip/casestudy/student_housing/data_analysis/anzeigen.csv) file. 

While most of the datapoints are fairly self-explanatory, I will go into more detail on two more sophisticated datapoints:

**sentiment:** To calculate one single numeric value for the sentiment of a listing, I extraced the strings from all possible free text fields and used nltk.sentiment to extract a vibe for all of them. In a second step, these single sentiments are further processed into a single sentiment score where $-1$ represents a negative sentiment, $0$ a neutral- and $1$ a positive one. This will later allow easy application of the sentiments in the regression.

**fraternities:** To determine this boolean variable, I very simply check wether the texts contain any synonyms of fraternity. It should be noted however, that some obvious fraternities do not identifiy themselves as such. To alleviate this effect, I conducted a small search for such cases and concluded that these cases can be ignored. See **Analysis of Verbindung and Verbindung möglich variables** in [data_analysis_and_regression.ipynb](/workspaces/fdap-2024-Big-Eric-Blip/casestudy/student_housing/data_analysis/data_analysis_and_regression.ipynb): Fraternities usually have low rent and a lot of flatmates, so that I marked such listings and then compared these listings to ones that identify themselves as fraternities. Since this overlap was fairly low, I only used the "Verbindung" Variable.

### UGS Data
To utilize Google Earth Engine for greenery-data analysis, I used the API of [Rhein Kreis Neuss](https://opendata.rhein-kreis-neuss.de/pages/home/) to extract usable location data for every plz, which they kindly provide for all of Germany.

To assess UGS, I used a function that calculates the [Normalized Difference Vegetation Index](https://de.wikipedia.org/wiki/Normalized_Difference_Vegetation_Index) of polygons by subtracting the B8 and B4 bands of the COPERNICUS/S2 satellite.

By inputing the PLZ data as Polygons into the NDVI function, I calculated the average NDVI of the year 2020 of every PLZ in Aachen. See [urban_green_spaces.ipynb](/workspaces/fdap-2024-Big-Eric-Blip/casestudy/student_housing/google_earth_engine/urban_green_spaces.ipynb) for more details on this process.

## Data Analysis and Interpretation
### Rent

### Duration
## Automation