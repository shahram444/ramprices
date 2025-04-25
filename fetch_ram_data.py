import os, json, datetime, hashlib, hmac, requests
from config import *

def fetch_ram_data(region="us"):
    if USE_DUMMY_DATA:
        return [
            {
                "title": "Test DDR4 16GB",
                "image": "https://via.placeholder.com/150",
                "price": 39.99,
                "link": "#",
                "capacity_gb": 16,
                "type": "DDR4",
                "form_factor": "DIMM",
                "condition": "New",
                "price_per_gb": 2.5
            }
        ]

    REGION_MAP = {
        "us": ("www.amazon.com", "us-east-1"),
        "uk": ("www.amazon.co.uk", "eu-west-1"),
        "de": ("www.amazon.de", "eu-central-1"),
    }
    host, aws_region = REGION_MAP.get(region, REGION_MAP["us"])
    cache_path = f"cache/products_{region}.json"

    if os.path.exists(cache_path):
        modified = datetime.datetime.fromtimestamp(os.path.getmtime(cache_path))
        if datetime.datetime.now() - modified < datetime.timedelta(hours=CACHE_DURATION_HOURS):
            with open(cache_path, 'r') as f:
                return json.load(f)

    payload = {
        "Keywords": "DDR4 DDR5 RAM memory",
        "SearchIndex": "Electronics",
        "Resources": ["Images.Primary.Small", "ItemInfo.Title", "Offers.Listings.Price"],
        "PartnerTag": AMAZON_PARTNER_TAG,
        "PartnerType": "Associates",
        "Marketplace": host
    }

    amz_date = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    date_stamp = datetime.datetime.utcnow().strftime('%Y%m%d')
    uri = "/paapi5/searchitems"
    canonical_headers = f'content-type:application/json; charset=utf-8\nhost:{host}\nx-amz-date:{amz_date}\n'
    signed_headers = 'content-type;host;x-amz-date'
    payload_str = json.dumps(payload)
    payload_hash = hashlib.sha256(payload_str.encode('utf-8')).hexdigest()
    canonical_request = f"POST\n{uri}\n\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
    credential_scope = f"{date_stamp}/{aws_region}/execute-api/aws4_request"
    string_to_sign = f"AWS4-HMAC-SHA256\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"

    def sign(key, msg): return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()
    def get_signature_key(key, dateStamp, regionName, serviceName):
        kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
        kRegion = sign(kDate, regionName)
        kService = sign(kRegion, serviceName)
        return sign(kService, 'aws4_request')

    signing_key = get_signature_key(AMAZON_SECRET_KEY, date_stamp, aws_region, "execute-api")
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "X-Amz-Date": amz_date,
        "Authorization": f"AWS4-HMAC-SHA256 Credential={AMAZON_ACCESS_KEY}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
    }

    url = f"https://{host}{uri}"
    response = requests.post(url, headers=headers, data=payload_str)
    data = response.json()

    products = []
    for item in data.get("SearchResult", {}).get("Items", []):
        try:
            title = item["ItemInfo"]["Title"]["DisplayValue"]
            image = item["Images"]["Primary"]["Small"]["URL"]
            price = item["Offers"]["Listings"][0]["Price"]["Amount"]
            link = item["DetailPageURL"]
            cap_guess = next((int(word.replace("GB", "")) for word in title.split() if "GB" in word), None)
            ram_type = "DDR5" if "DDR5" in title else "DDR4"
            form = "SO-DIMM" if "sodimm" in title.lower() else "DIMM"
            condition = "New"
            products.append({
                "title": title, "image": image, "price": price, "link": link,
                "capacity_gb": cap_guess, "type": ram_type, "form_factor": form,
                "condition": condition, "price_per_gb": round(price / cap_guess, 2) if cap_guess else None
            })
        except:
            continue

    with open(cache_path, 'w') as f:
        json.dump(products, f)

    return products
