import requests
import math
import json
from enum import Enum

class CATEGORY(Enum):
    RESTAURANT = 1
    RETAIL = 2
    HOTEL = 3
    ACTIVITY = 4

class APIHandling:
    def __init__(self, _url, _checkin_date):
        self.checkin_date = ""
        self.offers = []

        response = requests.get(_url)
        assert self._validate_input(response, _checkin_date) == True
        
        # Inputs are validated!
        self.offers = self._receive_offers(response)
        self.checkin_date = _checkin_date

        return
    
    def __str__(self):
        return "Methods: \n \
                1. category_filter \n \
                2. date_filter \n \
                3. closest_merchant_per_category_filter \n \
                4. merchant_filter \n \
                5. top_two_offers_filter \n \
                6. get_offers"
    
    # Helper functions
    
    def _is_valid_response(self, response):
        """
        Input: a HTTP response
        Return: True if we can access the web, False otherwise
        """
        if not response.status_code == 200:
            print(f"Please fix your URL: error code {response.status_code}")
        return True
    
    def _validate_input(self, response, _checkin_date):
        """
        Input:
        1. 'response' - a HTTP response
        2. '_checkin_date' - a string representing a guest's checkin date
        Return: True if all inputs are valid, False otherwise
        """
        return self._is_valid_response(response) and self._is_valid_date(_checkin_date, False)
    
    def _receive_offers(self, response):
        """
        Input: a HTTP response
        Return: a list of all JSON-formatted offers
        """
        KEYWORD = "offers"
        response_json = response.json()
        
        assert KEYWORD in response_json
        
        return response_json[KEYWORD]
    
    def _standardize_category_names(self, category_names):
        """
        Input: a list of names of categories we want to filter
        Return: the similar list except all names are uppercase.
        """
        return [category.upper() for category in category_names]
    
    def _get_category_enum(self, category_id):
        """
        Input: an integer representing a category ID
        Return: a category name based on the CATEGORY enum class,
        assuming the id is valid
        """
        assert category_id in [category_enum.value for category_enum in CATEGORY]

        return CATEGORY(category_id).name        
    
    def _get_category_offers_map(self):
        """
        Return: a map of (category_name -> a list of offers)
        """
        KEYWORD = 'category'
        ategory_offers_map = {}
        
        for offer in self.offers:
            assert KEYWORD in offer
            
            category_id = offer[KEYWORD]
            category_name = self._get_category_enum(category_id)
            
            if category_name not in ategory_offers_map:
                ategory_offers_map[category_name] = []
            ategory_offers_map[category_name].append(offer)
            
        return ategory_offers_map        
            
    def _get_year_month_day_from_str(self, cur_date_str):
        """
        Input: a date in string format.
        Return: a tuple of that date's year, month, and day, in respective order.
        """
        cur_dates = cur_date_str.split("-")
        cur_year_str, cur_month_str, cur_day_str = cur_dates[0], cur_dates[1], cur_dates[2]
        
        if len(cur_dates[1]) == 4:
            cur_year_str = cur_dates[1]
            cur_month_str = cur_dates[0]
            cur_day_str = cur_dates[2]
        if len(cur_dates[2]) == 4:
            cur_year_str = cur_dates[2]
            cur_month_str = cur_dates[0]
            cur_day_str = cur_dates[1]
        
        cur_year, cur_month, cur_day = int(cur_year_str), int(cur_month_str), int(cur_day_str)
        
        return (cur_year, cur_month, cur_day)
    
    def is_leap_year(self, year):
        """
        Input: an integer representing a year
        Return: True if that year is a leap year, False otherwise
        """
        return year % 4 == 0
    
    def _get_no_days_in(self, year, month):
        """
        Input:
        1. 'year' - an integer representing a year
        2. 'month' - an integer representing a month
        Return:
        - An integer representing the number of days in a month of a year
        """
        assert 1 <= month <= 12
        
        if month == 2:
            return 29 if self.is_leap_year(year) else 28
        return 30 if month in [4, 6, 9, 11] else 31        
        
    def _is_valid_date(self, date_str, is_testing = True):
        """
        Input:
        1. 'date_str' -- a string formatted date
        2. 'is_testing' -- True if we are in testing mode, 
        False if we're in production mode
        
        Return:
        True if the input string date is valid, False otherwise.
        """
        
        if date_str == "":
            return False
        
        for char in date_str:
            if not ('0' <= char <= '9' or char == '-'):
                return False
        
        year, month, day = self._get_year_month_day_from_str(date_str)
        
        JANUARY = 1
        DECEMBER = 12
        is_valid_month = (JANUARY <= month <= DECEMBER)
        if not is_valid_month:
            if not is_testing:
                print(f"{year, month, day} has Invalid MONTH. Please re-enter date in format month-day-year")
            return False
        
        FIRST_DAY = 1
        LAST_DAY = self._get_no_days_in(year, month)
        is_valid_day = (FIRST_DAY <= day <= LAST_DAY)
        if not is_valid_day:
            if not is_testing:
                print(f"{year, month, day} has Invalid DAY. Please re-enter date in format month-day-year")
            return False

        return True

    def _get_last_stay_date(self, date_str, no_extended_days):
        """
        Input:
        1. 'date_str' -- a string formatted date
        2. 'no_extended_days' -- an integer representing number of days
        from the string formatted date.
        Return:
        A tuple of (year, month, day) if the day after 'no_extended_days'.
        
        Note: Works only when 'no_extended_days' <= 31, getting a date after 
        n > 1 months is a bit complicated.
        """
        assert self._is_valid_date(date_str) == True
        
        if no_extended_days > 31:
            print(f"This function only works for 'no_extended_days' <= 31")
            return (-1, -1, -1)
        
        (cur_year, cur_month, cur_day) = self._get_year_month_day_from_str(date_str)
        
        no_days_in_cur_month = self._get_no_days_in(cur_year, cur_month)
        new_year, new_month, new_day = (cur_year, cur_month, cur_day)
        
        if cur_day + no_extended_days > no_days_in_cur_month:
            new_month = cur_month + 1
            
            if new_month > 12:
                new_year += 1
                new_month = 1

            new_day = cur_day + no_extended_days - no_days_in_cur_month

        else:
            new_day = cur_day + no_extended_days
            
        return (new_year, new_month, new_day)
    
    def _is_expired(self, valid_to_date_str, no_extended_days, checkin_date = ""):
        """
        Input:
        1. 'valid_to_date_str' -- a string formatted expiring date
        2. 'no_extended_days' -- an integer representing number of days
        from the string formatted date.
        3. 'checkin_date' -- a string formatted checkin date
        Return:
        True if the checkin date has not passed the expiring date, False otherwise.
        """
        if checkin_date == "":
            checkin_date = self.checkin_date
        
        staying_dates = self._get_last_stay_date(self.checkin_date, no_extended_days)
        cur_year, cur_month, cur_day = staying_dates[0], staying_dates[1], staying_dates[2]
        
        expiry_year, expiry_month, expiry_day = self._get_year_month_day_from_str(valid_to_date_str)
        
        if cur_year > expiry_year:
            return True
        
        elif cur_year == expiry_year:
            if cur_month > expiry_month:
                return True
            
            elif cur_month == expiry_month:
                if cur_day > expiry_day:
                    return True
                
                return False
            
        else:
            return False
    
    def _get_offer_merchants(self, offer):
        """
        Input: a JSON formatted offer
        Return: a list of merchants associated with the input offer.
        """
        assert 'merchants' in offer
        
        return offer['merchants']
    
    def _get_offer_id(self, offer):
        """
        Input: a JSON formatted offer
        Return: the id of the input offer.
        """        
        assert 'id' in offer
        
        return offer['id']
    
    def _get_closest_merchant_offer(self, seen_offers_set):
        """
        Input: a set of offers seen
        Return: the offer having the nearest merchant
        
        Note: runtime O(n)
        """
        min_merchant_dist = math.inf
        closest_merchant_offer = None
        
        for offer in self.offers:
            offer_id = self._get_offer_id(offer)
            
            if offer_id not in seen_offers_set:
                cur_merchant = self._get_offer_merchants(offer)
                
                assert 'distance' in cur_merchant

                cur_merchant_dist = cur_merchant['distance']
                if cur_merchant_dist < min_merchant_dist:
                    closest_merchant_offer = offer
                    min_merchant_dist = cur_merchant_dist
                    
        return closest_merchant_offer
    
    # \Helper functions
    
    # Helper Testing Functions
    def test_helper_functions(self):
        self.test_is_valid_date()
        self.test_get_last_stay_date()
    
    def test_is_valid_date(self):
        assert self._is_valid_date("") == False
        assert self._is_valid_date("abc-12-2023") == False
        assert self._is_valid_date("30-02-2024") == False
        assert self._is_valid_date("01-01-2023") == True
        assert self._is_valid_date("02-22-2023") == True
        
        assert self._is_valid_date("9-31-2024") == False
        assert self._is_valid_date("04-31-2024") == False
        assert self._is_valid_date("1-31-2023") == True
        assert self._is_valid_date("4-30-2023") == True
        
        assert self._is_valid_date("02-30-2024") == False
        assert self._is_valid_date("02-29-2023") == False
        assert self._is_valid_date("2-28-2023") == True
        assert self._is_valid_date("2-29-2024") == True
        
    def test_get_last_stay_date(self):
        assert self._get_last_stay_date("4-30-2023", 5) == (2023, 5, 5)
        assert self._get_last_stay_date("4-25-2023", 5) == (2023, 4, 30)
        assert self._get_last_stay_date("2-28-2023", 2) == (2023, 3, 2)
        
    # \Helper Testing Functions
    
    # Filter functions
            
    def category_filter(self, desired_categories):
        """
        Filter offers having specific categories
        
        Input: a list of desired categories we want to filter
        Return: None
        """
        category_names_set = self._standardize_category_names(desired_categories)
        
        categoryName_offers_map = self._get_category_offers_map()
        answers = []
    
        for category_name in category_names_set:
            answers.extend(categoryName_offers_map[category_name])
        
        self.offers = answers
        TestFilter.test_category_filter(self.offers)
        return
    
    def date_filter(self, no_extended_days):
        """
        Filter offers beeing still valid.
        
        Input: an integer of number of extended days after checkin date.
        Return: None
        """
        KEYWORD = "valid_to"
        answers = []
        
        for offer in self.offers:
            valid_to_date = offer[KEYWORD]
            if not self._is_expired(valid_to_date, no_extended_days):
                answers.append(offer)
        
        self.offers = answers
        TestFilter.test_date_filter(self.offers)
        return
    
    def merchant_filter(self):
        """
        Make all offers only have the closest merchant.
        
        Input: None
        Return: None
        
        Note: runtime O(nlogn)
        """
        for i, offer in enumerate(self.offers):
            if len(offer['merchants']) > 1:
                offer['merchants'].sort(key=lambda x:x['distance'])
            offer['merchants'] = offer['merchants'][0]
            
            self.offers[i] = offer
        
        TestFilter.test_merchant_filter(self.offers)
        return
    
    def closest_merchant_per_category_filter(self):
        """
        Filter the offer having the closest merchant per category
        Note: runtime O(nlogn)
        """
        categoryName_offer_map = self._get_category_offers_map()
        answers = []
        
        for categoryName, offers in categoryName_offer_map.items():
            offers.sort(key = lambda x:x['merchants']['distance'])
            answers.append(offers[0])
        
        self.offers = answers
        TestFilter.test_closest_merchant_per_category_filter(self.offers)
        return    
    
    def top_two_offers_filter(self):
        """
        Get two offers having different categories and the nearest merchants.
        
        Input: None
        Output: None
        
        Note: runtime O(2n) as we fix the number of offers we want.
        """
        seen_id_set = set()
        answers = []
        
        closest_merchant_offer = self._get_closest_merchant_offer(seen_id_set)
        
        if closest_merchant_offer:
            answers.append(closest_merchant_offer)
            seen_id_set.add(closest_merchant_offer['id'])
        
        second_closest_merchant_offer = self._get_closest_merchant_offer(seen_id_set)
        if second_closest_merchant_offer:
            answers.append(second_closest_merchant_offer)
            seen_id_set.add(closest_merchant_offer['id'])
        
        self.offers = answers
        TestFilter.test_top_two_offers_filter(self.offers)
        return
    
    # \Filter functions
    
    # Output functions
    def get_offers(self):
        """
        Get the final offers after all filters
        
        Return: a list of JSON formatted offers.
        """
        TestFilter.test_final_output(self.offers)
        return self.offers
    # \Output functions
    
class TestFilter:
    def write_to_file(offers, filename):
        outfile = open(f"{filename}.txt", 'w')
        outfile.writelines(json.dumps(offers, indent=4))
        outfile.close()    
    
    def test_category_filter(offers):
        file_name = "output_category_filter"
        TestFilter.write_to_file(offers, file_name)
        return
        
    def test_date_filter(offers):
        file_name = "output_date_filter"
        TestFilter.write_to_file(offers, file_name)
        return
        
    def test_merchant_filter(offers):
        file_name = "output_merchant_filter"
        TestFilter.write_to_file(offers, file_name)
        return
        
    def test_closest_merchant_per_category_filter(offers):
        file_name = "output_closest_merchant_per_category_filter"
        TestFilter.write_to_file(offers, file_name)
        return
        
    def test_top_two_offers_filter(offers):
        file_name = "output_top_two_offers_filter"
        TestFilter.write_to_file(offers, file_name)
        return
        
    def test_final_output(offers):
        file_name = "output_final"
        TestFilter.write_to_file(offers, file_name)
        return        


if __name__ == "__main__":
    LATITUDE = 1.313492
    LONGTIDUE = 103.860359
    RAD = 20
    
    DESIRED_CATEGORIES = ["Restaurant", "Retail", "Activity"]
    NO_EXTENDED_DAYS = 5

    URL = f"https://61c3deadf1af4a0017d990e7.mockapi.io/offers/near_by?lat={LATITUDE}&lon={LONGTIDUE}&rad={RAD}"
    
    checkin_year = input("Please input your checkin year: ")
    checkin_month = input("Please input your checkin month: ")
    checkin_day = input("Please input your checkin day: ")
    
    checkin_date = "-".join([checkin_year, checkin_month, checkin_day])

    api = APIHandling(URL, checkin_date)
    print(api)
    
    api.test_helper_functions()

    api.category_filter(DESIRED_CATEGORIES)
    api.date_filter(NO_EXTENDED_DAYS)
    api.merchant_filter()
    api.closest_merchant_per_category_filter()
    api.top_two_offers_filter()

    offers = api.get_offers()
    print(offers)