import pytest
from unittest.mock import MagicMock


@pytest.fixture
def wiki_page1():
    """Page 1 — Burj Khalifa full, Palm Jumeirah empty."""
    mock = MagicMock()
    mock.ok = True
    mock.status_code = 200
    mock.json.return_value = {
        "continue": {"excontinue": 1, "continue": "||"},
        "query": {
            "pages": {
                "794957": {
                    "pageid": 794957,
                    "title": "Burj Khalifa",
                    "extract": "The Burj Khalifa is a skyscraper in Dubai."
                },
                "3162976": {
                    "pageid": 3162976,
                    "title": "Palm Jumeirah",
                    "extract": ""
                }
            }
        }
    }
    return mock


@pytest.fixture
def wiki_page2():
    """Page 2 — Burj Khalifa empty, Palm Jumeirah full."""
    mock = MagicMock()
    mock.ok = True
    mock.status_code = 200
    mock.json.return_value = {
        "batchcomplete": "",
        "query": {
            "pages": {
                "794957": {
                    "pageid": 794957,
                    "title": "Burj Khalifa",
                    "extract": ""
                },
                "3162976": {
                    "pageid": 3162976,
                    "title": "Palm Jumeirah",
                    "extract": "The Palm Jumeirah is an artificial island."
                }
            }
        }
    }
    return mock

@pytest.fixture
def parsed_page_json():
    return {
        "status": 200,
        "data": {
            "query": {
                "pages": {
                    "794957": {
                        "pageid": 794957,
                        "title": "Burj Khalifa",
                        "extract": "The Burj Khalifa is a skyscraper in Dubai."
                    }
                }
            }
        }
    }

@pytest.fixture
def empty_extract_page_json():
    return {
        "status": 200,
        "data": {
            "query": {
                "pages": {
                    "794957": {
                        "pageid": 794957,
                        "title": "Burj Khalifa",
                        "extract": ""
                    }
                }
            }
        }
    }

@pytest.fixture
def missing_pages_json():
    return {
        "status": 200,
        "data": {"query": {}}
    }

@pytest.fixture
def parsed_articles():
    return [{
        "page_id": 794957,
        "title": "Burj Khalifa",
        "summary": """The Burj Khalifa (previously known as Burj Dubai prior to inauguration) is a megatall skyscraper in Dubai, United Arab Emirates. Designed by Skidmore, Owings & Merrill, it is the world's tallest structure, with a total height of 829.8 m (2,722 ft, or just over half a mile) and a roof height (excluding the antenna, but including a 242.6 m spire) of 828 m (2,717 ft). It has also been the tallest building in the world since its topping out in 2009, surpassing Taipei 101, which had held the record for a half-decade.
            Construction of the Burj Khalifa began in 2004; the exterior was completed five years later. The primary structure is reinforced concrete. Some of the structural steel for the building was salvaged from the demolished Palace of the Republic in East Berlin. The building was opened in 2010 as part of a new development called Downtown Dubai. It was designed to be the centrepiece of large-scale, mixed-use development.
            The building is named after the former president of the United Arab Emirates (UAE), Sheikh Khalifa bin Zayed Al Nahyan. The United Arab Emirates government provided Dubai with financial support as the developer, Emaar Properties, experienced financial problems during the Great Recession. Then-president of the United Arab Emirates, Khalifa bin Zayed, organised federal financial support. For his support, Mohammad bin Rashid, Ruler of Dubai, changed the name from "Burj Dubai" to "Burj Khalifa" during inauguration.
            The design is derived from the Islamic architecture of the region, such as in the Great Mosque of Samarra. The Y-shaped tripartite floor geometry is designed to optimise residential and hotel space. A buttressed central core and wings are used to support the height of the building. The Burj Khalifa's central core houses all vertical transportation except egress stairs within each of the wings. The structure also features a cladding system which is designed to withstand Dubai's hot summer temperatures. It contains a total of 57 elevators and 8 escalators.

            == Development ==
            Construction began on 12 January 2004, with the exterior of the structure completed on 1 October 2009. The building officially opened on 4 January 2010 and is part of the 2 km2 (490 acres) Downtown Dubai development at the 'First Interchange' along Sheikh Zayed Road, near Dubai's main business district.
            The tower's architecture and engineering were performed by Skidmore, Owings & Merrill of Chicago, with Adrian Smith as chief architect, and Bill Baker as a chief structural engineer. The firm had designed the Sears Tower in Chicago, a previous record holder for the world's tallest building.
            Hyder Consulting was supervising engineer and NORR Group Consultants supervised the architecture. The primary contractor was Samsung C&T of South Korea, together with the Belgian group BESIX and the local company Arabtec.
            Numerous complaints concerned migrant workers from South Asia, the primary building labour force, who were paid low wages and sometimes had their passports confiscated.""",
        "source": "wikipedia"
    }]

@pytest.fixture
def retrieved_chunks():
    return [
        {
            "title": "Burj Khalifa",
            "text": "The Burj Khalifa is a skyscraper in Dubai.",
            "page_id": 794957,
            "score": 0.95
        }
    ]