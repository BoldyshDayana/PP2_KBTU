import json

with open("c:/Users/HP OMEN/Desktop/pp2/practice4/json/sample-data.json", "r") as file:
    data = json.load(file)
    print("Interface Status")
    print("=" * 80)
    print(f"{'DN':<50} {'Description':<20} {'Speed':<7} {'MTU':<6}")
    print("-" * 50, "-" * 20, "-" * 7, "-" * 6)
    for item in data['imdata']:
        attributes = item['l1PhysIf']['attributes']
        dn = attributes.get('dn', '')
        desc = attributes.get('descr', '')
        speed = attributes.get('speed', '')
        mtu = attributes.get('mtu', '')
        print(f"{dn:<50} {desc:<20} {speed:<7} {mtu:<6}")
     