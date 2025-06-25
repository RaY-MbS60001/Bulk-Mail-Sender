import sys
import os
import requests
from sqlalchemy import create_engine
from redis import Redis

def check_database():
    try:
        engine = create_engine(os.getenv('DATABASE_URL'))
        connection = engine.connect()
        connection.close()
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print("✗ Database connection failed:", str(e))
        return False

def check_redis():
    try:
        redis = Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379))
        )
        redis.ping()
        print("✓ Redis connection successful")
        return True
    except Exception as e:
        print("✗ Redis connection failed:", str(e))
        return False

def check_email():
    try:
        import smtplib
        server = smtplib.SMTP(
            os.getenv('MAIL_SERVER'),
            int(os.getenv('MAIL_PORT'))
        )
        server.starttls()
        server.login(
            os.getenv('MAIL_USERNAME'),
            os.getenv('MAIL_PASSWORD')
        )
        server.quit()
        print("✓ Email configuration successful")
        return True
    except Exception as e:
        print("✗ Email configuration failed:", str(e))
        return False

def main():
    print("Running deployment checks...")
    checks = [
        check_database(),
        check_redis(),
        check_email()
    ]
    
    if all(checks):
        print("\nAll checks passed!")
        sys.exit(0)
    else:
        print("\nSome checks failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()