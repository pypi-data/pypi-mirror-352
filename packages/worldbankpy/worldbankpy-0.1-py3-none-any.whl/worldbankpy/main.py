import datetime as dt
import requests
import pandas as pd

from .utils import *
from .const import *


class Instance:
    """
    Interface for retrieving and filtering World Bank indicators and country metadata.

    Attributes:
        __current_year__ (int): Current calendar year.
        indicators (list[dict]): List of indicator metadata records.
        countries (list[dict]): List of country metadata records.
        countries_mapping (dict): Mapping from country name to country code.
        indicators_mapping (dict): Mapping from indicator category to {indicator name: code}.
        list_available_categories (list[str]): All top-level indicator categories.
        list_available_countries (list[str]): All available country names.
        list_popular_indicators (list[str]): Predefined list of popular indicator codes.
        list_regions (list[str]): Unique region names present in country metadata.
        list_admin_regions (list[str]): Unique administrative region names.
        list_income_levels (list[str]): Unique income level labels.
        list_lending_types (list[str]): Unique lending type labels.
        list_topics (list[str]): Unique indicator topics.
        list_sources (list[str]): Unique data source names.
    """

    def __init__(self):
        """
        Initialize the Instance instance by loading and mapping indicators and countries.

        Builds DataFrames for indicators and countries, converts them to record dictionaries,
        constructs lookup mappings, and populates lists of unique regions, income levels, topics, etc.
        """
        self.__current_year__ = dt.date.today().year
        self.indicators = build_indicators_df().to_dict("records")
        self.countries = build_countries_df().to_dict("records")

        self.countries_mapping = build_countries_mapping(self.countries)
        self.indicators_mapping = build_indicators_mapping(self.indicators)

        self.list_available_categories = list(self.indicators_mapping.keys())
        self.list_available_countries = list(self.countries_mapping.keys())
        self.list_popular_indicators = POPULAR_INDICATOR_LIST

        self.list_regions = []
        self.list_admin_regions = []
        self.list_income_levels = []
        self.list_lending_types = []
        self.list_topics = []
        self.list_sources = []

        # Populate unique region, admin region, income level, and lending type lists
        for x in self.countries:
            if x["region"] is not None:
                value = x["region"].get("value", None)
                if value:
                    value = value.strip()
                    if value not in self.list_regions:
                        self.list_regions.append(value)

            if x["adminregion"] is not None:
                value = x["adminregion"].get("value", None)
                if value:
                    value = value.strip()
                    if value not in self.list_admin_regions:
                        self.list_admin_regions.append(value)

            if x["incomeLevel"] is not None:
                value = x["incomeLevel"].get("value", None)
                if value:
                    value = value.strip()
                    if value not in self.list_income_levels:
                        self.list_income_levels.append(value)

            if x["lendingType"] is not None:
                value = x["lendingType"].get("value", None)
                if value:
                    value = value.strip()
                    if value not in self.list_lending_types:
                        self.list_lending_types.append(value)

        # Populate unique topics and sources from indicator metadata
        for indicator in self.indicators:
            try:
                topic = indicator["topics"][0].get("value", None)
                if topic:
                    topic = topic.strip()
                    if topic not in self.list_topics:
                        self.list_topics.append(topic)
            except (IndexError, KeyError):
                pass

            try:
                source = indicator["source"].get("value", None)
                if source:
                    source = source.strip()
                    if source not in self.list_sources:
                        self.list_sources.append(source)
            except (KeyError, TypeError):
                pass

    def filtered_countries(
        self,
        admin_region=None,
        region=None,
        income_level=None,
        lending_type=None,
        list_format: bool = False,
    ):
        """
        Return countries filtered by administrative region, region, income level, or lending type.

        Args:
            admin_region (str, optional): Name of the administrative region to filter by.
            region (str, optional): Name of the region to filter by.
            income_level (str, optional): Income level label to filter by.
            lending_type (str, optional): Lending type label to filter by.
            list_format (bool): If True, return a list of country codes; otherwise return a name-to-code mapping.

        Raises:
            ValueError: If any provided filter value is not in the corresponding list of valid options.

        Returns:
            dict or list[str]: Mapping from country name to code, or list of country codes if list_format is True.
        """
        if (
            admin_region is not None
            and admin_region not in self.list_admin_regions
        ):
            raise ValueError(
                f"admin_region {admin_region} must be in {self.list_admin_regions}"
            )
        if region is not None and region not in self.list_regions:
            raise ValueError(f"region {region} must be in {self.list_regions}")
        if (
            income_level is not None
            and income_level not in self.list_income_levels
        ):
            raise ValueError(
                f"income_level {income_level} must be in {self.list_income_levels}"
            )
        if (
            lending_type is not None
            and lending_type not in self.list_lending_types
        ):
            raise ValueError(
                f"lending_type {lending_type} must be in {self.list_lending_types}"
            )

        filtered_countries = []
        for country in self.countries:
            if (
                admin_region
                and country["adminregion"]["value"].strip() != admin_region
            ):
                continue
            if region and country["region"]["value"].strip() != region:
                continue
            if (
                income_level
                and country["incomeLevel"]["value"].strip() != income_level
            ):
                continue
            if (
                lending_type
                and country["lendingType"]["value"].strip() != lending_type
            ):
                continue
            filtered_countries.append(country)

        queried = build_countries_mapping(filtered_countries)
        if list_format:
            return list(queried.values())
        return queried

    def filtered_indicators(self, topic=None, source=None):
        """
        Return indicators filtered by topic or data source.

        Args:
            topic (str, optional): Topic label to filter indicators by.
            source (str, optional): Source label to filter indicators by.

        Raises:
            ValueError: If provided topic or source is not in the list of valid options.

        Returns:
            dict: Mapping from indicator name to indicator code within each category.
        """
        if topic is not None and topic not in self.list_topics:
            raise ValueError(f"topic {topic} must be in {self.list_topics}")
        if source is not None and source not in self.list_sources:
            raise ValueError(f"source {source} must be in {self.list_sources}")

        filtered_indicators = []
        for indicator in self.indicators:
            try:
                if topic and indicator["topics"][0]["value"].strip() != topic:
                    continue
            except (IndexError, KeyError):
                if topic:
                    continue
            try:
                if source and indicator["source"]["value"].strip() != source:
                    continue
            except (KeyError, TypeError):
                if source:
                    continue
            filtered_indicators.append(indicator)

        return build_indicators_mapping(filtered_indicators)

    def country_code(self, country_name):
        """
        Get the ISO country code for a given country name.

        Args:
            country_name (str): Official country name.

        Returns:
            str or None: Corresponding country code, or None if not found.
        """
        return self.countries_mapping.get(country_name)

    def category_indicators(self, category):
        """
        Get all indicators under a given category.

        Args:
            category (str): Category name.

        Returns:
            dict or None: Mapping from indicator name to code for the category, or None if category not found.
        """
        return self.indicators_mapping.get(category)

    def search_indicator_by_keywords(self, keywords: list[str]):
        """
        Search for indicators that match all of the provided keywords.

        Args:
            keywords (list[str]): List of keywords to search for in indicator names.

        Returns:
            list[dict]: List of dictionaries containing matching indicators with their name and code.
        """
        if not isinstance(keywords, list):
            raise ValueError("keywords must be a list of strings")

        matching_indicators = []
        for category, indicators in self.indicators_mapping.items():
            for name, code in indicators.items():
                if all(keyword.lower() in name.lower() for keyword in keywords):
                    matching_indicators.append({"name": name, "code": code})

        return matching_indicators

    def get_indicator_code(self, indicator_name):
        """
        Retrieve the code for a given indicator name.

        Args:
            indicator_name (str): Full name of the indicator.

        Returns:
            str or None: Indicator code if found, otherwise None.
        """
        for category in self.indicators_mapping:
            if indicator_name in self.indicators_mapping[category]:
                return self.indicators_mapping[category][indicator_name]
        return None

    def get_indicator_name(self, indicator_code):
        """
        Retrieve the name for a given indicator code.

        Args:
            indicator_code (str): Code of the indicator.

        Returns:
            str or None: Indicator name if found, otherwise None.
        """
        for category, indicators in self.indicators_mapping.items():
            for name, code in indicators.items():
                if code == indicator_code:
                    return name
        return None

    def _indicator(self, country_code, indicator_code):
        """
        Fetch time series data for a single country and indicator from the World Bank API.

        Args:
            country_code (str): ISO code of the country.
            indicator_code (str): Code of the indicator.

        Returns:
            pd.DataFrame: Time-indexed DataFrame containing columns for Country Code, Indicator, Indicator Code, Value, Unit, and Last Updated.
        """
        indicator_data_url = (
            f"https://api.worldbank.org/v2/country/{country_code}/indicator/"
            f"{indicator_code}?date=1930:{self.__current_year__}&per_page=10000&format=json"
        )
        json_indicator_data = requests.get(indicator_data_url).json()

        last_updated = json_indicator_data[0].get("lastupdated", None)
        indicator_data = json_indicator_data[1]

        country_ret = json_indicator_data[1][0]["country"]["value"]
        country_code_ret = json_indicator_data[1][0]["country"]["id"]
        indicator_ret = json_indicator_data[1][0]["indicator"]["value"]
        indicator_code_ret = json_indicator_data[1][0]["indicator"]["id"]
        unit_ret = json_indicator_data[1][0]["unit"]
        last_updated_ret = json_indicator_data[0].get("lastupdated", None)

        cleaned_indicator_data = []
        for data_dict in indicator_data:
            clean_dict = {
                "Date": pd.to_datetime(data_dict["date"]),
                f"{country_code}": (
                    float(data_dict["value"])
                    if data_dict["value"] is not None
                    else None
                ),
            }
            cleaned_indicator_data.append(clean_dict)

        dataframe = pd.DataFrame(cleaned_indicator_data).set_index("Date")
        dataframe.attrs["Country Code"] = country_code
        dataframe.attrs["Country"] = country_ret
        dataframe.attrs["Indicator"] = indicator_ret
        dataframe.attrs["Indicator Code"] = indicator_code_ret
        dataframe.attrs["Unit"] = unit_ret
        dataframe.attrs["Last Updated"] = last_updated_ret
        dataframe.attrs["Source"] = "World Bank"
        dataframe.attrs["Source URL"] = indicator_data_url

        return dataframe.sort_index(ascending=True)

    def indicator(self, country_codes, indicator_code):
        """
        Fetch and combine time series data for multiple countries and a single indicator.

        Args:
            country_codes (str or list[str]): One or more ISO country codes.
            indicator_code (str): Code of the indicator to retrieve.

        Returns:
            pd.DataFrame: DataFrame combining data from all specified countries,
                              avec une colonne par code pays, et attrs mis à jour.
        """
        if isinstance(country_codes, str):
            country_codes = [country_codes]

        if not isinstance(country_codes, list):
            raise ValueError(
                "country_codes must be a string or a list of strings"
            )

        dataframes = []
        countries = []
        last_updated_list = []
        source_urls = []

        for country_code in country_codes:
            try:
                df = self._indicator(country_code, indicator_code)
                dataframes.append(df)

                countries.append(df.attrs.get("Country"))
                last_updated_list.append(df.attrs.get("Last Updated"))
                source_urls.append(df.attrs.get("Source URL"))

            except Exception as e:
                print(
                    f"Failed to retrieve data for {country_code} with indicator {indicator_code}: {e}"
                )

        if not dataframes:
            raise ValueError(
                f"Aucune donnée récupérée pour l'indicateur {indicator_code}."
            )

        combined_df = pd.concat(dataframes, axis=1)

        combined_df.attrs["Country Codes"] = country_codes
        combined_df.attrs["Countries"] = countries

        first_df = dataframes[0]
        combined_df.attrs["Indicator"] = first_df.attrs.get("Indicator")
        combined_df.attrs["Indicator Code"] = first_df.attrs.get(
            "Indicator Code"
        )
        combined_df.attrs["Unit"] = first_df.attrs.get("Unit")

        try:
            timestamps = [
                pd.to_datetime(d) for d in last_updated_list if d is not None
            ]
            combined_df.attrs["Last Updated"] = max(timestamps).strftime(
                "%Y-%m-%d"
            )
        except Exception:
            combined_df.attrs["Last Updated"] = last_updated_list
        combined_df.attrs["Source"] = first_df.attrs.get("Source")
        combined_df.attrs["Source URLs"] = source_urls

        combined_df = combined_df.sort_index(ascending=True).dropna(
            axis=1, how="all"
        )
        combined_df = combined_df.dropna(axis=0, how="all")
        if combined_df.empty:
            raise ValueError(
                f"No data available for indicator {indicator_code} in the specified countries."
            )

        return combined_df
