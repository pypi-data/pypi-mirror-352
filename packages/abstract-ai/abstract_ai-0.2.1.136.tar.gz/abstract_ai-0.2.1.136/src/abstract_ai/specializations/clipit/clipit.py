# clipit.py
import sys,os
  # Assumed
def initialize_clipit(choice="display"):
    # Default to GUI if a display is available; otherwise start Flask
    if choice == "display":
        from src.gui_frontend  import gui_main
        gui_main()
    elif choice == "client":
        from src.client import client_main
        client_main()
    elif choice == "script":
        
        read_file_as_text()  # Note: This function requires a file path argument
    elif choice == "flask":
        port = port or 7823
        import wsgi
        url = f"http://localhost:{port}/drop-n-copy.html"
        wsgi.app.run(debug=True,port=port)  # Adjust based on your Flask setup

