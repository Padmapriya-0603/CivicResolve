"""
Greater Chennai Corporation (GCC) Municipal Zones and Wards Taxonomy.
15 Administrative Zones and 200 Municipal Wards.
"""

from typing import List, Dict, Any, Optional

CHENNAI_ZONES: List[Dict[str, Any]] = [
    {
        "id": "ZONE_01",
        "zone_number": 1,
        "name": "Zone 1 - Thiruvottiyur",
        "wards": [
            {"ward_number": 1, "id": "Ward 1", "name": "Ward 1 - Wimco Nagar / Ennore"},
            {"ward_number": 2, "id": "Ward 2", "name": "Ward 2 - Kathivakkam North"},
            {"ward_number": 3, "id": "Ward 3", "name": "Ward 3 - Kathivakkam South"},
            {"ward_number": 4, "id": "Ward 4", "name": "Ward 4 - Ernavoor"},
            {"ward_number": 5, "id": "Ward 5", "name": "Ward 5 - Thiruvottiyur North"},
            {"ward_number": 6, "id": "Ward 6", "name": "Ward 6 - Thiruvottiyur Market"},
            {"ward_number": 7, "id": "Ward 7", "name": "Ward 7 - Theradi"},
            {"ward_number": 8, "id": "Ward 8", "name": "Ward 8 - Mattankuppam"},
            {"ward_number": 9, "id": "Ward 9", "name": "Ward 9 - Kaladipet"},
            {"ward_number": 10, "id": "Ward 10", "name": "Ward 10 - Rajakadai"},
            {"ward_number": 11, "id": "Ward 11", "name": "Ward 11 - Sathangadu"},
            {"ward_number": 12, "id": "Ward 12", "name": "Ward 12 - Tollgate"},
            {"ward_number": 13, "id": "Ward 13", "name": "Ward 13 - Thangal"},
            {"ward_number": 14, "id": "Ward 14", "name": "Ward 14 - Tondiarpet High Road"},
        ]
    },
    {
        "id": "ZONE_02",
        "zone_number": 2,
        "name": "Zone 2 - Manali",
        "wards": [
            {"ward_number": 15, "id": "Ward 15", "name": "Ward 15 - Edayanchavadi"},
            {"ward_number": 16, "id": "Ward 16", "name": "Ward 16 - Sadayankuppam"},
            {"ward_number": 17, "id": "Ward 17", "name": "Ward 17 - Kadapakkam"},
            {"ward_number": 18, "id": "Ward 18", "name": "Ward 18 - Manali New Town"},
            {"ward_number": 19, "id": "Ward 19", "name": "Ward 19 - Mathur MMDA"},
            {"ward_number": 20, "id": "Ward 20", "name": "Ward 20 - Chinnasekkadu"},
            {"ward_number": 21, "id": "Ward 21", "name": "Ward 21 - Manali Town"},
        ]
    },
    {
        "id": "ZONE_03",
        "zone_number": 3,
        "name": "Zone 3 - Madhavaram",
        "wards": [
            {"ward_number": 22, "id": "Ward 22", "name": "Ward 22 - Vadaperumbakkam"},
            {"ward_number": 23, "id": "Ward 23", "name": "Ward 23 - Puzhal"},
            {"ward_number": 24, "id": "Ward 24", "name": "Ward 24 - Surapet"},
            {"ward_number": 25, "id": "Ward 25", "name": "Ward 25 - Shanmugapuram"},
            {"ward_number": 26, "id": "Ward 26", "name": "Ward 26 - Puthagaram"},
            {"ward_number": 27, "id": "Ward 27", "name": "Ward 27 - Kathirvedu"},
            {"ward_number": 28, "id": "Ward 28", "name": "Ward 28 - Madhavaram Milk Colony"},
            {"ward_number": 29, "id": "Ward 29", "name": "Ward 29 - Madhavaram West"},
            {"ward_number": 30, "id": "Ward 30", "name": "Ward 30 - Madhavaram Central"},
            {"ward_number": 31, "id": "Ward 31", "name": "Ward 31 - Kodungaiyur West"},
            {"ward_number": 32, "id": "Ward 32", "name": "Ward 32 - Kodungaiyur Central"},
            {"ward_number": 33, "id": "Ward 33", "name": "Ward 33 - Kodungaiyur East"},
        ]
    },
    {
        "id": "ZONE_04",
        "zone_number": 4,
        "name": "Zone 4 - Tondiarpet",
        "wards": [
            {"ward_number": 34, "id": "Ward 34", "name": "Ward 34 - Korukkupet North"},
            {"ward_number": 35, "id": "Ward 35", "name": "Ward 35 - Korukkupet South"},
            {"ward_number": 36, "id": "Ward 36", "name": "Ward 36 - Dr. Radhakrishnan Nagar"},
            {"ward_number": 37, "id": "Ward 37", "name": "Ward 37 - Tondiarpet West"},
            {"ward_number": 38, "id": "Ward 38", "name": "Ward 38 - Tondiarpet Central"},
            {"ward_number": 39, "id": "Ward 39", "name": "Ward 39 - Seniamman Koil"},
            {"ward_number": 40, "id": "Ward 40", "name": "Ward 40 - Old Washermanpet North"},
            {"ward_number": 41, "id": "Ward 41", "name": "Ward 41 - Old Washermanpet Central"},
            {"ward_number": 42, "id": "Ward 42", "name": "Ward 42 - Meenambal Nagar"},
            {"ward_number": 43, "id": "Ward 43", "name": "Ward 43 - Muthizhpet"},
            {"ward_number": 44, "id": "Ward 44", "name": "Ward 44 - Kasimedu Harbour"},
            {"ward_number": 45, "id": "Ward 45", "name": "Ward 45 - Royapuram Fishing Harbour"},
            {"ward_number": 46, "id": "Ward 46", "name": "Ward 46 - Stanley Hospital Area"},
            {"ward_number": 47, "id": "Ward 47", "name": "Ward 47 - Sanjeevirayanpet"},
            {"ward_number": 48, "id": "Ward 48", "name": "Ward 48 - Bojaraja Nagar"},
        ]
    },
    {
        "id": "ZONE_05",
        "zone_number": 5,
        "name": "Zone 5 - Royapuram",
        "wards": [
            {"ward_number": 49, "id": "Ward 49", "name": "Ward 49 - Singaravelar Nagar"},
            {"ward_number": 50, "id": "Ward 50", "name": "Ward 50 - Cemetery Road"},
            {"ward_number": 51, "id": "Ward 51", "name": "Ward 51 - Grace Garden"},
            {"ward_number": 52, "id": "Ward 52", "name": "Ward 52 - Royapuram Market"},
            {"ward_number": 53, "id": "Ward 53", "name": "Ward 53 - Kalmandapam"},
            {"ward_number": 54, "id": "Ward 54", "name": "Ward 54 - Seven Wells North"},
            {"ward_number": 55, "id": "Ward 55", "name": "Ward 55 - Seven Wells South"},
            {"ward_number": 56, "id": "Ward 56", "name": "Ward 56 - George Town North"},
            {"ward_number": 57, "id": "Ward 57", "name": "Ward 57 - Sowcarpet"},
            {"ward_number": 58, "id": "Ward 58", "name": "Ward 58 - Kothawal Chavadi"},
            {"ward_number": 59, "id": "Ward 59", "name": "Ward 59 - Park Town / Central"},
            {"ward_number": 60, "id": "Ward 60", "name": "Ward 60 - Harbour / Broadway"},
            {"ward_number": 61, "id": "Ward 61", "name": "Ward 61 - Elephant Gate"},
            {"ward_number": 62, "id": "Ward 62", "name": "Ward 62 - Kondithope"},
            {"ward_number": 63, "id": "Ward 63", "name": "Ward 63 - Periamet"},
        ]
    },
    {
        "id": "ZONE_06",
        "zone_number": 6,
        "name": "Zone 6 - Thiru-Vi-Ka Nagar",
        "wards": [
            {"ward_number": 64, "id": "Ward 64", "name": "Ward 64 - Kolathur West"},
            {"ward_number": 65, "id": "Ward 65", "name": "Ward 65 - Kolathur Central"},
            {"ward_number": 66, "id": "Ward 66", "name": "Ward 66 - Kolathur East"},
            {"ward_number": 67, "id": "Ward 67", "name": "Ward 67 - Peravallur"},
            {"ward_number": 68, "id": "Ward 68", "name": "Ward 68 - Sembium North"},
            {"ward_number": 69, "id": "Ward 69", "name": "Ward 69 - Sembium South"},
            {"ward_number": 70, "id": "Ward 70", "name": "Ward 70 - Thiru-Vi-Ka Nagar East"},
            {"ward_number": 71, "id": "Ward 71", "name": "Ward 71 - Thiru-Vi-Ka Nagar West"},
            {"ward_number": 72, "id": "Ward 72", "name": "Ward 72 - Jawahar Nagar"},
            {"ward_number": 73, "id": "Ward 73", "name": "Ward 73 - Agaram"},
            {"ward_number": 74, "id": "Ward 74", "name": "Ward 74 - Perambur Loco Works"},
            {"ward_number": 75, "id": "Ward 75", "name": "Ward 75 - Perambur Carriage Works"},
            {"ward_number": 76, "id": "Ward 76", "name": "Ward 76 - Ayanavaram North"},
            {"ward_number": 77, "id": "Ward 77", "name": "Ward 77 - Ayanavaram South"},
            {"ward_number": 78, "id": "Ward 78", "name": "Ward 78 - Otteri"},
        ]
    },
    {
        "id": "ZONE_07",
        "zone_number": 7,
        "name": "Zone 7 - Ambattur",
        "wards": [
            {"ward_number": 79, "id": "Ward 79", "name": "Ward 79 - Padi Pudur"},
            {"ward_number": 80, "id": "Ward 80", "name": "Ward 80 - Korattur North"},
            {"ward_number": 81, "id": "Ward 81", "name": "Ward 81 - Korattur Central"},
            {"ward_number": 82, "id": "Ward 82", "name": "Ward 82 - Mannurpet"},
            {"ward_number": 83, "id": "Ward 83", "name": "Ward 83 - Padi Saravana Nagar"},
            {"ward_number": 84, "id": "Ward 84", "name": "Ward 84 - Ambattur Industrial Estate"},
            {"ward_number": 85, "id": "Ward 85", "name": "Ward 85 - Ambattur Old Town"},
            {"ward_number": 86, "id": "Ward 86", "name": "Ward 86 - Venkatapuram"},
            {"ward_number": 87, "id": "Ward 87", "name": "Ward 87 - Ramapuram Ambattur"},
            {"ward_number": 88, "id": "Ward 88", "name": "Ward 88 - Menambedu"},
            {"ward_number": 89, "id": "Ward 89", "name": "Ward 89 - Mogappair East"},
            {"ward_number": 90, "id": "Ward 90", "name": "Ward 90 - Mogappair West"},
            {"ward_number": 91, "id": "Ward 91", "name": "Ward 91 - Nolambur"},
            {"ward_number": 92, "id": "Ward 92", "name": "Ward 92 - Ambattur OT East"},
            {"ward_number": 93, "id": "Ward 93", "name": "Ward 93 - Ayapakkam Border"},
        ]
    },
    {
        "id": "ZONE_08",
        "zone_number": 8,
        "name": "Zone 8 - Anna Nagar",
        "wards": [
            {"ward_number": 94, "id": "Ward 94", "name": "Ward 94 - Villivakkam North"},
            {"ward_number": 95, "id": "Ward 95", "name": "Ward 95 - Villivakkam South"},
            {"ward_number": 96, "id": "Ward 96", "name": "Ward 96 - SIDCO Nagar"},
            {"ward_number": 97, "id": "Ward 97", "name": "Ward 97 - Agathiyar Nagar"},
            {"ward_number": 98, "id": "Ward 98", "name": "Ward 98 - Anna Nagar West Extension"},
            {"ward_number": 99, "id": "Ward 99", "name": "Ward 99 - Shenoy Nagar / Pulla Ave"},
            {"ward_number": 100, "id": "Ward 100", "name": "Ward 100 - Anna Nagar West"},
            {"ward_number": 101, "id": "Ward 101", "name": "Ward 101 - Anna Nagar East"},
            {"ward_number": 102, "id": "Ward 102", "name": "Ward 102 - Anna Nagar Central / Tower"},
            {"ward_number": 103, "id": "Ward 103", "name": "Ward 103 - Naduvankarai"},
            {"ward_number": 104, "id": "Ward 104", "name": "Ward 104 - Aminjikarai North"},
            {"ward_number": 105, "id": "Ward 105", "name": "Ward 105 - Shenoy Nagar East"},
            {"ward_number": 106, "id": "Ward 106", "name": "Ward 106 - Arumbakkam North"},
            {"ward_number": 107, "id": "Ward 107", "name": "Ward 107 - Arumbakkam Metro"},
            {"ward_number": 108, "id": "Ward 108", "name": "Ward 108 - Kilpauk Garden"},
        ]
    },
    {
        "id": "ZONE_09",
        "zone_number": 9,
        "name": "Zone 9 - Teynampet",
        "wards": [
            {"ward_number": 109, "id": "Ward 109", "name": "Ward 109 - Choolaimedu North"},
            {"ward_number": 110, "id": "Ward 110", "name": "Ward 110 - Nungambakkam High Road"},
            {"ward_number": 111, "id": "Ward 111", "name": "Ward 111 - College Road"},
            {"ward_number": 112, "id": "Ward 112", "name": "Ward 112 - Thousand Lights North"},
            {"ward_number": 113, "id": "Ward 113", "name": "Ward 113 - Thousand Lights West"},
            {"ward_number": 114, "id": "Ward 114", "name": "Ward 114 - Triplicane North"},
            {"ward_number": 115, "id": "Ward 115", "name": "Ward 115 - Chepauk / Marina"},
            {"ward_number": 116, "id": "Ward 116", "name": "Ward 116 - Triplicane South"},
            {"ward_number": 117, "id": "Ward 117", "name": "Ward 117 - Royapettah North"},
            {"ward_number": 118, "id": "Ward 118", "name": "Ward 118 - Royapettah South"},
            {"ward_number": 119, "id": "Ward 119", "name": "Ward 119 - T. Nagar North"},
            {"ward_number": 120, "id": "Ward 120", "name": "Ward 120 - T. Nagar / Panagal Park"},
            {"ward_number": 121, "id": "Ward 121", "name": "Ward 121 - Pondy Bazaar"},
            {"ward_number": 122, "id": "Ward 122", "name": "Ward 122 - Alwarpet North"},
            {"ward_number": 123, "id": "Ward 123", "name": "Ward 123 - Alwarpet South"},
            {"ward_number": 124, "id": "Ward 124", "name": "Ward 124 - Mylapore / Kapaleeshwarar"},
            {"ward_number": 125, "id": "Ward 125", "name": "Ward 125 - Santhome Beach"},
            {"ward_number": 126, "id": "Ward 126", "name": "Ward 126 - Mandaveli"},
        ]
    },
    {
        "id": "ZONE_10",
        "zone_number": 10,
        "name": "Zone 10 - Kodambakkam",
        "wards": [
            {"ward_number": 127, "id": "Ward 127", "name": "Ward 127 - Vadapalani North"},
            {"ward_number": 128, "id": "Ward 128", "name": "Ward 128 - Saligramam"},
            {"ward_number": 129, "id": "Ward 129", "name": "Ward 129 - Virugambakkam North"},
            {"ward_number": 130, "id": "Ward 130", "name": "Ward 130 - Virugambakkam South"},
            {"ward_number": 131, "id": "Ward 131", "name": "Ward 131 - Vadapalani Temple"},
            {"ward_number": 132, "id": "Ward 132", "name": "Ward 132 - Kodambakkam North"},
            {"ward_number": 133, "id": "Ward 133", "name": "Ward 133 - Kodambakkam Station"},
            {"ward_number": 134, "id": "Ward 134", "name": "Ward 134 - Ashok Nagar North"},
            {"ward_number": 135, "id": "Ward 135", "name": "Ward 135 - Ashok Pillar"},
            {"ward_number": 136, "id": "Ward 136", "name": "Ward 136 - West Mambalam North"},
            {"ward_number": 137, "id": "Ward 137", "name": "Ward 137 - West Mambalam South"},
            {"ward_number": 138, "id": "Ward 138", "name": "Ward 138 - Saidapet West"},
            {"ward_number": 139, "id": "Ward 139", "name": "Ward 139 - Saidapet Bazar"},
            {"ward_number": 140, "id": "Ward 140", "name": "Ward 140 - CIT Nagar"},
            {"ward_number": 141, "id": "Ward 141", "name": "Ward 141 - Saidapet South"},
            {"ward_number": 142, "id": "Ward 142", "name": "Ward 142 - Jafferkhanpet"},
        ]
    },
    {
        "id": "ZONE_11",
        "zone_number": 11,
        "name": "Zone 11 - Valasaravakkam",
        "wards": [
            {"ward_number": 143, "id": "Ward 143", "name": "Ward 143 - Nerkundram North"},
            {"ward_number": 144, "id": "Ward 144", "name": "Ward 144 - Nerkundram South"},
            {"ward_number": 145, "id": "Ward 145", "name": "Ward 145 - Chinmaya Nagar"},
            {"ward_number": 146, "id": "Ward 146", "name": "Ward 146 - Koyambedu Market"},
            {"ward_number": 147, "id": "Ward 147", "name": "Ward 147 - Valasaravakkam North"},
            {"ward_number": 148, "id": "Ward 148", "name": "Ward 148 - Valasaravakkam South"},
            {"ward_number": 149, "id": "Ward 149", "name": "Ward 149 - Karambakkam"},
            {"ward_number": 150, "id": "Ward 150", "name": "Ward 150 - Porur Garden"},
            {"ward_number": 151, "id": "Ward 151", "name": "Ward 151 - Porur Lake Area"},
            {"ward_number": 152, "id": "Ward 152", "name": "Ward 152 - Porur Junction"},
            {"ward_number": 153, "id": "Ward 153", "name": "Ward 153 - Ramapuram North"},
            {"ward_number": 154, "id": "Ward 154", "name": "Ward 154 - Ramapuram South"},
            {"ward_number": 155, "id": "Ward 155", "name": "Ward 155 - Rayala Nagar"},
        ]
    },
    {
        "id": "ZONE_12",
        "zone_number": 12,
        "name": "Zone 12 - Alandur",
        "wards": [
            {"ward_number": 156, "id": "Ward 156", "name": "Ward 156 - Mugalivakkam"},
            {"ward_number": 157, "id": "Ward 157", "name": "Ward 157 - Manapakkam"},
            {"ward_number": 158, "id": "Ward 158", "name": "Ward 158 - Nandambakkam"},
            {"ward_number": 159, "id": "Ward 159", "name": "Ward 159 - St. Thomas Mount"},
            {"ward_number": 160, "id": "Ward 160", "name": "Ward 160 - Alandur Metro"},
            {"ward_number": 161, "id": "Ward 161", "name": "Ward 161 - Alandur Court"},
            {"ward_number": 162, "id": "Ward 162", "name": "Ward 162 - Pazhavanthangal"},
            {"ward_number": 163, "id": "Ward 163", "name": "Ward 163 - Nanganallur North"},
            {"ward_number": 164, "id": "Ward 164", "name": "Ward 164 - Nanganallur Temple"},
            {"ward_number": 165, "id": "Ward 165", "name": "Ward 165 - Nanganallur South"},
            {"ward_number": 166, "id": "Ward 166", "name": "Ward 166 - Adambakkam"},
            {"ward_number": 167, "id": "Ward 167", "name": "Ward 167 - Meenambakkam Airport Area"},
        ]
    },
    {
        "id": "ZONE_13",
        "zone_number": 13,
        "name": "Zone 13 - Adyar",
        "wards": [
            {"ward_number": 168, "id": "Ward 168", "name": "Ward 168 - Guindy Industrial Estate"},
            {"ward_number": 169, "id": "Ward 169", "name": "Ward 169 - Guindy Race Course"},
            {"ward_number": 170, "id": "Ward 170", "name": "Ward 170 - Gandhi Nagar"},
            {"ward_number": 171, "id": "Ward 171", "name": "Ward 171 - Kotturpuram"},
            {"ward_number": 172, "id": "Ward 172", "name": "Ward 172 - Adyar Bridge Road"},
            {"ward_number": 173, "id": "Ward 173", "name": "Ward 173 - Adyar / Shastri Nagar"},
            {"ward_number": 174, "id": "Ward 174", "name": "Ward 174 - Kasturba Nagar"},
            {"ward_number": 175, "id": "Ward 175", "name": "Ward 175 - Indira Nagar"},
            {"ward_number": 176, "id": "Ward 176", "name": "Ward 176 - Besant Nagar Beach"},
            {"ward_number": 177, "id": "Ward 177", "name": "Ward 177 - Kalakshetra Colony"},
            {"ward_number": 178, "id": "Ward 178", "name": "Ward 178 - Thiruvanmiyur North"},
            {"ward_number": 179, "id": "Ward 179", "name": "Ward 179 - Thiruvanmiyur Beach"},
            {"ward_number": 180, "id": "Ward 180", "name": "Ward 180 - Velachery West"},
        ]
    },
    {
        "id": "ZONE_14",
        "zone_number": 14,
        "name": "Zone 14 - Perungudi",
        "wards": [
            {"ward_number": 181, "id": "Ward 181", "name": "Ward 181 - Velachery East"},
            {"ward_number": 182, "id": "Ward 182", "name": "Ward 182 - Puzhuthivakkam"},
            {"ward_number": 183, "id": "Ward 183", "name": "Ward 183 - Madipakkam North"},
            {"ward_number": 184, "id": "Ward 184", "name": "Ward 184 - Madipakkam Koot Road"},
            {"ward_number": 185, "id": "Ward 185", "name": "Ward 185 - Pallikaranai Marsh"},
            {"ward_number": 186, "id": "Ward 186", "name": "Ward 186 - Perungudi OMR IT Corridor"},
            {"ward_number": 187, "id": "Ward 187", "name": "Ward 187 - Perungudi Industrial"},
            {"ward_number": 188, "id": "Ward 188", "name": "Ward 188 - Kottivakkam ECR"},
            {"ward_number": 189, "id": "Ward 189", "name": "Ward 189 - Palavakkam North"},
            {"ward_number": 190, "id": "Ward 190", "name": "Ward 190 - Palavakkam South"},
            {"ward_number": 191, "id": "Ward 191", "name": "Ward 191 - Neelankarai North"},
        ]
    },
    {
        "id": "ZONE_15",
        "zone_number": 15,
        "name": "Zone 15 - Sholinganallur",
        "wards": [
            {"ward_number": 192, "id": "Ward 192", "name": "Ward 192 - Neelankarai South"},
            {"ward_number": 193, "id": "Ward 193", "name": "Ward 193 - Okkiyam Thoraipakkam"},
            {"ward_number": 194, "id": "Ward 194", "name": "Ward 194 - Injambakkam"},
            {"ward_number": 195, "id": "Ward 195", "name": "Ward 195 - Akkarai ECR"},
            {"ward_number": 196, "id": "Ward 196", "name": "Ward 196 - Karapakkam IT Park"},
            {"ward_number": 197, "id": "Ward 197", "name": "Ward 197 - Sholinganallur Junction"},
            {"ward_number": 198, "id": "Ward 198", "name": "Ward 198 - Uthandi Beach"},
            {"ward_number": 199, "id": "Ward 199", "name": "Ward 199 - Semmancheri"},
            {"ward_number": 200, "id": "Ward 200", "name": "Ward 200 - Navalur Border"},
        ]
    }
]


def get_all_zones() -> List[Dict[str, Any]]:
    """Returns all 15 Greater Chennai Corporation Zones with their Wards."""
    return CHENNAI_ZONES


def get_zone_by_name_or_id(zone_identifier: str) -> Optional[Dict[str, Any]]:
    """Finds a zone by ID, name, or partial match."""
    identifier_clean = zone_identifier.strip().lower()
    for z in CHENNAI_ZONES:
        if z["id"].lower() == identifier_clean or z["name"].lower() == identifier_clean:
            return z
        if identifier_clean in z["name"].lower():
            return z
    return None


def get_wards_for_zone(zone_identifier: str) -> List[Dict[str, Any]]:
    """Returns list of wards for the given zone."""
    zone = get_zone_by_name_or_id(zone_identifier)
    return zone["wards"] if zone else []
