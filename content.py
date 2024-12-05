'''Input/Label info used for generating New Hike form markup
'''
form_content = {
    'date': {
        'name': 'hike_date',
        'label': 'Hike date',
        'inputType': 'date',
        'required': True
    },
    'area': {
        'name': 'area_name',
        'label': 'Area',
        'inputType': 'text',
        'required': True
    },
    'trailhead': {
        'name': 'trailhead',
        'label': 'Trailhead',
        'inputType': 'text',
        'required': True

    },
    'trails': {
        'name': 'trails_cs',
        'label': 'Trails (comma-separated)',
        'inputType': 'text',
        'required': True
    },
    'distance': {
        'name': 'distance_km',
        'label': 'Distance (KM)',
        'inputType': 'number',
        'required': True
    },
    'image_url': {
        'name': 'image_url',
        'label': 'Image URL',
        'inputType': 'text',
        'reuqired': False
    },
    'image_alt': {
        'name': 'image_alt',
        'label': 'Image description',
        'inputType': 'text',
        'reuqired': False
    },
    'map': {
        'name': 'map_link',
        'label': 'Map link',
        'inputType': 'text',
        'required': False
    },
    'description': {
        'name': 'other_info',
        'label': 'Description',
        'inputType': 'text',
        'required': False
    }
}
