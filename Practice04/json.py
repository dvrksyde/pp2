import json

FILE = "sample-data.json"


def load_interfaces(path):
    with open(path) as f:
        data = json.load(f)
    return data["imdata"]


def print_table(rows):
    print("Interface Status")
    print("=" * 50)

    header = f"{'DN':<55} {'Description':<15} {'Speed':<8} {'MTU':<6}"
    print(header)
    print("-" * len(header))

    for r in rows:
        attr = r["l1PhysIf"]["attributes"]
        dn = attr.get("dn", "")
        descr = attr.get("descr", "")
        speed = attr.get("speed", "")
        mtu = attr.get("mtu", "")
        print(f"{dn:<55} {descr:<15} {speed:<8} {mtu:<6}")


if __name__ == "__main__":
    interfaces = load_interfaces(FILE)
    print_table(interfaces)
