#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from urllib.parse import quote

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Script for parsing Xray configuration (VLESS) and generating a link vless://'
    )
    parser.add_argument(
        '--config', '-c', 
        type=str, 
        help='A path to your Xray (VLESS) config.json', 
        default='/usr/local/etc/xray/config.json'
    )
    return parser.parse_args()

def load_config(config_path: str) -> dict:
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_file, 'r', encoding='utf-8') as file:
        return json.load(file)

def generate_vless_uri(config: dict) -> str:
    try:
        encryption = "none"
        address = ""
        uuid = ""
        port = ""
        security = "none"
        network = "none"
        sni = "none"
        sid = "none"
        flow = "none"
        header_type = "none"
        fingerprint = "none"
        public_key = "none"
        
        if "outbounds" in config and config["outbounds"]:
            outbound = config["outbounds"][0]
            settings = outbound.get("settings", {})
            vnext = settings.get("vnext", [{}])[0]
            user = vnext.get("users", [{}])[0]
            
            uuid = user.get("id", "")
            address = vnext.get("address", "")
            port = vnext.get("port", "")
            
            security = outbound.get("streamSettings", {}).get("security", "none")
            network = outbound.get("streamSettings", {}).get("network", "none")
            reality_settings = outbound.get("streamSettings", {}).get("realitySettings", {})
            sni = reality_settings.get("serverName", "none")
            sid = reality_settings.get("shortId", "none")
            flow = user.get("flow", "none")
            fingerprint = reality_settings.get("fingerprint", "none")
            public_key = reality_settings.get("publicKey", "")
            while not public_key or public_key == 'none':
                public_key = input("Input your Public Key (can't be empty): ").strip()
            header_type = user.get("headerType", "none")
            encryption = user.get("encryption", "none")
        
        if "inbounds" in config and config["inbounds"] and not address:
            inbound = config["inbounds"][0]
            user = inbound["settings"].get("clients", [{}])[0]
            uuid = user.get("id", "")
            port = inbound.get("port", "")
            security = inbound.get("streamSettings", {}).get("security", "none")
            network = inbound.get("streamSettings", {}).get("network", "none")
            reality_settings = inbound.get("streamSettings", {}).get("realitySettings", {})
            sni = reality_settings.get("serverNames", [""])[0]
            sid = reality_settings.get("shortIds", [""])[0]
            flow = user.get("flow", "none")
            fingerprint = "firefox"
            
            if inbound["settings"].get("decryption", "none") == "none":
                encryption = "none"
            
            while not address or address == 'none':
                address = input("Input the server address (can't be empty): ").strip()
            while not public_key or public_key == 'none':
                public_key = input("Input your Public Key (can't be empty): ").strip()
        
        if not address:
            raise ValueError("Incorrect structure of the Xray configuration file: missing address")
        
        alias = "Xray_Server"
        
        params = [
            f"security={security}",
            f"encryption={encryption}",
            f"headerType={header_type}",
            f"fp={fingerprint}",
            f"type={network}",
            f"flow={flow}",
            f"pbk={public_key}",
            f"sni={sni}",
            f"sid={sid}"
        ]
        
        param_str = "&".join(params)
        return f"vless://{uuid}@{address}:{port}?{param_str}#{quote(alias)}"
    except (KeyError, IndexError):
        raise ValueError("Incorrect structure of the Xray configuration file")

def main():
    args = parse_arguments()
    config = load_config(args.config)
    try:
        vless_uri = generate_vless_uri(config)
        print(vless_uri)
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
