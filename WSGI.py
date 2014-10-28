from main_site import app


def application(env, start_response):
    app.run()
