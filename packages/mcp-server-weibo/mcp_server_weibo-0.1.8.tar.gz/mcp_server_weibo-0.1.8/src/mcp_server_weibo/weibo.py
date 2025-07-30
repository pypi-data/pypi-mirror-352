import httpx
import re
import logging
from urllib.parse import urlencode
from .consts import DEFAULT_HEADERS, PROFILE_URL, FEEDS_URL, HOT_SEARCH_URL, SEARCH_CONTENT_URL
from .schemas import PagedFeeds, SearchResult, HotSearchItem

class WeiboCrawler:
    """
    A crawler class for extracting data from Weibo (Chinese social media platform).
    Provides functionality to fetch user profiles, feeds, and search for users.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def extract_weibo_profile(self, uid: int) -> dict:
        """
        Extract user profile information from Weibo.
        
        Args:
            uid (int): The unique identifier of the Weibo user
            
        Returns:
            dict: User profile information or empty dict if extraction fails
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(PROFILE_URL.format(userId=uid), headers=DEFAULT_HEADERS)
                result = response.json()
                return result["data"]["userInfo"]
            except httpx.HTTPError:
                self.logger.error(f"Unable to eextract profile for uid '{str(uid)}'", exc_info=True)
                return {}

    async def extract_weibo_feeds(self, uid: int, limit: int = 15) -> list[dict]:
        """
        Extract user's Weibo feeds (posts) with pagination support.
        
        Args:
            uid (int): The unique identifier of the Weibo user
            limit (int): Maximum number of feeds to extract, defaults to 15
            
        Returns:
            list: List of user's Weibo feeds
        """
        feeds = []
        sinceId = ''
        async with httpx.AsyncClient() as client:
            containerId = await self._get_container_id(client, uid)

            while len(feeds) < limit:
                pagedFeeds = await self._extract_feeds(client, uid, containerId, sinceId)
                if not pagedFeeds.Feeds:
                    break

                feeds.extend(pagedFeeds.Feeds)
                sinceId = pagedFeeds.SinceId
                if not sinceId:
                    break
                
        return feeds

    async def search_weibo_users(self, keyword: str, limit: int = 5) -> list[SearchResult]:
        """
        Search for Weibo users based on a keyword.
        
        Args:
            keyword (str): Search term to find users
            limit (int): Maximum number of users to return, defaults to 5
            
        Returns:
            list: List of SearchResult objects containing user information
        """
        async with httpx.AsyncClient() as client:
            try:
                params = {'containerid': f'100103type=3&q={keyword}&t=', 'page_type': 'searchall'}
                encoded_params = urlencode(params)

                response = await client.get(f'https://m.weibo.cn/api/container/getIndex?{encoded_params}', headers=DEFAULT_HEADERS)
                result = response.json()
                cards = result["data"]["cards"]
                if len(cards) < 2:
                    return []
                else:
                    cardGroup = cards[1]['card_group']
                    return [self._to_search_result(item['user']) for item in cardGroup][:limit]
            except httpx.HTTPError:
                self.logger.error(f"Unable to search users for keyword '{keyword}'", exc_info=True)
                return []

    async def get_host_search_list(self, limit: int = 15) -> list[HotSearchItem]:
        """
        Get a list of hot search items from Weibo.

        Args:
            limit (int): Maximum number of hot search items to return, defaults to 15

        Returns:
            list: List of HotSearchItem objects containing hot search information
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(HOT_SEARCH_URL, headers=DEFAULT_HEADERS)
                data = response.json()
                cards = data.get('data', {}).get('cards', [])
                if not cards:
                    return []

                hot_search_card = None
                for card in cards:
                    if 'card_group' in card and isinstance(card['card_group'], list):
                        hot_search_card = card
                        break

                if not hot_search_card or 'card_group' not in hot_search_card:
                    return []

                hot_search_items = []
                id = 1
                for item in hot_search_card['card_group']:
                    if item.get('desc') and id <= limit:
                        extr_values = re.findall(r'\d+', str(item.get('desc_extr')))
                        trending = int(extr_values[0]) if extr_values else 0
                        hot_search_item = HotSearchItem(
                            description=item['desc'],
                            id=id,
                            trending=trending,
                            url=item.get('scheme', '')
                        )
                        hot_search_items.append(hot_search_item)
                        id += 1
                return hot_search_items
        except httpx.HTTPError:
            self.logger.error('Unable to fetch Weibo hot search list', exc_info=True)
            return []

    async def search_weibo_content(self, keyword: str, limit: int = 15, page: int = 1) -> list[dict]:
        """
        Search Weibo content (posts) by keyword.

        Args:
            keyword (str): The search keyword
            limit (int): Maximum number of content results to return, defaults to 15
            page (int, optional): The starting page number, defaults to 1

        Returns:
            list: List of dictionaries containing content search results
        """
        results = []
        current_page = page
        try:
            while len(results) < limit:
                url = SEARCH_CONTENT_URL.format(keyword=keyword, page=current_page)
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, headers=DEFAULT_HEADERS)
                    data = response.json()
                cards = data.get('data', {}).get('cards', [])
                content_cards = []
                for card in cards:
                    if card.get('card_type') == 9:
                        content_cards.append(card)
                    elif 'card_group' in card and isinstance(card['card_group'], list):
                        content_group = [item for item in card['card_group'] if item.get('card_type') == 9]
                        content_cards.extend(content_group)
                if not content_cards:
                    break
                for card in content_cards:
                    if len(results) >= limit:
                        break
                    mblog = card.get('mblog')
                    if not mblog:
                        continue
                    pics = [pic['url'] for pic in mblog.get('pics', []) if 'url' in pic] if mblog.get('pics') else []
                    video_url = None
                    page_info = mblog.get('page_info')
                    if page_info and page_info.get('type') == 'video':
                        video_url = (
                            page_info.get('media_info', {}).get('stream_url') or
                            page_info.get('urls', {}).get('mp4_720p_mp4') or
                            page_info.get('urls', {}).get('mp4_hd_mp4') or
                            page_info.get('urls', {}).get('mp4_ld_mp4')
                        )
                    user = mblog.get('user', {})
                    content_result = {
                        'id': mblog.get('id'),
                        'text': mblog.get('text'),
                        'created_at': mblog.get('created_at'),
                        'reposts_count': mblog.get('reposts_count'),
                        'comments_count': mblog.get('comments_count'),
                        'attitudes_count': mblog.get('attitudes_count'),
                        'user': {
                            'id': user.get('id'),
                            'screen_name': user.get('screen_name'),
                            'profile_image_url': user.get('profile_image_url'),
                            'verified': user.get('verified'),
                        },
                        'pics': pics if pics else None,
                        'video_url': video_url
                    }
                    results.append(content_result)
                current_page += 1
                cardlist_info = data.get('data', {}).get('cardlistInfo', {})
                if not cardlist_info.get('page') or str(cardlist_info.get('page')) == '1':
                    break
            return results[:limit]
        except httpx.HTTPError:
            self.logger.error(f"Unable to search Weibo content for keyword '{keyword}'", exc_info=True)
            return []

    def _to_search_result(self, user: dict) -> SearchResult:
        """
        Convert raw user data to SearchResult object.
        
        Args:
            user (dict): Raw user data from Weibo API
            
        Returns:
            SearchResult: Formatted user information
        """
        return SearchResult(
            id=user['id'], 
            nickName=user['screen_name'], 
            avatarHD=user['avatar_hd'],
            description=user['description']
        )
        
    async def _get_container_id(self, client, uid: int):
        """
        Get the container ID for a user's Weibo feed.
        
        Args:
            client (httpx.AsyncClient): HTTP client instance
            uid (int): The unique identifier of the Weibo user
            
        Returns:
            str: Container ID for the user's feed or None if extraction fails
        """
        try:
            response = await client.get(PROFILE_URL.format(userId=str(uid)), headers=DEFAULT_HEADERS)
            data = response.json()
            tabs_info = data.get("data", {}).get("tabsInfo", {}).get("tabs", [])
            for tab in tabs_info:
                if tab.get("tabKey") == "weibo":
                    return tab.get("containerid")
        except httpx.HTTPError:
            self.logger.error(f"Unable to extract containerId for uid '{str(uid)}'", exc_info=True)
            return None

    async def _extract_feeds(self, client, uid: int, container_id: str, since_id: str):
        """
        Extract a single page of Weibo feeds for a user.
        
        Args:
            client (httpx.AsyncClient): HTTP client instance
            uid (int): The unique identifier of the Weibo user
            container_id (str): Container ID for the user's feed
            since_id (str): ID of the last feed for pagination
            
        Returns:
            PagedFeeds: Object containing feeds and next page's since_id
        """
        try:
            url = FEEDS_URL.format(userId=str(uid), containerId=container_id, sinceId=since_id)
            response = await client.get(url, headers = DEFAULT_HEADERS)
            data = response.json()

            new_since_id = data.get("data", {}).get("cardlistInfo", {}).get("since_id", "")
            cards = data.get("data", {}).get("cards", [])
            mblogs = cards
            
            if mblogs:
                return PagedFeeds(SinceId=new_since_id, Feeds=mblogs)
            else:
                return PagedFeeds(SinceId=new_since_id, Feeds=[])
        except httpx.HTTPError:
            self.logger.error(f"Unable to extract feeds for uid '{str(uid)}'", exc_info=True)
            return PagedFeeds(SinceId=None, Feeds=[])