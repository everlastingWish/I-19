import json

# make a python map from json file - "moodContext"
def json_to_map(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)

    # in data['moodContext'][0] 
    mood_ratings_dict = data.get('moodContext', [{}])[0]

    result_map = {}

    for rating_key, context_list in mood_ratings_dict.items():
        # rating_key is a string (char) of 1,2,3...etc
        
        # make sure the key is a digit and the value is a 1 str list
        if rating_key.isdigit() and isinstance(context_list, list) and context_list:
            rating_int = int(rating_key)
              
            # only item in the list... context is under the key 'context1'
            context_object = context_list[0]
            context_value = context_object.get('context1')
            
            # data to the map
            result_map[rating_int] = context_value.strip()
    
    return result_map
