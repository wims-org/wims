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
        images: ["image1_id", "image2_id"],
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
