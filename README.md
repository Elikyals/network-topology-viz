# lldp-topology-mapper

A Python-based network automation tool that discovers and visualizes physical network topology on Juniper routers using LLDP (Link Layer Discovery Protocol). The tool connects to a starting router, recursively traverses the network via LLDP neighbor data, and generates a Graphviz diagram showing how all routers are interconnected.

This was built and tested on Juniper vSRX routers as part of a graduate-level network automation course project (ENTS749E).

---

## What It Does

Starting from a single management IP, the tool:

1. Connects to the router via PyEZ
2. Collects LLDP neighbor information from all active interfaces
3. Recursively visits each discovered neighbor until the full topology is mapped
4. Renders a directed graph using Graphviz with router hostnames, management IPs, and interface labels on each edge

Two topologies were tested: a 6-router topology and a 5-router topology.

---

## Project Goals

- Automate the discovery of physical network connections without manual cable tracing or documentation
- Use LLDP as the single source of truth for neighbor relationships
- Produce a clean, readable visual output that accurately reflects the physical topology
- Keep the codebase modular so it can be adapted to different topologies with minimal changes

---

## Repository Structure

```
lldp-topology-mapper/
├── router_conf.py          # Configures interface IPs on all routers (Topology B - 5 routers)
├── routers.py              # Device list with interface IP config for Topology A (6 routers)
├── template.conf           # Jinja2 template for interface IP address assignment
├── enable_llpd.py          # Enables LLDP on all routers via PyEZ
├── enable_llpd_temp.conf   # Jinja2 template for LLDP configuration
├── get_lldp_info.py        # Main script: discovers topology and renders the Graphviz diagram
└── README.md
```

---

## Prerequisites

- Python 3.x
- Juniper PyEZ (`junos-eznc`)
- Graphviz Python library (`graphviz`)
- Graphviz system binary (for rendering)
- Juniper routers with NETCONF enabled and reachable management IPs
- `lxml`

Install Python dependencies:

```bash
pip install junos-eznc graphviz lxml
```

Install the Graphviz system binary:

```bash
# Fedora / RHEL
sudo dnf install graphviz

# Debian / Ubuntu
sudo apt install graphviz
```

---

## Usage

### Step 1: Configure Interface IPs

Update the `devices` list in `router_conf.py` (5-router topology) or `routers.py` (6-router topology) with your router management IPs and interface-to-IP mappings. Then run:

```bash
python router_conf.py
```

This pushes the interface configurations to each router using the `template.conf` Jinja2 template.

### Step 2: Enable LLDP

Update the `devices` list in `enable_llpd.py` with your router names and management IPs, then run:

```bash
python enable_llpd.py
```

The script checks each router's current LLDP status and enables it if disabled, using `enable_llpd_temp.conf` as the configuration template.

### Step 3: Discover and Visualize the Topology

In `get_lldp_info.py`, update the `management_ips` list with the starting router's management IP:

```python
management_ips = ['192.168.1.36']
```

Then run:

```bash
python get_lldp_info.py
```

The script recursively walks the topology and renders a `network_topology.gv.pdf` file. It will also open the diagram automatically.

---

## How the Discovery Works

The script maintains two lists: `management_ips` (a queue of routers to visit) and `seen_routers` (already-visited routers). Starting from the seed IP:

1. It calls `get_lldp_local_info` to get the router's system name and management IP.
2. It calls `get_lldp_neighbors_information` to list all neighboring interfaces.
3. For each interface connected to another router, it calls `get_lldp_interface_neighbors_information` to get the specific neighbor details.
4. Each discovered neighbor's management IP is appended to `management_ips` if not already seen.
5. The loop continues until all reachable routers have been visited.

The collected link data is passed to `draw_graph()`, which builds the Graphviz `Digraph` object, deduplicates nodes and edges, and renders the final diagram.

---

## Topology Reference

**Topology A (6 routers)** - managed by `routers.py`

| Router | Management IP | Loopback |
|--------|--------------|----------|
| Router A | 192.168.1.35 | 72.114.96.36/32 |
| Router B | 192.168.1.36 | 72.114.96.37/32 |
| Router C | 192.168.1.37 | 72.114.96.38/32 |
| Router D | 192.168.1.38 | 72.114.96.39/32 |
| Router E | 192.168.1.39 | 72.114.96.40/32 |
| Router F | 192.168.1.13 | 72.114.96.41/32 |

**Topology B (5 routers)** - managed by `router_conf.py`

| Router | Management IP | Loopback |
|--------|--------------|----------|
| Router 1 | 192.168.1.35 | 72.114.96.36/32 |
| Router 2 | 192.168.1.36 | 72.114.96.37/32 |
| Router 3 | 192.168.1.37 | 72.114.96.38/32 |
| Router 4 | 192.168.1.38 | 72.114.96.39/32 |
| Router 5 | 192.168.1.39 | 72.114.96.40/32 |

---

## Challenges

**Junos version differences in RPC behavior**

The biggest challenge was inconsistency in how LLDP RPCs behave across Junos versions. On newer versions, `get-lldp-neighbor-detail-information` returns complete neighbor data in a single call. On older versions, that RPC either does not exist or returns incomplete data, requiring a two-step process: first calling `get-lldp-neighbors-information` to identify connected interfaces, then calling `get-lldp-interface-neighbors-information` per interface to get the actual neighbor details.

This meant the codebase had to be designed around the older RPC pattern to work consistently across the test environment. Even minor version differences (e.g., 11.4R3.0 vs 12.2R2.0) could cause the script to fail silently or return partial data.

**Ensuring all routers ran consistent Junos versions**

Because the discovery logic is tightly coupled to RPC response structure, the test environment required all vSRX instances to run the same Junos version. This is straightforward in a homelab but is a real constraint in production or heterogeneous environments.

---

## Known Limitations

- The neighbor filtering logic in `get_lldp_info.py` uses a string match on `"router"` in the remote system name. This works for the test topology but will miss neighbors whose hostnames do not contain that substring.
- Credentials are hardcoded (`labuser` / `Labuser`). For any real deployment, these should be moved to environment variables or a secrets manager.
- The `management_ips` seed list is hardcoded at the top of `get_lldp_info.py`. There is no CLI argument support yet.
- The output is always a directed graph (`Digraph`). Bidirectional edges are deduplicated by sorting the node pair, but the arrowhead direction may look inconsistent depending on which router was visited first.

---

## Future Work

- Add version detection to automatically select the correct RPC path based on the connected device's Junos version
- Replace hardcoded credentials with environment variable or config file support
- Add CLI argument support for the seed IP and output file path
- Extend neighbor filtering to support arbitrary hostname patterns or device types
- Add support for exporting topology data to JSON or YAML for use in other tools

---

## References

- [Juniper Networks - Device Discovery Using LLDP](https://www.juniper.net/documentation/us/en/software/junos/user-access/topics/topic-map/device-discovery-using-lldp-lldp-med.html)
- [Juniper PyEZ Documentation](https://junos-pyez.readthedocs.io/en/stable/)
- [Graphviz Python Library](https://graphviz.readthedocs.io/en/stable/)
