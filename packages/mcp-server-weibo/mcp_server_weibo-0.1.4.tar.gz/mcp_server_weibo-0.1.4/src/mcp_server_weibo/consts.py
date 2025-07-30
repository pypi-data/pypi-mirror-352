# Default HTTP headers for Weibo API requests
DEFAULT_HEADERS = { 'Content-Type': 'application/json' }

# URL template for fetching user profile information
# {userId} will be replaced with the actual user ID
PROFILE_URL = 'https://m.weibo.cn/api/container/getIndex?type=uid&value={userId}'

# URL template for fetching user's Weibo feeds
# {userId}: User's unique identifier
# {containerId}: Container ID for the user's feed
# {sinceId}: ID of the last feed for pagination
FEEDS_URL = 'https://m.weibo.cn/api/container/getIndex?type=uid&value={userId}&containerid={containerId}&since_id={sinceId}'

# URL for fetching the Weibo hot search list
HOT_SEARCH_URL = 'https://m.weibo.cn/api/container/getIndex?containerid=106003type%3D25%26t%3D3%26disable_hot%3D1%26filter_type%3Drealtimehot'

# URL template for searching Weibo content
# {keyword} will be replaced with the search keyword
# {page} will be replaced with the page number
SEARCH_CONTENT_URL = 'https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D1%26q%3D{keyword}&page_type=searchall&page={page}'