import yaml

with open('../docs/eve_files/typeIDs.yaml', 'r', encoding='utf-8') as stream:
    try:
        data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

try:
    print(f"Type: {type(data)}")
except Exception:
    print("Unable to find Type.")

try:
    print(f"Length: {len(data)}")
except Exception:
    print("Unable to find Length.")

if 11317 in data:
    try:
        print(f"Object 11317: {data[11317]}")
    except Exception:
        print("Unable to find Object 11317.")

    try:
        print(f"Type of Object 11317: {type(data[11317])}")
    except Exception:
        print("Unable to find Type of Object 11317.")

    try:
        print(f"Length of Object 11317: {len(data[11317])}")
    except Exception:
        print("Unable to find Length of Object 11317.")

    try:
        print(f"Name of Object 11317: {data[11317]['name']['en']}")
    except Exception:
        print("Unable to find Name of Object 11317.")

    try:
        print(f"Type of Name of Object 11317: {type(data[11317]['name']['en'])}")
    except Exception:
        print("Unable to find Type of Name of Object 11317.")

    try:
        print(f"Length of Name of Object 11317: {len(data[11317]['name']['en'])}")
    except Exception:
        print("Unable to find Length of Name of Object 11317.")
else:
    print("Unable to find Object 11317.")
