from .types import CriteriaTestCase

VISION_DATA: dict[str, CriteriaTestCase] = {
    "vision_llama": CriteriaTestCase(
        id="vision_llama",
        request_data={
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What is in this image? Keep your answer short.",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "https://upload.wikimedia.org/wikipedia/commons/f/f7/Llamas%2C_Vernagt-Stausee%2C_Italy.jpg"
                            },
                        },
                    ],
                }
            ]
        },
        criteria="vision",
        criteria_params={"expected_output": ["llama", "alpaca"]},
    ),
    "vision_two_images": CriteriaTestCase(
        id="vision_two_images",
        request_data={
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Does these two image both contain a sport activity? Answer yes or no",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "https://cdn.shopify.com/s/files/1/0040/5251/6910/files/06stg05_van-aert02_tdf_2022_1024x1024.jpg?"
                            },
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/40._Schwimmzonen-_und_Mastersmeeting_Enns_2017_100m_Brust_Herren_USC_Traun-9897.jpg/2560px-40._Schwimmzonen-_und_Mastersmeeting_Enns_2017_100m_Brust_Herren_USC_Traun-9897.jpg"
                            },
                        },
                    ],
                }
            ],
        },
        criteria="vision",
        criteria_params={"expected_output": ["yes"]},
    ),
}
