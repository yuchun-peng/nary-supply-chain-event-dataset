EVENT_SPECS = {
    "Competition": {
        "definition": (
            "An explicit competitive relationship, competitor identity, "
            "competitive comparison, competitive pressure, or competitive "
            "advantage or disadvantage between identifiable market participants, "
            "products, technologies, or offerings."
        ),
        "boundary": (
            "Generic leadership, market position, market presence, customer "
            "relationships, supplier relationships, or industry participation "
            "alone are not Competition. An explicit competitive relationship "
            "or comparison must be present."
        ),
        "examples": (
            'Positive: "We face competition from Chinese manufacturers." '
            "-> Competition\n"
            'Positive: "Our technology provides advantages over competing '
            'battery systems." -> Competition\n'
            'Negative: "We are a global leader in automotive seating." '
            "-> NON_TARGET\n"
            'Negative: "We maintain relationships with major OEM customers." '
            "-> NON_TARGET"
        ),
        "roles": (
            "time",
            "competitor_status",
            "market",
            "product",
            "competition_area",
            "location",
            "competitor_count",
        ),
    },

    "Manufacturing": {
        "definition": (
            "Physical manufacturing, assembly, fabrication, processing, "
            "refining, milling, smelting, transformation, or other activities "
            "that physically produce or transform goods or components."
        ),
        "boundary": (
            "General facility existence, capacity, ownership, or business "
            "description alone is not Manufacturing unless an actual "
            "manufacturing or production activity is described. "
            "Selling, supplying, delivering, or distributing finished goods "
            "does not by itself constitute Manufacturing."
        ),
        "examples": (
            'Positive: "We manufacture battery packs in Germany." '
            "-> Manufacturing\n"
            'Positive: "Rivian vehicles are built in the United States." '
            "-> Manufacturing\n"
            'Negative: "This is a full-scale EV manufacturing facility." '
            "-> NON_TARGET\n"
            'Negative: "We design and engineer driveline technologies." '
            "-> NON_TARGET"
        ),
        "roles": (
            "location",
            "time",
            "resulting_product",
            "process",
            "application",
            "recipient",
            "facility",
            "market",
            "manufacturer",
        ),
    },

    "Supply": {
        "definition": (
            "Physical goods, components, materials, or products are supplied, "
            "delivered, shipped, distributed, or otherwise provided to a "
            "customer or recipient."
        ),
        "boundary": (
            "Selling alone, service provision, customer relationships, and "
            "generic supply-chain discussion are not Supply unless the source "
            "describes the provision or delivery of physical goods. "
            "Physical building, manufacturing, assembling, or producing goods "
            "belongs to Manufacturing rather than Supply."
        ),
        "examples": (
            'Positive: "We supply complete seat systems to automotive '
            'manufacturers." -> Supply\n'
            'Positive: "We deliver battery components to OEM customers." '
            "-> Supply\n"
            'Negative: "Vehicles are sold directly to consumers." '
            "-> NON_TARGET\n"
            'Negative: "We maintain relationships with major customers." '
            "-> NON_TARGET"
        ),
        "roles": (
            "customer",
            "recipient",
            "location",
            "time",
            "application",
        ),
    },

    "Investment": {
        "definition": (
            "An explicit commitment, allocation, deployment, or expenditure "
            "of financial, physical, technological, or other organizational "
            "resources into a company, facility, technology, project, "
            "production capability, geographic operation, or other identifiable "
            "investment target."
        ),
        "boundary": (
            "Existing ownership, facilities, operations, assets, capabilities, "
            "or financial metrics alone are not Investment. The source must "
            "describe an explicit resource commitment, allocation, deployment, "
            "expenditure, or stated plan to invest."
        ),
        "examples": (
            'Positive: "We made significant investments in our plants across '
            'North America." -> Investment\n'
            'Positive: "We plan to invest $500 million in a new battery '
            'facility." -> Investment\n'
            'Negative: "We operate manufacturing plants across North America." '
            "-> NON_TARGET\n"
            'Negative: "The company owns several production facilities." '
            "-> NON_TARGET"
        ),
        "roles": (
            "amount",
            "currency",
            "location",
            "purpose",
            "time",
            "investment_type",
            "asset_type",
        ),
    },
}
