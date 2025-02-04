from structure import app
from dotenv import load_dotenv
from flask_socketio import SocketIO
import os
socketio = SocketIO(app)

# if __name__ == '__main__':
#     load_dotenv()
#     socketio.run(app, debug=True)
    # app.run(debug=True)


if __name__ == '__main__':
    load_dotenv()
    # socketio.run(
    #     app,
    #     host='0.0.0.0',  # Allow external connections
    #     port=int(os.getenv('PORT', 5001)),  # Use PORT from .env or default to 5000
    #     debug=True
    # )

    socketio.run(
    app,
    host='0.0.0.0',  # Allow external access
    port=5001,        # Specify your port
    allow_unsafe_werkzeug=True
)