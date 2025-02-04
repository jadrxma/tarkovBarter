import streamlit as st
import requests
import pandas as pd

# API Base URL
TARKOV_API_URL = "https://api.tarkov.dev/graphql"

# GraphQL Query to Get Barters and Flea Prices
BARTER_QUERY = """
query {
  barters {
    trader {
      name
    }
    requiredItems {
      item {
        name
        sellFor {
          priceRUB
          source
        }
      }
      count
    }
    rewardItems {
      item {
        name
        sellFor {
          priceRUB
          source
        }
      }
      count
    }
  }
}
"""

def fetch_barters():
    response = requests.post(TARKOV_API_URL, json={'query': BARTER_QUERY})
    if response.status_code == 200:
        return response.json().get("data", {}).get("barters", [])
    return []

def extract_flea_price(item):
    flea_price = "N/A"
    if "sellFor" in item and item["sellFor"]:
        for price in item["sellFor"]:
            if price.get("source") == "fleaMarket":  # Ensure correct key match
                flea_price = price.get("priceRUB", "N/A")
                break
    return flea_price

def calculate_profit(required_items, reward_items):
    total_cost = sum(float(extract_flea_price(item["item"])) * item["count"] for item in required_items if extract_flea_price(item["item"]) != "N/A")
    total_value = sum(float(extract_flea_price(item["item"])) * item["count"] for item in reward_items if extract_flea_price(item["item"]) != "N/A")
    return total_value - total_cost if total_cost and total_value else "N/A"

def main():
    st.title("Tarkov Barter Profit Finder")
    
    if st.button("Fetch Barters"): 
        with st.spinner("Fetching barter data..."):
            barters = fetch_barters()
            if barters:
                results = []
                for barter in barters:
                    trader_name = barter["trader"]["name"]
                    required_items = barter["requiredItems"]
                    reward_items = barter["rewardItems"]
                    profit = calculate_profit(required_items, reward_items)
                    
                    required_items_str = ", ".join(f"{item['count']}x {item['item']['name']} (Flea: {extract_flea_price(item['item'])} RUB)" for item in required_items)
                    reward_items_str = ", ".join(f"{item['count']}x {item['item']['name']} (Flea: {extract_flea_price(item['item'])} RUB)" for item in reward_items)
                    
                    results.append([trader_name, required_items_str, reward_items_str, profit])
                
                df = pd.DataFrame(results, columns=["Trader", "Required Items", "Reward Items", "Profit (RUB)"])
                st.dataframe(df)
            else:
                st.warning("No barter items found.")

if __name__ == "__main__":
    main()
