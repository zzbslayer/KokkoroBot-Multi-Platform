from kokkoro.web import get_app

quart = get_app()
quart.run(host='0.0.0.0', port=5001, debug=True)