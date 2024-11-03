import json
from datetime import datetime


def parse_response(data):
    # Extract filters information
    filters = {
        "retailers": [
            {"id": retailer["id"], "name": retailer["name"], "resultsCount": retailer["resultsCount"]}
            for retailer in data["filters"]["retailers"]
        ],
        "brands": [
            {"id": brand["id"], "name": brand["name"], "resultsCount": brand["resultsCount"]}
            for brand in data["filters"]["brands"]
        ],
        "categories": [
            {"id": category["id"], "name": category["name"], "resultsCount": category["resultsCount"]}
            for category in data["filters"]["categories"]
        ]
    }

    # Process each product result
    results = []
    for result in data["results"]:
        item = {
            "id": result["id"],
            "brand": result["brand"]["name"],
            "advertiser": result["advertisers"][0]["name"],
            "category": result["categories"][0]["name"],
            "description": result["description"],
            "price": result["price"],
            "referencePrice": result.get("referencePrice"),
            "validityDates": [
                {
                    "from": datetime.fromisoformat(date_range["from"].replace("Z", "+00:00")),
                    "to": datetime.fromisoformat(date_range["to"].replace("Z", "+00:00"))
                }
                for date_range in result["validityDates"]
            ],
            "requiresLoyaltyMembership": result["requiresLoyalityMembership"],
            "product": result["product"]["name"],
            "unit": result["unit"]["name"],
        }
        results.append(item)

    # Structure parsed data
    parsed_data = {
        "filters": filters,
        "totalResults": data["totalResults"],
        "results": results
    }

    return parsed_data

