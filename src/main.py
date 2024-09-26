from src.scraping_ins import get_region_code
from src.scraping_ins import fetch_trending


def main():
    user_input = input("Country name：")
    user_input2 = input("interest: ")
    user_input3 = input('base on most populor trend or base on personel interest')
    country_list = [country.strip() for country in user_input.split(',')]
    interest_list = 

    regions = []
    for country in country_list:
        region_code = get_region_code(country)
        if region_code:
            regions.append(region_code)
        else:
            print(f"no such country{country}")

    if regions:
        try:
            fetch_trending(regions)
        except Exception as e:
            print(f"error: {e}")
    else:
        print("error")

if __name__ == "__main__":
    main()