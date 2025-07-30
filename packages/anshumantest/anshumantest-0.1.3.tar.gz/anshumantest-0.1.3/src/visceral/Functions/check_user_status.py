
def check_user_status(user_id):
    """Check user status from API and cache the result"""
    try:
        import requests
        response = requests.get(f"https://visceralos.com/check-pre/user/{user_id}")
        if response.status_code == 200:
            use_ami=False
            use_dyn=False
            use_gen=False
            data = response.json()
            if data.get("check",False):
                use_ami=True
            elif data.get("check2",False):
                use_dyn=True
            else:
                use_gen=True
            
            payload={
                "use_ami":use_ami,
                "use_dyn":use_dyn,
                "use_gen":use_gen
            }

            return payload
        
    except Exception as e:
        print(f"Error checking user status: {str(e)}")
    return False