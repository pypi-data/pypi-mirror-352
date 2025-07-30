class FacebookConstants:

    HEDERS_BRAND = {
        'authority': 'graph.facebook.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        'content-type': 'application/x-www-form-urlencoded',
        'cookie': '{cookie}',
        'origin': 'https://developers.facebook.com',
        'referer': 'https://developers.facebook.com/',
        'sec-ch-ua': '"Chromium";v="100", " Not A;Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.162 Safari/537.36'
    }

    PROFILE_QUERY_FIELDS = 'id,name,username,phone,about,bio,followers_count,photos,location,' \
        'description,emails,link,website,picture.width(720).height(720),' \
        'videos{views,id,created_time},' \
        'posts{id,is_hidden,parent_id,via,updated_time,place,from,to,targeting,target,story,' \
        'full_picture,permalink_url,picture,status_type,message,shares,' \
        'reactions.limit(0).summary(true),comments.limit(0).summary(true),' \
        'attachments{description,description_tags,media, media_type, target, title, ' \
        'type,unshimmed_url, url},sharedposts.limit(0).summary(true),created_time}'
    
    MAX_BRAND_POST_RETRY = 5
    MAX_POST_BY_BRAND = 5000

    VARIABLES_KW = {"allow_streaming": False, "args": {"callsite": "COMET_GLOBAL_SEARCH",
                                                       "config": {"exact_match": False, "high_confidence_config": None,
                                                                  "intercept_config": None, "sts_disambiguation": None,
                                                                  "watch_config": None},
                                                       "context": {"bsid": "3fdce70f-7e0e-491f-a1ce-7c1810724ede",
                                                                   "tsid": "0.23133416141757124"}, "experience": {
            "client_defined_experiences": ["ADS_PARALLEL_FETCH"], "encoded_server_defined_params": None, "fbid": None,
            "type": "POSTS_TAB"}, "filters": [], "text": "philips sg"}, "count": 5,
                    "cursor": "Abo8MZvMBOv5T21eckWgDsJkcGKdodlri5n9OGNvQ6vbRjvTHx2XCJ8Y1cShX2iGDU2yWtR1ttye-KlqMe_XutVXjQNBxKnjStFmLPCOVkGRmdLJmnpTCNIjAEZHNvmNx06cthPqeth3jVMxl_mDnqwLhpKND0keUjTcsOXZ-rk_c7LimQ8U9BQt65GCBDbUACJdceoHKDPm7tLB32kUQLSwvtAjEIdsNdE0E6G9rYWKaAQ7bhmauj1OZbP9Ozo_k-VxKm0i0cflmWpS8rrDJsqFEJzcqGbhIOv0440mp8VjT9do0m-H0rsHlb-TLgWKl8LY0-FpXdzC1nEPgl4t2VPXKIOAG8Vmbf8NnPJvHBm1vt6Or5flFJE8ftbhbcNnrNYRoJfKEAx0_eShHfJrI-gHHPuffZGwquPaQGp2Yu4QrW6r3eHVBVwSyLfghZPgGDMhYCVOpbGyCBsiOswLCAo5qXybNKv3HT6a-GSCY36VDKLtbskVRNJ3u9-5yQ4r8yPpgQyzIti76S-tLxjtxe4YwqwopBQaTSPx804DEYlxgNT0iYERBo3L6K9osfSowQq95vtQU5XyRQaQC-1c5znvLeUdSov2HX20nkA-C2AuSolUv_33Bh4YoZX-vtz5KGbi2dZKH70S5dKcL0DvEPPLdwjbfAYmwo4HsuYL_ncApTa1qtzEDJqEjcR5_5C1zuntvZ8J3z21bEIAso9wJt7XqAlhH3gfUL5zC-2_R0a2BcK9z0Wc5dGuW79UcobNWv0RoGgFSERqsztYVF9e5_Tyhmi2X_D7uthn0HhCJiSwnAD5UEHYfHR2112imT6QRXpq2RinFVVUeKzH0puDu2Dfpigsrhx7od-kkopAAHOzdcmzrZwyB7dHW3jCJmLrzXszE61ftbE6JhCHRDB5uGYHrr8NDTXGeyM4BSxN4nC0ioVWMLIdXIald_2WO_rD-qvMdNkf-R560wcR8PDDeY9N6xNenB94Jh2ihloyC6_7VAVuRMrOv6wYQEBUna_0k5LR-sgGtUhl5kdRyzUXq5rbohdhJndf1lcNULPN3EE1hXNNYFtUWv5CgjU6UOvjI59Xnqlkr-U12MH_qUGYEpzPCnbC9i8hIJHtSsQY7B1MCsjrBhYcUH1JWZf3ksOFFCOwHnUetRjUrLe725TIjUfeJ2mMtrez1FMUiCXFBDGGffCu1RW3_o7EUQcM6XIKibVZDOG_XU3cXtS_T22tdMLZPF9C7JQfQs-gtuwtCl1EbG0QlzSWVxnw4FjMlZpYd_-W6DwSzDkFB6UNzvTmM3lMqwP-0XZv6OUufQfXwy22AXI84xBeyYq8-ORjGz5jewFoEsEd50q4BD3IlztjFTkVCV8hoJFCmfPxaKqQqM1piL4KRNz9SQUC2OOh5z_5VOiKnph532QGopl91gsURIhAePV7cFcJTWM9ednSEyIEMJWkffGHeESvoycoOUaUav_VOH-amslt4gUfugvqZQUlF1kOTmJ82ocUSgQtxzImy7JysOkNyCJafROpxwhUeW5Gpvhz8nMR184Fvv0vZkzQOCnwkTX65j79a-OzCCiElds0ENfIrBcgNVNK1i_1vIBheYNpsb_TNjt4WYFxYWt1OnN0cJLVlwWeYevT6TRp3yz3pkEw6s4FuPodmaePsZacLFbdEz8CRx_RVcFlOpb3bpap1FEiTy8z2PJA2-FwXC_LVdH0zYgI5WQ6KbyMDcDZeFPyhsLOVjYaGM9NqDIpj4a-JC_Yo9Txhi5jgGjGeAS3RM712IHShobapOUWJ67SDwdmp1pX544lUSwbHmpJ3XPdij-diwkjDdp3sIgC0m2p40lKthPq-MKjiMRyT7Iu1NDaMdY5zrwXKxs1GcAI-MGnuk6vPWWf_H0jCiRmWgC3WsgJ0PJWnHzXc_0ke6VcTHw69i1LOiYjrPFVlfJdCHoN1mTPBq_5lM34lJQbCG29DS9h3TzS7keJyVbHGNA0vbgwukRcAB6TLv4BbDvcvMoe2cxRHsiG2z3qxCD4OpQzCmuoEiq_IWL_q3H29mKeOQUtsUq2E0AjJmO2cUIJSpoq_EyO4-5irIJYK6yPeGfBJu2UgpMchBGuvTMKBCNvyuqaUoHZJE41i5H-kVU4jwUjmReLT1i1ckaY5B4Zm-zyBIPePrjEyNTMAyG7Z7tWpynDV8cRYmIrtPa4n60e4Jo67CXqXNgyVTWeRJGPwyOLU_5Eqo_WtnVfV_XvneRu9i96LYqLUqdCikNzBb_l7H3p46rdYd6uNGN3ug761EkV_Fg3La3meURK1xYUi6XSKxjtjwn8GGBsI1u74GfQ5H_wJgVhk2B9c5Z0wZmfaQeJQZj-KcCk_N9fgvqXyHqNdr2K2H6440WSi455hgf_ZwaazWr_Atzc5p4GEgq1jh6ES9eQMG9MM9soZRgzvZw",
                    "feedLocation": "SEARCH", "feedbackSource": 23, "fetch_filters": True, "focusCommentID": None,
                    "locale": None, "privacySelectorRenderLocation": "COMET_STREAM",
                    "renderLocation": "search_results_page", "scale": 1, "stream_initial_count": 0,
                    "useDefaultActor": False, "__relay_internal__pv__GHLShouldChangeAdIdFieldNamerelayprovider": False,
                    "__relay_internal__pv__GHLShouldChangeSponsoredDataFieldNamerelayprovider": False,
                    "__relay_internal__pv__IsWorkUserrelayprovider": False,
                    "__relay_internal__pv__CometFeedStoryDynamicResolutionPhotoAttachmentRenderer_experimentWidthrelayprovider": 500,
                    "__relay_internal__pv__CometImmersivePhotoCanUserDisable3DMotionrelayprovider": False,
                    "__relay_internal__pv__IsMergQAPollsrelayprovider": False,
                    "__relay_internal__pv__FBReelsMediaFooter_comet_enable_reels_ads_gkrelayprovider": False,
                    "__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider": False,
                    "__relay_internal__pv__CometUFIShareActionMigrationrelayprovider": True,
                    "__relay_internal__pv__StoriesArmadilloReplyEnabledrelayprovider": True,
                    "__relay_internal__pv__EventCometCardImage_prefetchEventImagerelayprovider": False}
    

    API_URL_COLLECT_HASHTAG = "https://www.facebook.com/api/graphql/"

    HEADERS_KW = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://www.facebook.com',
        'priority': 'u=1, i',
        'referer': 'https://www.facebook.com',
        'sec-ch-prefers-color-scheme': 'dark',
        'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        'sec-ch-ua-full-version-list': '"Not(A:Brand";v="99.0.0.0", "Google Chrome";v="133.0.6943.141", "Chromium";v="133.0.6943.141"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"Linux"',
        'sec-ch-ua-platform-version': '"5.13.0"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
        'x-asbd-id': '359341',
        'x-fb-friendly-name': 'SearchCometResultsPaginatedResultsQuery',
        'x-fb-lsd': 'KV23N0NmTCvuBWIDg4u0A7',
    }

    VARIABLES = {"feedLocation": "SEARCH", "feedbackSource": 40, "focusCommentID": None,
                 "input": {"extra_data": None, "scope_information": None,
                           "session_id": "40d11570-1f4d-41e8-8901-d3e87be63f23", "topic_id": "#philips",
                           "explore_tab": "TOP"}, "locale": None, "privacySelectorRenderLocation": "COMET_STREAM",
                 "renderLocation": "search_results_page", "scale": 2,
                 "topic_results_paginating_after_cursor": "{\"current_section\":12,\"serialized_section_cursor\":\"{\\\"serialized_browse_cursor\\\":\\\"AbpcjlyOPBSF1j2UxRP7DqwowvBQvSMoP7Vja2_JdClWiqKDdsXaI4ob7C-JbJpL3wAW7_83Uu4vOVkYRlyi-f8wvPxJ7yX9ygMw9CwyhkB5weL1Zw4KgTsdNDmzsGii6YkWs-Cy0PLMgGbfLbCnK4ElLQB-HZXtFEMLNyqe8S8JfRtaTUDnu9Jxk6wJpoSfFKh43yatwumF4h_DTG7DzdTCxY2aneJZdKmN_8Rs1GEy2gWm1NWchkhiEBrNfau3NyqwiQISGQOoErNpsWRa67IzPNTAC2EWQLE29GVKaOAtrFD86DMtG2RHCDbFFl2W6p9k8J0JtqYHflPouwP4WvRHkpJYs0FnByMG3n70vwcW3V0UhyLpenxT_kzAcMUa6xnDtKYMw3dPvWq2mirFB-92qTmHd1tKGN8QSw1JpnEPyf35Y-3oCQSkTa_1yvNJgUUuA5XufzPu1uM9NkhO8qWujLRYZMHLa_kDeY3pOvVzEl9usJ5UbZWo7-t13RbWIu4bg5LvSinn5BMIc7vXX3_tF1VW1a6ByQC9IWLXX23yAjMURpx_UwhvdKVa7SD991erkR8ZmMpJNtdBLvv3EXyS\\\",\\\"browse_unit_id\\\":\\\"browse_serp:5a925e45-af2b-43ab-bc5d-78ff5a9d3235\\\",\\\"top_n_fbids_shown_at_start_of_section\\\":[]}\",\"session_id\":\"40d11570-1f4d-41e8-8901-d3e87be63f23\",\"current_page_num\":1,\"section_to_num_results_shown\":{\"top_posts\":2},\"top_n_fbids_shown\":[3892274881005358,914379323793145],\"quick_promotion_fbids_shown\":[],\"ordered_sections\":[\"top_posts\"],\"reels_shown\":[],\"reels_fetched\":[]}",
                 "topic_results_paginating_at_stream_enabled": False,
                 "topic_results_paginating_at_stream_initial_count": 1, "topic_results_paginating_first": 5,
                 "useDefaultActor": False,
                 "__relay_internal__pv__CometImmersivePhotoCanUserDisable3DMotionrelayprovider": False,
                 "__relay_internal__pv__IsWorkUserrelayprovider": False,
                 "__relay_internal__pv__IsMergQAPollsrelayprovider": False,
                 "__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider": False,
                 "__relay_internal__pv__CometUFIShareActionMigrationrelayprovider": False,
                 "__relay_internal__pv__CometIsAdaptiveUFIEnabledrelayprovider": False,
                 "__relay_internal__pv__StoriesArmadilloReplyEnabledrelayprovider": False,
                 "__relay_internal__pv__StoriesRingrelayprovider": False,
                 "__relay_internal__pv__EventCometCardImage_prefetchEventImagerelayprovider": False}