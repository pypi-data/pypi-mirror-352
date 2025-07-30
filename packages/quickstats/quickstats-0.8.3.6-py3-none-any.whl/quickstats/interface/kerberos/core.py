import os
import subprocess

import quickstats

__all__ = [
    "get_kerberos_ticket_cache",
    "kerberos_ticket_exists",
    "list_service_principals"
]

def get_kerberos_ticket_cache():
    krb_cache = os.getenv('KRB5CCNAME')
    if krb_cache:
        return krb_cache
    # Fallback to default path if KRB5CCNAME is not set
    uid = os.getuid()
    return f"/tmp/krb5cc_{uid}"

def kerberos_ticket_exists():
    ticket_cache = get_kerberos_ticket_cache()
    return os.path.exists(ticket_cache)

def list_service_principals():
    list_service_principals = []
    try:
        result = subprocess.run(['klist'], capture_output=True, text=True, check=True)
        lines = result.stdout.split('\n')
        for line in lines:
            if '@' not in line:
                continue
            tokens = line.split()
            if len(tokens) > 3 and '@' in tokens[-1]:
                list_service_principals.append(tokens[-1]) 
    except subprocess.CalledProcessError:
        quickstats.stdout.error("Failed to list tickets - are you sure Kerberos is configured correctly?")
    except FileNotFoundError:
        quickstats.stdout.error("Kerberos 'klist' command not found. Is Kerberos installed?")
    except Exception as e:
        quickstats.stdout.error(f"An unexpected error occurred: {e}")
    return list_service_principals