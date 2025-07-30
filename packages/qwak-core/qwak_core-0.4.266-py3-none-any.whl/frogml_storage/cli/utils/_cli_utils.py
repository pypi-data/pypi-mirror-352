from typing import List


def get_list_of_servers_from_config(jfrog_cli_config: dict) -> List[str]:
    if jfrog_cli_config is not None:
        servers = jfrog_cli_config.get("servers")
        if servers is not None:
            return list(map(__map_server_ids, servers))

    return []


def __map_server_ids(server: dict) -> str:
    server_id = ""
    if server is not None:
        server_id = str(server.get("serverId"))
        if server.get("isDefault") is not None and bool(server.get("isDefault")):
            server_id = server_id + " (Default)"
    return server_id
