from src.news_mailer.service.auth.oauth import load_user_credentials

if __name__ == "__main__":
    creds = load_user_credentials()
    if creds:
        print(creds.refresh_token)
    else:
        print("Failed to load credentials")