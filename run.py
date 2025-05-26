from app import create_app

if __name__ == "__main__":
    app = create_app()
    # Use debug=True for development; remove or set to False in production.
    # If you want to test HTTPS locally, uncomment the ssl_context line:
    #'app.run(debug=True, ssl_context="adhoc")
            #^https://stackoverflow.com/questions/29458548/can-you-add-https-functionality-to-a-python-flask-web-server
    app.run(debug=True)