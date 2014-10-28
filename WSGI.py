from main_site import app


def appliction(env, start_response):
    app.run()
