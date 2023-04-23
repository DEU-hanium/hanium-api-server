def get_ipset_lock_token(client,ipset_name,ipset_id):
    """Returns the AWS WAF IP set lock token"""
    ip_set = client.get_ip_set(
        Name=ipset_name,
        Scope='REGIONAL',
        Id=ipset_id
    )
    
    return ip_set['LockToken']