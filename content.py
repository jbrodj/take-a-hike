'''This module contains content information organized into dictionaries.
'''
# pylint: disable=line-too-long
hike_form_content = {
    'hike_date': {
        'name': 'hike_date',
        'label': 'Hike date',
        'inputType': 'date',
        'required': True
    },
    'area_name': {
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
    'trails_cs': {
        'name': 'trails_cs',
        'label': 'Trails (comma-separated)',
        'inputType': 'text',
        'required': True
    },
    'distance_km': {
        'name': 'distance_km',
        'label': 'Distance (KM)',
        'inputType': 'number',
        'required': True
    },
        'image_url': {
        'name': 'image_url',
        'label': 'Image',
        'inputType': 'file',
        'required': False
    },
    'image_alt': {
        'name': 'image_alt',
        'label': 'Image alt text',
        'inputType': 'text',
        'required': False
    },
    'other_info': {
        'name': 'other_info',
        'label': 'Description',
        'inputType': 'text',
        'required': False
    },
    'map_link': {
        'name': 'map_link',
        'label': 'Map link',
        'inputType': 'text',
        'required': False
    }
}


error_messages = {
    'incorrect_pw': 'Incorrect password. Please try again.',
    'invalid_number': 'Distance field must contain only numbers or decimal characters.',
    'missing_values': 'Required values are missing. Ensure all required values are provided.', 
    'no_username_or_pw': 'Username and password are required.',
    'password_invalid': 'Password with four to sixty-four characters is required.',
    'pw_confirm_match': 'Passwords must match.',
    'out_of_range': 'Distance must be between 0 and 100km.',
    'user_query_invalid': 'Usernames are between four and sixteen characters.',
    'unauthorized': 'You are not authorized to view this page.',
    'user_not_found': 'Username not found. Please check the username provided and try again.',
    'username_invalid': 'A username between four and sixteen characters containing only letters and/or numbers is required.',
    'username_taken': 'Username is already taken. Please select a different username.',
}
