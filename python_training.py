


events = [
    {"event_id": "a", "user_id": 1, "ts": 100, "value": 10},
    {"event_id": "b", "user_id": 2, "ts": 105, "value": 20},
    {"event_id": "a", "user_id": 1, "ts": 110, "value": 15},
    {"event_id": "c", "user_id": 1, "ts": 108, "value": 5},
    {"event_id": "b", "user_id": 2, "ts": 103, "value": 99},
]

def deduplicate(events):
    latest = {}
    
    for event in events:
        event_id = event['event_id']

        if event_id not in latest: 
            latest[event_id] = event 

        elif event['ts'] >= latest[event_id]['ts']:
            latest[event_id] = event

    return sorted(
        latest.values(),
        key=lambda event: (event['ts'], event['event_id'])
        )  
print(deduplicate(events))           
