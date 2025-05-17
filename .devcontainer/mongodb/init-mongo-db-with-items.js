db.items.insert([
    {
        tag_uuid: "123e4567-e89b-12d3-a456-426614174000",
        short_name: "Hammer",
        amount: 10,
        item_type: "tool",
        consumable: false,
        created_at: "2023-10-01T12:00:00Z",
        created_by: "user1",
        changes: [
            {
                user: "user2",
                timestamp: 1672531200,
                diff_from_prev_version: {
                    cost_new: 20.0,
                    vendors: ["Vendor1"],
                }
            },
            {
                user: "user1",
                timestamp: 1672551200,
                diff_from_prev_version: {
                    amount: 5,
                    description: "some tool, not sure"
                }
            },
        ],
        ai_generated: ["tag1", "tag2"],
        description: "A heavy-duty hammer",
        min_amount: 2,
        tags: ["hardware", "tool"],
        images: [
            'data:image/jpeg;base64,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'
        ],
        cost_new: 25.0,
        acquisition_date: 1672531200,
        cost_used: 15.0,
        manufacturer: "ToolCorp",
        model_number: "TC-HAMMER-01",
        manufacturing_date: 1672531200,
        upc: "123456789012",
        asin: "B000123456",
        serial_number: "SN1234567890",
        vendors: ["Vendor1", "Vendor2"],
        shop_url: ["http://shop1.com", "http://shop2.com"],
        size: { length: 300, width: 100, height: 50 },
        documentation: ["http://docs.toolcorp.com/hammer"],
        container_tag_uuid: "123e4567-e89b-12d3-a456-426614174003",
        current_location: "Warehouse A",
        borrowed_by: "user4",
        borrowed_at: 1672800000,
        borrowed_until: 1675401600,
        owner: "user1",
        related_items: [
            {
                related_tags: ["123e4567-e89b-12d3-a456-426614174001"],
                tag: ["tool"],
                description: "Related to Screwdriver Set"
            }
        ]
    },
    {
        tag_uuid: "123e4567-e89b-12d3-a456-426614174001",
        short_name: "Screwdriver Set",
        amount: 50,
        item_type: "tool",
        consumable: false,
        created_at: "2023-10-02T12:00:00Z",
        created_by: "user2",
        changes: [],
        ai_generated: [],
        description: "A set of precision screwdrivers",
        min_amount: 5,
        tags: ["hardware", "tool"],
        images: ["image3_id", "image4_id"],
        cost_new: 40.0,
        acquisition_date: 1672617600,
        cost_used: 25.0,
        manufacturer: "ToolCorp",
        model_number: "TC-SCREW-SET-01",
        manufacturing_date: 1672617600,
        upc: "123456789013",
        asin: "B000123457",
        serial_number: "SN1234567891",
        vendors: ["Vendor3", "Vendor4"],
        shop_url: ["http://shop3.com", "http://shop4.com"],
        size: { length: 200, width: 50, height: 50 },
        documentation: ["http://docs.toolcorp.com/screwdriver-set"],
        container_tag_uuid: null,
        current_location: "Warehouse B",
        borrowed_by: null,
        borrowed_at: null,
        borrowed_until: null,
        owner: "user2",
        related_items: [
            {
                related_tags: ["123e4567-e89b-12d3-a456-426614174000"],
                tag: ["tool"],
                description: "Related to Hammer"
            }
        ]
    },
    {
        tag_uuid: "123e4567-e89b-12d3-a456-426614174002",
        short_name: "Drill",
        amount: 20,
        item_type: "tool",
        consumable: false,
        created_at: "2023-10-03T12:00:00Z",
        created_by: "user3",
        changes: [
            {
                user: "user2",
                timestamp: 1672793002,
                diff_from_prev_version: {
                    borrowed_by: "user6",
                    borrowed_at: 1672793002,
                    borrowed_until: 1672853002,
                }
            },
            {
                user: "user6",
                timestamp: 1672855002,
                diff_from_prev_version: {
                    borrowed_by: "user6",
                    borrowed_at: null,
                    borrowed_until: null,
                }
            },
        ],
        ai_generated: ["tag4", "tag5"],
        description: "A cordless drill",
        min_amount: 3,
        tags: ["hardware", "tool"],
        images: ["image5_id", "image6_id"],
        cost_new: 100.0,
        acquisition_date: 1672704000,
        cost_used: 70.0,
        manufacturer: "ToolCorp",
        model_number: "TC-DRILL-01",
        manufacturing_date: 1672704000,
        upc: "123456789014",
        asin: "B000123458",
        serial_number: "SN1234567892",
        vendors: ["Vendor5", "Vendor6"],
        shop_url: ["http://shop5.com", "http://shop6.com"],
        size: { length: 250, width: 80, height: 70 },
        documentation: ["http://docs.toolcorp.com/drill"],
        container_tag_uuid: "123e4567-e89b-12d3-a456-426614174005",
        current_location: "Warehouse C",
        borrowed_by: "user6",
        borrowed_at: 1672800002,
        borrowed_until: 1675401602,
        owner: "user3",
        related_items: [
            {
                related_tags: ["123e4567-e89b-12d3-a456-426614174000"],
                tag: ["tool"],
                description: "Related to Hammer"
            }
        ]
    },
    {
        tag_uuid: "123e4567-e89b-12d3-a456-426614174003",
        short_name: "Eurobox 3",
        amount: 1,
        item_type: "eurobox",
        consumable: false,
        created_at: "2023-10-04T12:00:00Z",
        created_by: "user4",
        changes: [],
        ai_generated: [],
        description: "A large eurobox",
        min_amount: 1,
        tags: ["container", "eurobox"],
        images: ["image7_id", "image8_id"],
        cost_new: 50.0,
        acquisition_date: 1672793002,
        cost_used: 30.0,
        manufacturer: "EuroboxCorp",
        model_number: "EB-3",
        manufacturing_date: 1672793002,
        upc: "123456789015",
    }

])
db.readers.insert([
    { reader_id: "04-04-46-42-CD-66-81", reader_name: "Reader1" }, 
    { reader_id: "04-04-46-42-CD-66-82", reader_name: "Reader2" },
])
