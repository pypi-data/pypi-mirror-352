# netcrypt/cli.py

import click
from .key_manager import generate_rsa_keypair, save_private_key, save_public_key
from .tunnel import start_secure_tunnel
import os

@click.group()
def cli():
    """NetCrypt: Secure network encryption and tunneling"""
    pass

@cli.command()
@click.option('--keyfile', default='aes.key', help='Path to AES key file')
@click.option('--generate', is_flag=True, help='Generate a new AES key')
def keygen(keyfile, generate):
    """Generate and save AES key"""
    if generate:
        key = os.urandom(32)  # 256-bit key
        with open(keyfile, 'wb') as f:
            f.write(key)
        click.echo(f"[+] AES key generated and saved to {keyfile}")
    else:
        click.echo("[!] Use --generate to create a key")

@cli.command()
@click.option('--mode', type=click.Choice(['server', 'client']), required=True, help='Tunnel mode')
@click.option('--keyfile', default='aes.key', help='AES key file path')
@click.option('--host', default='localhost', help='Host to bind/connect')
@click.option('--port', default=9000, help='Port number')
def tunnel(mode, keyfile, host, port):
    """Start encrypted tunnel as server/client"""
    with open(keyfile, 'rb') as f:
        key = f.read()
    start_secure_tunnel(mode, key, host, port)

@cli.command()
@click.option('--out-private', default='rsa_private.pem', help='Output file for private key')
@click.option('--out-public', default='rsa_public.pem', help='Output file for public key')
def rsagen(out_private, out_public):
    """Generate RSA key pair"""
    priv, pub = generate_rsa_keypair()
    save_private_key(priv, out_private)
    save_public_key(pub, out_public)
    click.echo(f"[+] RSA keys saved to {out_private} and {out_public}")

if __name__ == '__main__':
    cli()
